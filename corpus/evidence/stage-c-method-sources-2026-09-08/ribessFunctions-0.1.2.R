#' Expand the input list to all possible risk group combinations
#' @param inputList list of risk factors that contain numeric vectors 
#' of e.g. relativeRisks per risk factor
#' @return vector that combines values of inputList for all possible
#' risk group combinations
#' @export
helpExpandRisks <- function(inputList) {
  
  expandRisks <- expand.grid(rev(inputList))
  outputVector <- apply(expandRisks, 1, prod)
  
  return(outputVector)
  
}

#' Expand the input list to all possible risk group combinations
#' @param inputList inputList list of risk factors that contain numeric vectors 
#' of e.g. relativeRisks per risk factor
#' @param toPaste boolean; TRUE (default) then return 1 pasted string per 
#' combination, FALSE then return a data frame with columns the risk factors
#' @return vector or data frame that combines names for all possible 
#' risk group combinations; a unique name per combination is given
#' @export
helpExpandNames <- function(inputList, toPaste = TRUE) {
  
  if( !toPaste ) {
    
    if( any(sapply(inputList, function(x) is.null(names(x)))) ) {
      
      getNames <- lapply( names(inputList), 
          function(x) letters[seq_along(inputList[[x]])]) 
      
    } else {
      
      getNames <- lapply( names(inputList), 
          function(x) names(inputList[[x]]))
      
    }
    
    names(getNames) <- names(inputList)
    expandNames <- expand.grid(rev(getNames), stringsAsFactors = FALSE)
    expandNames <- expandNames[,(dim(expandNames)[2]:1)]
    
  } else {
    
    if( any(sapply(inputList, function(x) is.null(names(x)))) ) {
      
      getNames <- lapply( names(inputList), 
          function(x) paste0(x, letters[seq_along(inputList[[x]])]) ) 
      
    } else {
      
      getNames <- lapply( names(inputList), 
          function(x) paste0(x, names(inputList[[x]])) )
      
    }
    
    expandNames <- expand.grid(rev(getNames), stringsAsFactors = FALSE)
    expandNames <- apply(expandNames, 1, function(x) paste0(x, collapse = "_"))
    
  }
  
  return(expandNames)
  
}


#' Expand the all input list elements to all possible risk group combinations
#' @param unexpanded named list of risk factors that contain numeric vectors 
#' of e.g. relativeRisks per risk factor
#' @return a dataframe with combined values for all possible risk group combinations
#' @export
expandRisks <- function(unexpanded){
  
  isRandom <- sapply(unexpanded, function(x) ifelse(is.null(attr(x, "random")),
            FALSE, attr(x, "random")))
  
  if( any(isRandom) ) {
    
    nRuns <- nrow(unexpanded[[ which(isRandom)[1] ]])
    output <- helpExpandRisks(inputList = lapply(unexpanded, '[', 1,))
    names(output) <- helpExpandNames(inputList = lapply(unexpanded, '[', 1,))
    
    for( iRun in 2:nRuns ) {
      
      output <- rbind(output,
          helpExpandRisks(inputList = lapply(unexpanded, '[', iRun,))) 
      
    }
    
    rownames(output) <- 1:nRuns
    attr(output, "random") <- TRUE
    
  } else {
    
    output <- helpExpandRisks(inputList = unexpanded)
    names(output) <- helpExpandNames(inputList = unexpanded)
    
  }
  
  return(output)
  
}



