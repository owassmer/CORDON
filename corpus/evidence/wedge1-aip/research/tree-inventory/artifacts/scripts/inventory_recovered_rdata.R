#!/usr/bin/env Rscript
args <- commandArgs(trailingOnly = TRUE)
if (length(args) != 2) stop("usage: inventory_recovered_rdata.R SNAPSHOT_DIR OUT_CSV")
base <- normalizePath(args[[1]])
out <- args[[2]]
files <- list.files(base, pattern = "\\.RData$", recursive = TRUE, full.names = TRUE)
rows <- list()
for (f in files) {
  e <- new.env()
  suppressWarnings(load(f, envir = e))
  for (n in ls(e)) {
    o <- get(n, e)
    rows[[length(rows) + 1]] <- data.frame(
      file = sub(paste0("^", base), "", f),
      object = n,
      class = paste(class(o), collapse = "/"),
      rows = ifelse(length(dim(o)) >= 1, dim(o)[1], NA),
      columns = ifelse(length(dim(o)) >= 2, dim(o)[2], NA),
      bytes_in_memory = as.numeric(object.size(o)),
      column_names = ifelse(is.data.frame(o), paste(names(o), collapse = "|"), ""),
      stringsAsFactors = FALSE
    )
  }
}
write.csv(do.call(rbind, rows), out, row.names = FALSE)
cat(length(files), "RData files inventoried into", out, "\n")
