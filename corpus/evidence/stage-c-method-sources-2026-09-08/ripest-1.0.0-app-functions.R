# Project: efsa-plh-surveillance_git
# 
# Author: dbemelmans
###############################################################################

#' Get answers for the survey type in question in case the answers
#' cannot be found in the database
#' @param surveyType character, should be one of 
#' \code{c("detection", "delimiting", "buffer")}
#' @param phase character, should be one of 
#'    \code{c("initiation", "preparation", "design", "implementation")}
#' @param question character, code for the question
#' @return character
#' 
#' @author dbemelmans
#' @export 
getAnswers <- function(surveyType, phase, question) {
  
  answers <- switch(surveyType, 
      "detection" = switch(phase,
          "initiation" = list(
              "Q1A" = c("",
                  "Comply with regulatory requirements",
                  "Finding and outbreak",
                  "Other"),
              "Q1C2" = c("", 
                  "Absent",
                  "Present"),
              "Q1D" = c("",
                  "Upload a map (shapefile)",
                  "Select the area (NUTS 0,1,2,3)")
          )
      
      ),
      "delimiting" = switch(phase,
          "initiation" = list(
              "Q1A" = c("Delimiting survey"),
              "Q1C2" = c("", 
                  "Absent",
                  "Present"
              ),
              "Q1D" = c("",
                  "Upload a map of the demarcated area (shapefile)",
                  "Define the provisional demarcated area. ") 
          )
      
      ),
      "buffer" = switch(phase,
          "initiation" = list(
              "Q1A" = c("Bufffer zone survey"),
              "Q1C2" = c("", 
                  "Absent",
                  "Present"
              )
          )
      )
  )
  
  return(answers)
  
}

#' Get label for data frames
#' 
#' @param abbreviation character
#' @param rev logical 
#' @return vector
#' 
#' @author dbemelmans
#' @export
getLabel <- function(abbreviation, 
    rev = FALSE) {
  
  allLabels <- c(
      "theoreticalSampleSize" = "Theoretical sample size",
      "epiUnit" = "Epidemiological unit",
      "populationSize" = "Population size",
      "theoreticalAchievedConfidenceLevel" = "Theoretical achieved confidence level",
      "actualAchievedConfidenceLevel" = "Actual achieved confidence level",
      "riskLevel" = "Risk level",
      "cellId" = "Cell identifier",
      "populationSizeCell" = "Total number of cells",
      "theoreticalSampleSizeCell" = "Theoretical cells to be visisted",
      "actualSampleSizeCell" = "Actual cells visited",
      "numberRiskLocations" = "No. of risk locations",
      "proportionRiskLocations" = "Proportion of risk locations",
      "updatedTheoreticalSampleSize" = "Updated theoretical sample size",
      "proportionHostPlants" = "Proportion of host plant population",
      "numberHostPlants" = "No. of host plants",
      "riskLevel1" = "Risk level 1",
      "riskLevel2" = "Risk level 2",
      "undeterminedSamples" = "Undetermined samples",
      "positiveSamples" = "Positive samples",
      "negativeSamples" = "Negative samples"
  )
  
  if(rev) {
    names(allLabels[match(abbreviation, allLabels)])
  } else {
    allLabels[abbreviation]
  }
  
}

