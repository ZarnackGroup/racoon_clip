# find_pandoc(cache = TRUE, dir = /home/mklostermann/applications/anaconda3/envs/racoon_r_fix1/bin/pandoc, version = NULL)
#Sys.setenv(RSTUDIO_PANDOC="--- insert directory here ---")

#pre_c <- read.delim(snakemake@input[[2]], header = F)
#pre_c[1, 1]

#paste0(pre_c[1,1], "/bin/pandoc")
#rmarkdown::find_pandoc(dir = paste0(pre_c[1,1], "/bin/"))

#https://community.rstudio.com/t/cannot-open-file-myfile-knit-md-read-only-file-system/59941
report_path <- tempfile(fileext = ".Rmd")
file.copy("report.Rmd", report_path, overwrite = TRUE)

rmarkdown::render(paste0(snakemake@params[[3]], "/workflow/rules/Report.rmd"),
  output_dir=paste0(snakemake@params[[1]],"/results/"),
 params=list(config=snakemake@params[[2]]),
 output_format = "html_document")
