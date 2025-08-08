report_original_path <- paste0(snakemake@params[[3]], "/workflow/rules/Report.rmd")
report_tmp_path <- paste0(snakemake@params[[1]], "/results/tmp/Report.rmd")
file.copy(report_original_path, report_tmp_path, overwrite = TRUE)

# copy workflow overview
wf_image_original_path <- paste0(snakemake@params[[3]], "/workflow/rules/Workflow.png")
wf_image_tmp_path <- paste0(snakemake@params[[1]], "/results/tmp/Workflow.png")
file.copy(wf_image_original_path, wf_image_tmp_path, overwrite = TRUE)

rmarkdown::render(report_tmp_path,
  output_dir = paste0(snakemake@params[[1]], "/results/"),
  params = list(config = snakemake@params[[2]],  
  snake_dir = snakemake@params[[3]],
  workflow_type = snakemake@params[[2]][["workflow_type"]]),
  output_format = "html_document"
)