#' Get question per phase
#' @param phase character, should be one of 
#'    \code{c("initiation", "preparation", "design", "implementation")}
#' @return character
#' 
#' @author dbemelmans
#' @export
getQuestion <- function(phase) {
  
  allQuestions <- switch(phase, 
      "initiation" = c(
          "Q1A" = "What is the motivation of the survey?",
          "Q1AOther" = "Please provide additional details on the purpose of the survey.",
          "Q1C1" = "What is the target pest of the survey?",
          "Q1C2" = paste0("What is the status of the pest in your ", tooltip(name = "target population"), "?"),
          "Q1C2Delim" = "What was the status of the pest in the outbreak area prior to the finding?",
          "Q1C2Buffer" = "What is the status of the pest in the buffer zone?",
          "Q1C2Other" = "Describe the status of the pest in your target population.",
          "Q1C21" = "When was the last survey conducted for the same pest and target population?",
          "Q1C21Delim" = "When was the last detection survey conducted without finding the pest for the same target population?",
          "Q1C21Buffer" = "When was the last buffer zone survey conducted without finding the pest for the same target population?",
          "Q1C21Date" = "Please provide the year of the last survey.",
          "Q1C21SurveyType" = "Which survey(s) was(were) conducted in that year?",
          "Q1C3" = "How many findings have been made for the pest?", 
          "Q1D0" = "Member State",
          "Q1D" = "What is the survey area?",
          "Q1DShapefile" = "Upload at least 4 files with following extensions: .shp, .shx, .prj and .dbf ",
          "Q1DNUTS" = "Select the appropriate NUTS classification.",
          "Q1E1" = "Which host plants or environmental components (soil, water...) are targeted by the survey?",
          "Q1E1Other" = "Please describe what is targeted by the survey.",
          "Q1E2" = "Do you have a shapefile with the host plant distribution?",
          "Q1E21" = "Upload at least 4 files with following extensions for the host plant distribution: .shp, .shx, .prj and .dbf ",
          "Q1E22" = "Indicate the area covered by the host plants. [ha]",
          "Q1E4" = "Indicate the average host plant density. [plants/ha]"
      ),
      "detection" = c(
          "1" = "1. Characterise the pest",
          "2" = "2. Target population",
          "3" = "3. Inspection units"
      ),
      "detection_preparation" = c(
          "Q1A1" = "Which statement is true for the targeted pest?",
          "Q1A2" = "Can the targeted pest be distributed by vectors?",
          "Q1A3" = "Upload a shapefile of the environment's suitability for the targeted pest. (Optional)",
          "Q1B0" = "Do you want to use the two-step approach?",
          "Q1B01" = paste0("What is the ",  tooltip(name = "inspection unit"), " considered in the survey?"),
          "Q1B1" = paste0("What is(are) the ", tooltip(name = "inspection unit"), "(s) considered in the survey?"),
          "Q1B10" = paste0("Can the target ", tooltip(name = "population size"), " be considered infinite?"),
          "Q1B00" = "What is the area of a cell? [ha]",
          "Q1B11" = "Indicate the number of inspection units that can be found in the area to be surveyed.",
          "Q1B12" = "Indicate the approximate number of inspection units that can be found in the area to be surveyed.",
          "Q1B11TwoStep" = "Indicate the average number of inspection units that can be found in one cell.",
          "Q1B2" = "How can you divide the target population?",
          "Q1B21" = "How many epidemiological units do you want to define?",
          "Q1B22" = "Select the appropriate NUTS classification.",
          "Q1B3" = "Do you want to conduct a risk based survey?",
          "Q1B31" = "Does the risk depend on the spread capacity?",
          "Q1B32" = "Are there any other risk factors?",
          "Q1B33" = "How many other factors do you want to include?",
          # detection methods
          "Q2C1" = "How many detection methods will you use?",
          "Q2C11" = "What type of survey procedure is applied in the field to detect the pest?",
          "Q2C2" = "What is the type of survey site?",
          "Q2C2Other2" = "Please describe the survey site in open air.",
          "Q2C2Other3" = "Please describe the survey site in physically closed conditions.",
          "Q2C22" = "Specify the survey site.",
          "Q2C31" = "Survey period start",
          "Q2C32" = "Survey period end",
          "Q2C111" = "Indicate the type of trap.",
          "Q2C112" = "Which other detection method is used in the field?",
          "Q2C12" = "Which sampling matrix or matrices are collected?", 
          "Q2C13" = paste0("What is the ",  tooltip(name = "sampling effectiveness"), "? [%]"),
          "Q2C14" = "Please describe the main steps (e.g. screening, isolation, extraction, sample preparation, detection, confirmation) in the laboratory procedure:",
          "Q2C14Specific" = "Please select the specific laboratory methods.",
          "Q2C15" = paste0("What is the ", tooltip(name = "diagnostic sensitivity"), " of the full laboratory procedure? [%]")
      
      ),
      "detection_design" = c(
          "Q1" = "How many risk levels do you want to take into account?",
          "Q3A" =  "Convenience sampling approach",
          "Q3ALimitUpper" = "Upper limit",
          "Q3ALimitLower" = "Lower limit",
          "Q4" = "Do you want to reallocate the samples to the epidemiological units?",
          "Q4A" = "How do you want to allocate the samples?"
      ),
      "detection_implementation" = c(
          "Q1A" = "Do you want to include the geographic coordinates of the inspection units?",
          "Q1ACell" = "Do you want to include the geographic coordinates of the cells?",
          "Q2ACell" = "Do you have clear survey instructions in the field?",
          "Q2A1Cell" = "Please provide instructions for sampling in the within the cell." 
      ),
      "detection_conclusion" = c(
          "Q1" = "Was the pest found during the survey?"
      ),
      "delimiting" = c(
          "1" = "1. Source(s) of infestation",
          "2" = "2. Estimate boundaries", 
          "3" = "3. Delimit boundaries"),
      "delimiting_preparation" = c(
          "Q1D" = "Indicate the annual short-distance spread rate of the pest (m).",
          "Q1D_checkbox" = "Is the annual short-distance spread rate the median value? (if not checked use the mean)",
          "riskLocationsFile" = "Upload excel file with all risk locations. (.xlsx) (Optional)",
          "Q1E1" = "Choose the approach for performing the delimiting survey."
      ),
      "delimiting_design" = c(
          "Q1B1" = "Indicate the number of inspection units that can be found in the green survey area.",
          "Q1B2" = "Confidence level (%)",
          "Q1B3" = "Design prevalence (%)",
          "Q1B4" = "Method sensitivity",
          "Q1B5" = "Please select one of the following options.",
          "Q1B51" = "Provide a file with all inspection units and locations in the survey area. (.xlsx)",
          "Q1B52" = "Provide a file with all taken samples and locations in the survey area. Also indicate
              if the sample was positive (1) or negative (0). (.xlsx)",
          "Q1B61" = "How many findings have been made for the pest?",
          "Q1B72A" = "Upload file with samples, containing all results."
      ),
      "buffer" = c(
          "1" = "1. Define infested zone",
          "2" = "2. Target population",
          "3" = "3. Inspection units"
      ),
      "buffer_preparation" = c(
          "Q1G1" = "What is the upper range of the yearly spread capacity of the pest? [m]",
          "Q1G2" = "Do you have a file with information about the infested zone from this tool?", 
          "Q1G21" = "How many centers does the infested zone contain?"
      )
  
  )
  
  allQuestions
  
}

