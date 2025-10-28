# Verbose logging for debugging
cat("=== Starting Report Generation ===\n")
cat("Working directory:", getwd(), "\n")
cat("Snake params:\n")
cat("  wdir:", snakemake@params[[1]], "\n")
cat("  snake_path:", snakemake@params[[3]], "\n")

report_original_path <- paste0(snakemake@params[[3]], "/workflow/rules/Report.rmd")
report_tmp_path <- paste0(snakemake@params[[1]], "/results/tmp/Report.rmd")

cat("Copying Report.rmd:\n")
cat("  From:", report_original_path, "\n")
cat("  To:", report_tmp_path, "\n")
if (!file.exists(report_original_path)) {
  stop("ERROR: Report.rmd source file not found at: ", report_original_path)
}
file.copy(report_original_path, report_tmp_path, overwrite = TRUE)
if (!file.exists(report_tmp_path)) {
  stop("ERROR: Failed to copy Report.rmd to: ", report_tmp_path)
}

# copy workflow overview
wf_image_original_path <- paste0(snakemake@params[[3]], "/workflow/rules/racoon_clip_workflow_2.0.png")
wf_image_tmp_path <- paste0(snakemake@params[[1]], "/results/tmp/Workflow.png")

cat("Copying Workflow.png:\n")
cat("  From:", wf_image_original_path, "\n")
cat("  To:", wf_image_tmp_path, "\n")
if (!file.exists(wf_image_original_path)) {
  warning("WARNING: Workflow.png not found at: ", wf_image_original_path)
} else {
  file.copy(wf_image_original_path, wf_image_tmp_path, overwrite = TRUE)
  cat("  Success!\n")
}

cat("\nRendering R Markdown report:\n")
cat("  Template:", report_tmp_path, "\n")
cat("  Output dir:", paste0(snakemake@params[[1]], "/results/"), "\n")
cat("  Workflow type:", snakemake@params[[2]][["workflow_type"]], "\n")

tryCatch({
  rmarkdown::render(report_tmp_path,
    output_dir = paste0(snakemake@params[[1]], "/results/"),
    params = list(config = snakemake@params[[2]],  
    snake_dir = snakemake@params[[3]],
    workflow_type = snakemake@params[[2]][["workflow_type"]]),
    output_format = "html_document"
  )
  cat("\n=== Report Generation Complete ===\n")
}, error = function(e) {
  cat("\n!!! ERROR during report rendering !!!\n")
  cat("Error message:", conditionMessage(e), "\n")
  cat("Call stack:\n")
  print(traceback())
  stop(e)
})