#' Calculate sample size and (group-specific) system sensitivity
#' @param sse system sensitivity; default value is NA. This value may be 
#'  missing when values for n are provided
#' @param n numeric vector for sample sizes; default value is NA.
#'  If numbers are provided, sample size is not calculated, only
#'  (group-specific) system sensitivity 
#' @param totalN total population size, default value is NA;
#'  non-NA value needed for hypergeometric sample size calculation
#' @param dp design prevalence, the survey will be designed in order to obtain at 
#' least a positive test result when the prevalence of the disease will be at 
#' or above the defined value of the design prevalence; default value is NA
#' @param tse test sensitivity, the probability that the test used will return a
#' positive result given that the sample is really positive
#' @param method method of sample size calculation; 
#' one of 'hyper' (default) or 'binom' 
#' @param isRiskbased logical Is the sampling risk based; 
#' default value is FALSE
#' @param relativeRisks a dataframe with relative risks for all possible 
#' risk group combinations; default value is NULL
#' @param proportionsRiskGroups a dataframe with relative proportions of 
#' total population for all possible risk group combinations; 
#' default value is NULL 
#' @param reportMaxGse boolean, whether the maximum sensitivity per risk group
#' should be reported; default is FALSE 
#' @return data frame reports for each risk group the population size,
#' sample size and group sensitivity; attribute ase is the global sensitivity;
#' if dp is missing the estimated value for dp is returned
#' @importFrom stats uniroot
#' @export
getSampleSizeGse <- function(sse = NA, n = NA, totalN = NA, dp = NA, tse, 
    method = c("hyper", "binom"), isRiskbased = FALSE,
    relativeRisks = NULL, proportionsRiskGroups = NULL, reportMaxGse = FALSE) {
  
  method <- match.arg(method)
  
  
  # Estimate dp
  if (is.na(dp)) {
    
    if (method == "binom") {
      
      dp <-  (1 - (1 - sse)^(1/n)) / tse
      
    } else {
      
      tseInfinite <- function(sse, n, totalN, tse, dp) {
        
        1 - sse - (1 - n*tse/(totalN - 0.5*(totalN*dp*tse - 1)))^(totalN*dp)
        
      }
      
      dp <- uniroot(tseInfinite, interval = c(0, 1), sse = sse, n = n, 
          totalN = totalN, tse = tse, tol = 1e-15)$root
      
    }
    
    
    return(data.frame(populationSize = totalN, sampleSize = n, gse = sse, dp = dp))
        
  }
  
  
  if (!isRiskbased) {
    
    EPI <- ifelse(is.na(totalN), dp, rep(dp, times = length(totalN)))
    N <- totalN
    
  } else {
    
    N <- proportionsRiskGroups * totalN
    weightedRisks <- relativeRisks / sum(relativeRisks * proportionsRiskGroups)
    EPI <- dp * weightedRisks
    
    if(any(EPI > 1)){
      stop('Some of the RiskGroups have infection probability larger than 1')
    }
    
  }
  
  populationSize <- floor(N)
  
  #Infinite
  if (method == "binom") {
    
    if (all(is.na(n))) {
      
      sampleSize <- ceiling(log(1 - sse) / log(1 - EPI * tse))
      gse <- rep(sse, length(N))
      
    } else {
      
      sampleSize <- n
      gse <- 1 - (1 - (EPI * tse))^sampleSize
      
    }
    
    maxGse <- rep(NA, length(N))
    
    #Finite
  } else {
    
    numberDiseased <- round(N * EPI)
#    numberDiseased <- N * EPI
    #numberDiseased <- ceiling(N * EPI)
    
    if ( all(is.na(n)) ) {
      
      term1 <- 1 - ((1 - sse)^(1 / numberDiseased))
      term2 <- N - 0.5* (numberDiseased * tse - 1)
      sampleSize <- ceiling((term1 * term2) / tse)
#      sampleSize <- (term1 * term2) / tse
      
      
    } else {
      
      sampleSize <- n
      
    }        
    
    numerator <- sampleSize * tse
    denominator <- N - 0.5 * (numberDiseased * tse - 1)
    # pmin because probability [0, 1]
    gse <- 1 - (1 - pmin(1, (numerator / denominator))) ^ numberDiseased
    
    maxNumerator <- populationSize * tse
    maxGse <- 1 - (1 - (maxNumerator / denominator))^numberDiseased
    
    if(!any(is.na(populationSize))){
      
      tooLarge <- which(sampleSize > populationSize)
      if(length(tooLarge > 0)){
        
#        warning("For some groups the population size is too small")
        sampleSize[tooLarge] <- populationSize[tooLarge]
        gse[tooLarge] <- maxGse[tooLarge]
        
      }
      
    }
    
    
    
#    if ( any(is.na(gse)) ) {
#      
#      stop("Population size is too small. \n 
#              Not all group sensitivity values can be calculated")
#      print(data.frame(populationSize = N, sampleSize = sampleSize))
#      
#    }
    
  }
  
  if(!reportMaxGse){
    
    returnValue <- data.frame(populationSize = populationSize, 
        sampleSize = sampleSize, gse = gse)
#    sampleSize = ceiling(sampleSize), gse = gse)
    
  } else {
    
    returnValue <- data.frame(populationSize = populationSize, 
        sampleSize = sampleSize, gse = gse, maxGse = maxGse)
#    sampleSize = ceiling(sampleSize), gse = gse)
    
  }
  
  attr(returnValue, "ase") <- 1 - prod(1 - gse, na.rm = TRUE)
  
  
  return(returnValue)
  
}



