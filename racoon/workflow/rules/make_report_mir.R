rmarkdown::render("workflow/rules/Report_miR.rmd",
  output_dir=paste0(snakemake@params[[1]],"/results/"),
 params=list(config=snakemake@params[[2]]),
 output_format = "html_document")