#' Set tooltip with definition/formula
#' @param name character, keyword with definition/formula
#' @param definitions data.frame
#' @return ui
#' 
#' @author dbemelmans
#' @export
tooltip <- function(name, 
    definitions = allData$definitions) {
  
  keyword_row <- definitions[tolower(definitions$keyword) == tolower(name), ]
  keyword_definition <- keyword_row[1, "definition"]
  
  tagList(
      div(class = "customTooltip",
          title = keyword_definition,
          HTML(paste0(icon("lightbulb", "fa-regular"), name))
      )
  )
  
}

#' read tables from sqlite database
#' @param table character, table in database
#' @return data.frame
#' 
#' @import RSQLite
#' @author dbemelmans
#' @export 
loadTableSQLite <- function(table)  {
  # open connection
  filepath <- paste0(file.path(system.file("extdata", package = "surveillance")), "/relationalDatabase.db")
  sqlite.driver <- RSQLite::dbDriver("SQLite")
  con <- RSQLite::dbConnect(sqlite.driver, filepath)
  
  table <- RSQLite::dbReadTable(con, table)
  
  # close connection
  RSQLite::dbDisconnect(con)
  
  table
  
}

#' Select hosts for the selected pest 
#' @param pestName character, pest selected by user
#' @param pestTable data.frame
#' @return data.frame
#' 
#' @import RSQLite
#' @author dbemelmans
#' @export 
loadHosts <- function(pestName,
    pestTable)  {
  
  pestId <- pestTable[pestTable$Scientific_name == pestName, "Id_Pest"]
  
  if(length(pestId) == 0) {
    return(NULL)
  } else {
    
    # open connection
    filepath <- paste0(file.path(system.file("extdata", package = "surveillance")), "/relationalDatabase.db")
    sqlite.driver <- RSQLite::dbDriver("SQLite")
    con <- RSQLite::dbConnect(sqlite.driver, filepath)
    
    table <- RSQLite::dbGetQuery(con, 
        paste0('
                SELECT HOST.Id_Host, HOST.Scientific_name
                FROM HOST
                INNER JOIN UnionHostPestT ON HOST.Id_Host = UnionHostPestT.Id_Host
                INNER JOIN PEST ON UnionHostPestT.Id_Pest = PEST.Id_Pest 
                WHERE PEST.Id_Pest = ', pestId)
    )
    
    # close connection
    RSQLite::dbDisconnect(con)
    
    if(nrow(table) == 0) {
      return(NULL)  
    } else {
      return(table)  
    }
    
  }
}


#' Create dateInput widget with the min view mode argument (in order to only select a year-month)
#' @param minViewMode numeric, set a minimum limit for the view mode. 
#' Accepts: 0 or “days” or “month”, 1 or “months” or “year”, 2 or “years” or “decade”, 3 or “decades” or “century”, 
#' and 4 or “centuries” or “millenium”. Gives the ability to pick only a month, a year or a decade. 
#' The day is set to the 1st for “months”, and the month is set to January for “years”, 
#' the year is set to the first year from the decade for “decades”, and the year is set to the first from the millennium for “centuries”.
#' @param maxViewMode numeric, set a maximum limit for the view mode.
#' @param startDate character, The earliest date that may be selected; all earlier dates will be disabled. ("yyyy-mm-dd")
#' @param needMonths logical, show format "mm-yyyy"
#' @param ... other possible parameters of the dateInput
#' @inheritParams shiny::dateInput
#' @return data.frame
#' @author dbemelmans
#' @export 
dateInputCustom <- function(inputId, label, minViewMode = 2, maxViewMode = 2, startDate = NULL, needMonths = FALSE, ...) { # set default values
  if(needMonths) {
    cal <- shiny::dateInput(inputId, label, format = "mm-yyyy", ...)
  } else {
    cal <- shiny::dateInput(inputId, label, format = "yyyy", ...)  
  }
  
  cal$children[[2L]]$attribs[["data-date-min-view-mode"]] <- minViewMode
  cal$children[[2L]]$attribs[["data-date-start-date"]]    <- startDate
  cal
}


#' Calculate the CL per unit
#' @param overallCL numeric, overall confidence level
#' @param N integer, number of areas that need to be combined to achieve the
#'  overall confidence level
#' @return numeric 
#' 
#' @author dbemelmans
#' @export
confidenceLeveli <- function(overallCL, N) {
  
  CLi <- 1 - (1 - overallCL)^(1/N)
  
  return(CLi)
  
}

#' Calculate the overall CL
#' @param CLis vector, confidence levels per epi unit
#' @return numeric 
#' 
#' @author dbemelmans
#' @export
overallCL <- function(CLis) {
  
  tmpResult <- 1
  
  for(CLi in CLis) {
    tmpResult <- tmpResult * (1 - CLi)
  }
  
  1 - tmpResult
  
}

#' Combines risk factor tables in case of two risk factors,
#' makes the table ready to input in ribess function
#' @param table1 data.frame, risk factor table (label, relative, proportion)
#' @param table2 data.frame, risk factor table (label, relative, proportion)
#' @return data.frame
#' 
#' @author dbemelmans
#' @export
combineRiskFactorTables <- function(table1, table2) {
  
  noRow1 <- nrow(table1)
  noRow2 <- nrow(table2)
  
  resultTable <- data.frame()
  
  table1$proportion <- table1$proportion / 100
  table2$proportion <- table2$proportion / 100
  
  for(i in 1:noRow1) {
    for(j in 1:noRow2) {
      newRow <- data.frame(
          label1 = table1$label[i],
          label2 = table2$label[j],
          relative = table1$relative[i]*table2$relative[j],
          proportion = table1$proportion[i] * table2$proportion[j]
      )
      resultTable <- rbind(resultTable, newRow)
    }
  }
  
  resultTable$proportion <- resultTable$proportion * 100 
  
  resultTable
  
}


#' Shape the input from the user to feed to the ribess function to calculate 
#' the sample size
#' @param confidenceLevel numeric, in \%
#' @param targetPopulationSize numeric
#' @param designPrevalence numeric, in \%
#' @param sensitivities vector
#' @param infinite logical
#' @param names vector
#' @param isRiskBased logical
#' @param table1 data.frame
#' @param table2 data.frame
#' @param riskLabels vector
#' @return data.frame
#' 
#' @author dbemelmans
#' @export 
estimateSampleSize <- function(
    confidenceLevel, 
    targetPopulationSize, 
    designPrevalence,
    sensitivities,
    infinite,
    names,
    isRiskBased = FALSE,
    table1 = NULL,
    table2 = NULL,
    riskLabels = NULL) {
  
  sse <- confidenceLevel/100
  totalN <- targetPopulationSize
  if(is.null(totalN))
    totalN <- NA
  dp <- designPrevalence/100
  
  tmpSolution <- 1
  for(sensitivity in sensitivities) {
    tmpSolution <- tmpSolution * (1 - sensitivity)
  }
  tse <- 1 - tmpSolution
  
  # infinite population size? 
  if(infinite) {
    method <- "binom"
  } else {
    method <- "hyper"
  }
  
  if(isRiskBased) {
    
    if(!is.null(table2)) {
      # in case of two risk factors combine the table
      table1$proportion <- table1$proportion / 100
      table2$proportion <- table2$proportion / 100
      riskTable <- combineRiskFactorTables(table1, table2)
    } else {
      table1$proportion <- table1$proportion / 100
      riskTable <- table1
    }
    
    # update confidence level per risk level
    N <- nrow(riskTable)
    sse <- 1 - (1 - sse) ^ (1/N)
    
    relativeRisks <- as.vector(t(riskTable$relative))
    proportionRiskGroups <- as.vector(t(riskTable$proportion))
    
  }
  
  # binom is infinite population size, hyper is finite population size
  table <- ribess::getSampleSizeGse(sse = sse,
      totalN = totalN,
      dp = dp,
      tse = tse,
      method = method,
      isRiskbased = isRiskBased,
      relativeRisks = relativeRisks,
      proportionsRiskGroups = proportionRiskGroups)
  
  if(isRiskBased) {
    
    table <- cbind(riskTable[grepl("label", colnames(riskTable))], 
        table)
    colnames(table) <- c(paste0("Risk level ", 1:length(riskLabels)), names)
  } else {
    colnames(table) <- names
  }
  
  return(table)
  
}

#' Estimate the confidence level 
#' 
#' @param targetPopulationSize numeric
#' @param sampleSize vector
#' @param designPrevalence numeric
#' @param methodSensitivity numeric, 
#' @param isInfinite logical 
#' @param isRiskbased logical
#' @param riskTable1 data.frame
#' @param riskTable2 data.frame
#' @return numeric, achieved confidence level
#' 
#' @import ribess
#' @author dbemelmans
#' @export
estimateConfidenceLevel <- function(targetPopulationSize,
    sampleSize, 
    designPrevalence,
    methodSensitivity,
    isInfinite,
    isRiskbased = FALSE,
    riskTable1, 
    riskTable2) {
  
  # infinite population size? 
  if(isInfinite) {
    method <- "binom"
  } else {
    method <- "hyper"
  }
  
  if(isRiskbased) {
    if(!is.null(riskTable2)) {
      riskTable <- combineRiskFactorTables(riskTable1, riskTable2)
    } else {
      riskTable <- riskTable1
    }
  } else {
    riskTable <- NULL
  }
  
  if(!is.null(riskTable)) {
    relativeRisks <- as.vector(t(riskTable$relative))
    proportionsRiskGroups <- as.vector(t(riskTable$proportion)) / 100
  } else {
    relativeRisks <- NULL
    proportionsRiskGroups <- NULL
  }
  
  ribess::getSampleSizeGse(sse = NA, 
      n = sampleSize,
      totalN = targetPopulationSize, 
      dp = designPrevalence,
      tse = methodSensitivity,
      method = method, 
      isRiskbased = isRiskbased,
      relativeRisks = relativeRisks,
      proportionsRiskGroups = proportionsRiskGroups)
  
}

#' Calculate the shortest distance between two points on earth
#' @param point1 vector, containing the latitude and longitude
#' @param point2 vector, containing the latitude and longitude
#' @return numeric, distance in metres
#' 
#' @author dbemelmans
#' @export 
getDistance <- function(point1, point2) {
  
  lat1 <- point1[1]
  lat2 <- point2[1]
  
  lon1 <- point1[2]
  lon2 <- point2[2]
  
  # mean radius of the earth
  R <- 6371e3
  phi1 <- lat1 * pi/180
  phi2 <- lat2 * pi/180 
  delta_phi <- (lat2-lat1) * pi/180
  delta_lambda <- (lon2-lon1) * pi/180 
  
  a <- sin(delta_phi/2) * sin(delta_phi/2) +
      cos(phi1) * cos(phi2) *
      sin(delta_lambda/2) * sin(delta_lambda/2);
  c <- 2 * atan2(sqrt(a), sqrt(1-a));
  
  R * c 
  
}

#' Create a leaflet map for the delimiting survey
#' @param noMap integer, map number
#' @param latitude numeric, latitude of the centroid
#' @param longitude numeric, longitude of the centroid
#' @param radius1 numeric, radius of the PIZ
#' @param radius2 numeric, radius of the PIZ + band
#' @param centroid vector, contains centre of extra circle
#' @return leaflet
#' 
#' @author dbemelmans
#' @export
createDelimitingMap <- function(noMap, 
    latitude, 
    longitude, 
    radius1,
    radius2,
    centroid = NULL) {
  
  labelPIZ <- paste0("PIZ ", noMap)
  labelBand <- paste0("Band ", noMap)
  
  myData <- data.frame(lon = longitude, lat = latitude)
  
  if(!is.null(centroid)) {
    
    myCentroid <- data.frame(lon = centroid[2], lat = centroid[1])
    labelBandCentroid <- paste0("Band ", noMap, " (to survey)")
    labelBand <- paste0("Band ", noMap, " (already surveyed)")
    map <- leaflet() %>%
        setView(lng = longitude, lat = latitude, zoom = 09) %>%
        addTiles() %>%
        addCircles(data = myCentroid,
            radius = radius2,
            stroke = FALSE,
            fillOpacity = 1,
            color = "#062E03",
            label = labelBandCentroid) %>%
        addCircles(data = myData,
            radius = radius2,
            stroke = FALSE,
            fillOpacity = 1,
            color = "green",
            label = labelBand) %>%
        addCircles(data = myCentroid,
            radius = radius1,
            stroke = FALSE,
            fillOpacity = 1,
            color = "red", 
            label = labelPIZ) %>%
        addCircles(data = myData,
            radius = radius1,
            stroke = FALSE,
            fillOpacity = 1,
            color = "red", 
            label = labelPIZ)
    
  } else {
    
    map <- leaflet() %>%
        setView(lng = longitude, lat = latitude, zoom = 09) %>%
        addTiles() %>%
        addCircles(data = myData,
            radius = radius2,
            stroke = FALSE,
            fillOpacity = 1,
            color = "green",
            label = labelBand) %>%
        addCircles(data = myData,
            radius = radius1,
            stroke = FALSE,
            fillOpacity = 1,
            color = "red", 
            label = labelPIZ)
  }
  
  map
  
}

#' Calculates the area of a circle
#' @param radius numeric, radius of the circle
#' @return numeric
#' 
#' @author dbemelmans
#' @export
getCircleArea <- function(radius) {
  pi*radius^2
}

#' Calculate the centroid (only valid over short distances)
#' @param myTable data.frame, contains the latitude and longitude
#' @return vector
#' 
#' @author dbemelmans
#' @export
getCentroid <- function(myTable) {
  
  latitude <- sum(myTable$latitude)/nrow(myTable)
  longitude <- sum(myTable$longitude)/nrow(myTable)
  
  return(data.frame(latitude = latitude, longitude =longitude))
}

#' Create the start map for the delimiting survey
#' @param tableCenters data.frame, the locations of the centers
#' @param medianSpreadRate numeric, the median spread rate (width of the band in meters) 
#' @param newSmallRadius numeric, a newly created radius for the conservative approach
#' @param findings data.frame, contains label, longitude and latitude of relevant finding(s)
#' @param riskLocations data.frame, contains label, longitude and latitude of relevant risk location(s)
#' @param expanding logical, if survey area of the delimiting area
#' @return leaflet
#' 
#' @author dbemelmans
#' @export
createDelimitingStartMap <- function(tableCenters,
    medianSpreadRate,
    newSmallRadius,
    findings = NULL, 
    riskLocations = NULL,
    expanding = NULL) {
  
  iconsR <- awesomeIcons(
      icon = 'ios-close',
      iconColor = 'black',
      library = 'ion',
      markerColor = "orange"
  )
  
  iconsF <- awesomeIcons(
      icon = 'ios-close',
      iconColor = 'black',
      library = 'ion',
      markerColor = "red"
  )
  
  map <- leaflet() %>% 
      setView(lng = tableCenters[1, "longitude"], lat = tableCenters[1, "latitude"], zoom = 09) %>%
      addTiles()
  
  if(!is.null(findings)) {
    map <- map %>%
        addAwesomeMarkers(lng = findings[, "Longitude"], 
            lat = findings[, "Latitude"], 
            label = findings[, "finding"],
            icon = iconsF)
  }
  
  if(!is.null(riskLocations)) {
    map <- map %>%
        addAwesomeMarkers(lng = riskLocations[, "longitude"], 
            lat = riskLocations[, "latitude"], 
            label = riskLocations[, "label"], 
            icon = iconsR) 
  }
  
  for(iRow in 1:nrow(tableCenters)) {
    
    rowCenter <- tableCenters[iRow, ]
    if(is.null(newSmallRadius)) {
      bigRadius <- medianSpreadRate + rowCenter$PIZbase
    } else {
      bigRadius <- medianSpreadRate + newSmallRadius
    }
    
    map <- map %>% 
        addCircles(lng = rowCenter$longitude,
            lat = rowCenter$latitude,
            radius = bigRadius,
            stroke = FALSE,
            fillOpacity = 1,
            color = "green",
            label = "band 1"
        )
  }
  
  for(iRow in 1:nrow(tableCenters)) {
    
    rowCenter <- tableCenters[iRow, ]
    
    if(is.null(newSmallRadius)) {
      smallRadius <- rowCenter$PIZbase
    } else {
      smallRadius <- newSmallRadius
    }
    
    
    map <- map %>% 
        addCircles(lng = rowCenter$longitude,
            lat = rowCenter$latitude,
            radius = smallRadius,
            stroke = FALSE,
            fillOpacity = 1,
            color = "red",
            label = "PIZ 1"
        )
  }
  
  map
  
}

#' Creates the map of the buffer zone
#' 
#' @param tableCenters data.frame, contains the data from the delimiting survey
#' @param conservativeRadius numeric, the radius in case of the conservative approach
#' @param bufferWidth numeric, the width of the buffer band (m)
#' @return leaflet
#' 
#' @author dbemelmans
#' @export
createBufferZoneMap <- function(tableCenters, 
    conservativeRadius = NULL,
    bufferWidth) {
  
  map <- leaflet() %>%
      setView(lng = tableCenters[1, "Longitude"], lat = tableCenters[1, "Latitude"], zoom = 09) %>%
      addTiles()
  
  for(i in 1:nrow(tableCenters)) {
    if(is.null(conservativeRadius)) {
      radius <- bufferWidth + tableCenters[i, "Radius [m]"] 
    } else {
      radius <- bufferWidth + conservativeRadius
    }
    
    map <- map %>%
        addCircles(lng = tableCenters[i, "Longitude"],
            lat = tableCenters[i, "Latitude"],
            radius = radius,
            stroke = FALSE,
            fillOpacity = 1,
            color = "green",
            label = "Buffer band")
  }
  
  
  for(i in 1:nrow(tableCenters)) {
    if(is.null(conservativeRadius)) {
      radius <- tableCenters[i, "Radius [m]"]
    } else {
      radius <- conservativeRadius
    }
    
    map <- map %>%
        addCircles(lng = tableCenters[i, "Longitude"],
            lat = tableCenters[i, "Latitude"],
            radius = radius,
            stroke = FALSE,
            fillOpacity = 1,
            color = "orange",
            label = "Infested zone")
  }
  
  map
  
}

#' Creates the map of the buffer zone
#' 
#' @param tableCenters data.frame, contains the data from the delimiting survey
#' @param conservativeRadius numeric, the radius in case of the conservative approach
#' @return leaflet
#' 
#' @author dbemelmans
#' @export
createInfestedZone <- function(tableCenters, 
    conservativeRadius) {
  
  map <- leaflet() %>% 
      setView(lng = tableCenters[1, "longitude"], lat = tableCenters[1, "latitude"], zoom = 09) %>%
      addTiles()
  
  for(iRow in 1:nrow(tableCenters)) {
    
    rowCenter <- tableCenters[iRow, ]
    
    if(is.null(conservativeRadius)) {
      smallRadius <- rowCenter$PIZbase 
    } else {
      smallRadius <- conservativeRadius
    }
    
    map <- map %>% 
        addCircles(lng = rowCenter$longitude,
            lat = rowCenter$latitude,
            radius = smallRadius,
            stroke = FALSE,
            fillOpacity = 1,
            color = "red",
            label = "Infested zone"
        )
  }
  
  map
  
}
