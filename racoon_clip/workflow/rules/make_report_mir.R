# change lib path to lib of conda env
args = commandArgs(trailingOnly = TRUE)
paste0(args[[3]], "/lib/R/library/")[1]
.libPaths(c(paste0(args[[3]], "/lib/R/library/")))
# copy report md
report_original_path <- paste0(args[[2]], "/workflow/rules/Report_miR.rmd")
report_tmp_path <- paste0(args[[1]], "/results/tmp/Report_miR.rmd")
file.copy(report_original_path , report_tmp_path, overwrite = TRUE)

#print(report_tmp_path)

# copy workflow overview
wf_image_original_path <- paste0(args[[2]], "/workflow/rules/miRpipe-Figure_v2.png")
wf_image_tmp_path <- paste0(args[[1]], "/results/tmp/miRpipe-Figure_v2.png")
file.copy(wf_image_original_path, wf_image_tmp_path, overwrite = TRUE)

rmarkdown::render(report_tmp_path,
  output_dir = paste0(args[[1]], "/results/"),
  params = list(config = list(args),  
                snake_dir = args[[2]],
                output_dir = paste0(args[[1]], "/results/")),
  output_format = "html_document"
)