#' Calculate the optimal sample size and group sensitivity
#'  for a given target value of the area system sensitivity
#' @param targetAse target value of the area system sensitivity
#' @param totalN total population size, default value is NULL;
#'  non-NULL value needed for hypergeometric sample size calculation
#' @param dp design prevalence
#' @param tse test sensitivity
#' @param method method of sample size calculation; 
#' one of 'hyper' (default) or 'binom' 
#' @param isRiskbased logical Is the sampling risk based; 
#' default value is FALSE
#' @param relativeRisks a dataframe with relative risks for all possible 
#' risk group combinations; default value is NULL
#' @param proportionsRiskGroups a dataframe with relative proportions of 
#' total population for all possible risk group combinations; 
#' default value is NULL 
#' @return data frame reports for each risk group the population size, 
#' sample size and group sensitivity; such that the area sensitivity is targetAse
#' @export
optimizeSampleSizeGse <- function(targetAse, totalN = NULL, dp, tse,
    method = c("hyper", "binom"), isRiskbased = FALSE,
    relativeRisks = NULL, proportionsRiskGroups = NULL) {
  
  
  if(!isRiskbased){
    
    initialGse <- targetAse
    
  } else {
    
    nGroups <- length(relativeRisks)
    initialGse <- 1 - (1 - targetAse)^(1/nGroups)
    
  }
  
  returnValue <- getSampleSizeGse(sse = initialGse, n = NA, totalN = totalN, 
      dp = dp, tse = tse, method = method, isRiskbased = isRiskbased, 
      relativeRisks = relativeRisks, 
      proportionsRiskGroups = proportionsRiskGroups,
      reportMaxGse = TRUE)
  
  if(any(returnValue$maxGse < initialGse, na.rm = TRUE)){
      
    if(!isRiskbased){
      
      stop("Total population size is too small to reach target area sensitivity")
      
    } 
    
    count <- 1
    tooSmall <- which(returnValue$maxGse < initialGse)
      
      
      while(count < 10){
        
        newGse <- 1 - ((1 - targetAse)/prod(1 - returnValue$maxGse[tooSmall]))^
            (1/(nGroups - length(tooSmall)))
        
        returnValue <- getSampleSizeGse(sse = newGse, n = NA, totalN = totalN, 
            dp = dp, tse = tse, method = method, isRiskbased = isRiskbased, 
            relativeRisks = relativeRisks, 
            proportionsRiskGroups = proportionsRiskGroups,
            reportMaxGse = TRUE)
        
        if(all(which(returnValue$maxGse < newGse) == tooSmall)){
          
          returnValue$maxGse <- NULL
          return( returnValue )
          
        } else {
          
          tooSmall <- which(returnValue$maxGse < newGse)
          
        }
        
        count <- count + 1
        
      }
      
      stop("Total population size is too small to reach target area sensitivity
              (after 10 iterations)")
      
    } else {
      
      returnValue$maxGse <- NULL
      return( returnValue )
      
    }
    
    
    
  
#  for (iGse in seq(0, 0.99, 0.01)) {
#    
#    tmpResult <- getSampleSizeGse(sse = iGse, n = NA, totalN = totalN, dp = dp, 
#        tse = tse, method = method, isRiskbased = isRiskbased, 
#        relativeRisks = relativeRisks, 
#        proportionsRiskGroups = proportionsRiskGroups)
#    
#    if ( attr(tmpResult, "ase") >= targetAse) {
#      
#      return(tmpResult)
#      
#    }
#    
#  }
#  
#  stop("Total population size is too small to reach target area sensitivity")
  
}


#' Calculate the sample size and group sensitivity
#'  for a given target value of the area system sensitivity
#'  while accounting for the convenience matrix
#' @param targetAse target value of the area system sensitivity
#' @param inputConvenience numeric vector with convenience values per risk factor
#' @param maxn maximum number of observations that can be sampled 
#'  in the least convenient risk groups; default value is NA
#' @param isSampledMaxn boolean value, default is TRUE. Only used if a 
#' non-missing value for maxn is provided; 
#' if TRUE, sample size in risk groups with convenience 1 is automatically maxn,
#' if FALSE their sample size may be smaller but at most maxn 
#' @param totalN total population size, default value is NULL
#' @param dp design prevalence
#' @param tse test sensitivity
#' @param method method of sample size calculation; 
#' one of 'hyper' (default) or 'binom' 
#' @param isRiskbased logical Is the sampling risk based; 
#' default value is FALSE
#' @param relativeRisks a dataframe with relative risks for all possible 
#' risk group combinations; default value is NULL
#' @param proportionsRiskGroups a dataframe with relative proportions of 
#' total population for all possible risk group combinations; 
#' default value is NULL 
#' @return data frame reports for each risk group the population size, 
#' sample size and group sensitivity; such that the area sensitivity is targetAse
#' and size are according to input convenience values
#' @export
getConvenience <- function(targetAse, inputConvenience, maxn = NA,
    isSampledMaxn = TRUE, totalN = NULL, dp, tse, method = c("hyper", "binom"), 
    isRiskbased = FALSE, relativeRisks = NULL, proportionsRiskGroups = NULL) { 
  
  method <- match.arg(method)
  
  maxFactor <- ifelse(isSampledMaxn, ceiling(totalN / sum(inputConvenience)),
      maxn)
  tmpSampleSize <- rep(0, length(inputConvenience))
  
  if( isSampledMaxn & !is.na(maxn) ) {
    
    tmpSampleSize[ which(inputConvenience == 1) ] <- maxn 
    inputConvenience[ which(inputConvenience != 0) ] <- 
        inputConvenience[ which(inputConvenience != 0) ] - 1
    
  }
  
  for( iFactor in 1 : (maxFactor+1) ) {
    
    tmpResult <- getSampleSizeGse(sse = NA, n = tmpSampleSize, totalN = totalN, 
        dp = dp, tse = tse, method = method, isRiskbased = isRiskbased,
        relativeRisks = relativeRisks, 
        proportionsRiskGroups = proportionsRiskGroups)
    
    if (attr(tmpResult, "ase") >= targetAse) {
      
      return(tmpResult)
      
    }
    
    tmpSampleSize <- tmpSampleSize + inputConvenience 
    
  }
  
  if(isSampledMaxn){
    
    stop("Total population size is too small to reach target area sensitivity")
    
  } else {
    
    currentSampleSize <- tmpResult$sampleSize
    newConvenience <- inputConvenience
    newConvenience[ which(inputConvenience != 0) ] <- 
        newConvenience[ which(inputConvenience != 0) ] - 1
    maxFactor <- ceiling( (totalN - sum(currentSampleSize))/ sum(newConvenience) )
    
    for( iFactor in 1 : maxFactor ) {
      
      tmpSampleSize <- currentSampleSize + newConvenience*iFactor 
      tmpResult <- getSampleSizeGse(sse = NA, n = tmpSampleSize,
          totalN = totalN, dp = dp, tse = tse, method = method, 
          isRiskbased = isRiskbased, relativeRisks = relativeRisks, 
          proportionsRiskGroups = proportionsRiskGroups)
      
      if (attr(tmpResult, "ase") >= targetAse) {
        
        return(tmpResult)
        
      }
      
    }
    
    stop("Total population size is too small to reach target area sensitivity")
    
  }
  
}


#' Calculate the probability of freedom from disease
#' @param targetPFree a numeric, the targeted probability 
#' of freedom from disease
#' @param pFreePrior a numeric, the prior probability of freedom from disease
#' @param sse a numeric, the initial system sensitivity
#' @param pIntro a numeric vector, the probability that the disease was 
#' introduced since last survey or a given timespan; 
#' its length should correspond to the integer provided for timePoints
#' @param timePoints an integer, the number of time points for which the 
#' probability of freedom should be calculated; min value is 2
#' @return data frame with named numeric vectors for: 
#' pFreePrior, the prior probability of freedom from disease;
#' pFree, the probability of freedom from disease;
#' sse, the system sensitivity;
#' pIntro, the probability that disease was introduced;
#' pFreeAdjusted, the probability of freedom from disease adjusted for the 
#' fact that disease is introduced with probability pIntro 
#' @export
calculatePfree <- function(targetPFree, pFreePrior, sse, pIntro, 
    timePoints = 2) {
  
  pFree <- pFreePrior / (1 - sse*(1 - pFreePrior))
  pFreeAdjusted <- pFree * (1 - pIntro[1])
  pFreePrior[2] <- pFreeAdjusted
  
  if( length(pIntro) != timePoints) {
    
    stop("pIntro must be provided for each time point")
    
  }
  
  for (i in 2:timePoints) {
    
    for ( jSse in seq(0.01,0.99,0.01) ) {
      
      pFree[i] <- pFreePrior[i] / (1 - jSse*(1 - pFreePrior[i]))
      
      if (pFree[i] >= targetPFree){
        sse[i] <- jSse
        break()
      }
    }
    
    pFreeAdjusted[i] <- pFree[i] * (1 - pIntro[i])
    pFreePrior[i + 1] <- pFreeAdjusted[i]
    
  } 
  
  returnValue <- data.frame(pFreePrior = pFreePrior[-length(pFreePrior)],
      pFree = pFree, sse = sse, pIntro = pIntro, pFreeAdjusted = pFreeAdjusted)
  row.names(returnValue) <- paste0("timePeriod", 1:nrow(returnValue)) 
  
  return(returnValue)
  
}

#' Wrap Monte Carlo experiments around one of the functions in this package 
#' to account for uncertainty on input parameters
#' @param wrappedFunction function that needs to be wrapped 
#' One of "getSampleSizeGse", "optimizeSampleSizeGse", 
#' "getConvenience", "calculatePfree"
#' @param ... further input parameters as passed to wrappedFunction
#' @param nMC number of Monte Carlo experiments
#' @return Named list with output as from the original wrappedFunction for all 
#' Monte Carlo experiments
#' @export
wrapFunction <- function(wrappedFunction = c("getSampleSizeGse", 
        "optimizeSampleSizeGse", "getConvenience", "calculatePfree"),
    ..., nMC = 100) {
  
  wrappedFunction <- match.arg(wrappedFunction)
  
  dotList <- list(...) 
  isRandom <- sapply(dotList, function(x) ifelse(is.null(attr(x, "random")),
            FALSE, attr(x, "random")))
  outputWrapper <- list()
  
  if( any(isRandom) ){
    
    for(iMC in 1:nMC) {
      
      argList <- c(lapply(dotList[ which(isRandom) ], '[', iMC,),
          dotList[ which(!isRandom) ])
      outputWrapper[[iMC]] <- do.call(wrappedFunction, argList)
      names(outputWrapper)[iMC] <- paste0("MCrun", iMC)
      
    }
    
  } else {
    
    outputWrapper[[1]] <- do.call(wrappedFunction, dotList)
    
  }
  
  
  return(outputWrapper = outputWrapper)
  
}


#' Generate random values for uncertain input parameter
#' @param distributionName character, distribution that is assumed;
#'  one of the standard distribution names 
#' "beta", "cauchy", "chisq", "exp", "f", "gamma", "hyper", "lnorm", "nbinom",
#' "norm", "pois", "t", "unif", "weibull"; or "constant" if no uncertainty
#' @param distributionParameters numeric vector with named arguments 
#' needed for each of the distribution functions; 
#' for distribution "constant" provide the 'value' 
#' @param isQuantiles boolean vector with same length as 
#' distributionNames; indicates whether quantiles and corresponding 
#' probabilities are provided in distributionParameters 
#' @param nMC number of Monte Carlo experiments; default is 100
#' @param seed integer, seed for random number generation; default is 1
#' @return matrix with nMC random values (1 column)
#' @import rriskDistributions
#' @export
createRandom <- function(distributionName, distributionParameters, 
    isQuantiles = FALSE, nMC = 100, seed = 1) {
  
  set.seed(seed)
  
  # Prepare generating constant values
  if( distributionName == "constant" ) {
    
    names(distributionParameters) <- NULL
    distributionParameters <- c(mean = distributionParameters, sd = 0)
    distributionName <- "norm"
    
  }
  
  # Get distribution parameters based on given quantiles
  if (isQuantiles) {
    
    indexProbabilities <- grep('probabilities', names(distributionParameters))
    indexQuantiles <- grep('quantiles', names(distributionParameters))
    
    names(distributionParameters) <- NULL
    
    distributionParameters <- 
        do.call(paste0("get.", distributionName, ".par"), 
            list(p = distributionParameters[indexProbabilities],
                q = distributionParameters[indexQuantiles],
                show.output = FALSE, plot = FALSE))
    
  }
  
  # Generate random values
  distributionFunction <- paste0("r", distributionName)
  
  randomValues <- matrix(do.call(distributionFunction, 
          c(n = nMC, as.list(distributionParameters))), ncol = 1)
  
  
  # TODO provide nMC as argument for the wrapFunction(); can this work?
#doublex <- function(x,n) 2*x
#doublex(n = 5, x = rnorm(n = n, 3, 0.1))
  
  attr(randomValues, "random") <- TRUE
  return(randomValues = randomValues)
  
}


#' Get the best distributional fit & its parameters for known quantiles
#' @param probabilities a numeric vector of probabilities
#' @param quantiles a numeric vector of quantiles corresponding to probabilities
#' @param withGUI boolean, if TRUE a user-interface pops-up to choose the best
#' distributional shape, if FALSE automatically the best distribution is chosen
#' out of "normal", "beta" and "gamma"; default is FALSE 
#' @return a list with "bestName" the name of the best distribution function,
#' "bestParameters" a vector with the distribution parameter values and
#' "logLikelihood" a numeric, the (largest) log-likelihood value
#' @import rriskDistributions  
#' @export
getBestDistribution <- function(probabilities, quantiles, withGUI = FALSE) {
  
  if(withGUI){
    
    resultGUI <- fit.perc(p = probabilities, q = quantiles)
    returnList <- list(bestName = resultGUI$chosenDistr,
        bestParameters = resultGUI$fittedParams, logLikelihood = NULL)
    
    
  } else {
    
    distributions <- c("normal" = "norm", "beta" = "beta", "gamma" = "gamma")
    
    if(any(quantiles < 0 | quantiles > 1)){
      
      distributions <- distributions[(distributions != "beta")]
      
    } 
    
    if(any(quantiles < 0)){
      
      distributions <- distributions[(distributions != "gamma")]
      
    }
    
    diagnostics <- c()
    parameterEstimates <- list()
    
    for(i in seq_along(distributions)){
      
      xValues <- tryCatch(createRandom(distributionName = distributions[i], 
          distributionParameters = c(probabilities = probabilities, quantiles = quantiles), 
          isQuantiles = TRUE, nMC = 10000), error = function(e) NaN)
        
        if (all(is.nan(xValues))) {
          
          diagnostics[i] <- NA
          parameterEstimates[[i]] <- NA
          
        } else {
          
          results <- rriskFitdist.cont(xValues[,1], distr = distributions[i])
          diagnostics[i] <- results$loglik
          parameterEstimates[[i]] <- results$estimate
          
        }      
    }
    
    idBest <- which(diagnostics == max(diagnostics, na.rm = TRUE))
    
    returnList <- list(
      bestName = distributions[idBest],
      allNames = distributions,
      bestParameters = parameterEstimates[[idBest]], 
      logLikelihood = diagnostics[idBest])
    
  }
  
  return(returnList)
  
}


#' Select one scenario out of all Monte Carlo experiments
#' @param outputWrapper output object from the wrapperUncertain() function
#' @param percentile value between 0 and 1; the percentage of MC experiments with
#' smaller values for the parameterName than the one that will be reported
#' @param parameterName character; the selection will be based on this variable; 
#' if it consider several values per experiment (e.g. sampleSize per risk group) 
#' the sum will be taken
#' @return Named list with results for the provided percentile
#' @importFrom stats quantile
#' @export
summaryWrapper <- function(outputWrapper, percentile, parameterName) {
  
  parameterValues <- sapply(outputWrapper, function(x) sum(x[[parameterName]]))
  id <- which(parameterValues == quantile(parameterValues, percentile, na.rm = TRUE, type = 3))[1]
  
  return(outputWrapper[[id]])
  
}



#' Plot Histograms of Uncertainty
#' @param outputWrapper output from wrapFunction
#' @param varNames names of the variables for which to plot histograms
#' @param timePeriods, character vector with time periods for which the 
#' histogram should be plotted; default is NA
#' @importFrom graphics hist
#' @export
histogramWrapper <- function(outputWrapper, varNames, timePeriods = NA) {
  
  if( length(outputWrapper) == 1 ) {
    return()
  } else {
    
    outputArray <- array(unlist(outputWrapper), 
        dim = c(nrow(outputWrapper[[1]]), ncol(outputWrapper[[1]]), 
            length(outputWrapper)))
    
    #op <- par(ask = TRUE)
    
    for( iName in seq_along(varNames) ){
      
      column <- grep(varNames[iName], colnames(outputWrapper[[1]]))
      if(all(is.na(timePeriods))){
        
        timePeriods <- rownames(outputWrapper[[1]])  
        for( jLine in seq_along(timePeriods) ){
          
          hist(outputArray[jLine, column, ], 
              xlab = varNames[iName], main = timePeriods[jLine])
          
        }
        
      } else{
        
        for( jLine in timePeriods ){
          
          row <- grep(jLine, rownames(outputWrapper[[1]]))      
          hist(outputArray[row, column, ], 
              xlab = varNames[iName], main = jLine)
          
        }
        
      }
      
      
      
    }
    
    #par(op)
    
  }
  
}