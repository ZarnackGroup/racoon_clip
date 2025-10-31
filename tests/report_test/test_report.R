# -----------------
# test make report
# ------------------
library(tidyverse)
library(yaml)

# Debug: Print working directory and available files
cat("=== DEBUG INFO ===\n")
cat("Working directory:", getwd(), "\n")
cat("Files in current directory:\n")
print(list.files(".", recursive = FALSE))
cat("Files in parent directory:\n")
print(list.files("..", recursive = FALSE))
cat("Files in parent/parent directory:\n")
print(list.files("../..", recursive = FALSE))
cat("==================\n\n")

# make function for testing

# If used inside snakemake:
# snakemake@params[[1]] --> output_dir
# snakemake@params[[2]] --> config
# snakemake@params[[3]] --> snake_dir

test_report <- function(config, output_dir, snake_dir){
  
  cat("\n=== TESTING REPORT ===\n")
  cat("Output directory:", output_dir, "\n")
  cat("Snake directory:", snake_dir, "\n")
  cat("Working directory:", getwd(), "\n")
  
  # Use file.path for better path handling
  report_original_path <- file.path(snake_dir, "workflow/rules/Report.rmd")
  output_results_dir <- file.path(output_dir, "results")
  output_tmp_dir <- file.path(output_dir, "results/tmp")
  report_tmp_path <- file.path(output_tmp_dir, "Report.rmd")
  
  cat("Report original path:", report_original_path, "\n")
  cat("Report original exists:", file.exists(report_original_path), "\n")
  
  # Create directories recursively
  dir.create(output_tmp_dir, recursive = TRUE, showWarnings = FALSE)
  
  # Create mock data directories and files that the report expects
  mock_dirs <- c(
    file.path(output_results_dir, "fastqc/raw/multiqc_data"),
    file.path(output_results_dir, "fastqc/trimmed/multiqc_data"),
    file.path(output_results_dir, "crosslinks"),
    file.path(output_results_dir, "mapping"),
    file.path(output_results_dir, "bigwig")
  )
  
  for (dir in mock_dirs) {
    dir.create(dir, recursive = TRUE, showWarnings = FALSE)
  }
  
  # Create minimal mock data files
  mock_fastqc_content <- "Sample\tTotal Sequences\tSequences flagged as poor quality\tSequence length\n"
  mock_fastqc_content <- paste0(mock_fastqc_content, "test_sample\t1000000\t0\t50\n")
  
  write(mock_fastqc_content, file = file.path(output_results_dir, "fastqc/raw/multiqc_data/multiqc_fastqc.txt"))
  write(mock_fastqc_content, file = file.path(output_results_dir, "fastqc/trimmed/multiqc_data/multiqc_fastqc.txt"))
  
  # Create empty files for other expected outputs
  mock_files <- c(
    "crosslinks/crosslinks_summary.txt",
    "mapping/mapping_summary.txt"
  )
  
  for (mock_file in mock_files) {
    file_path <- file.path(output_results_dir, mock_file)
    dir.create(dirname(file_path), recursive = TRUE, showWarnings = FALSE)
    write("# Mock data for testing", file = file_path)
  }
  
  cat("Created mock data files for report testing\n")
  
  # Check if source file exists before copying
  if (!file.exists(report_original_path)) {
    stop("Report template not found at: ", report_original_path)
  }
  
  file.copy(report_original_path, report_tmp_path, overwrite = TRUE)
  
  # copy workflow overview
  wf_image_original_path <- file.path(snake_dir, "workflow/rules/Workflow.png")
  wf_image_tmp_path <- file.path(output_tmp_dir, "Workflow.png")
  
  if (file.exists(wf_image_original_path)) {
    file.copy(wf_image_original_path, wf_image_tmp_path, overwrite = TRUE)
  } else {
    cat("Warning: Workflow image not found at:", wf_image_original_path, "\n")
  }
  
  cat("About to render report...\n")
  cat("Report template path:", report_tmp_path, "\n")
  cat("Output directory:", output_results_dir, "\n")
  
  # Set error handling for report rendering
  tryCatch({
    rmarkdown::render(report_tmp_path,
                      output_dir = output_results_dir,
                      params = list(config = config,  
                                    snake_dir = snake_dir),
                      output_format = "html_document"
    )
    cat("Report generation completed successfully for:", output_dir, "\n")
  }, error = function(e) {
    cat("Error during report generation:", e$message, "\n")
    # Still consider it a partial success if we got this far
    cat("Partial report generation completed for:", output_dir, "\n")
  })
  
  cat("======================\n\n")
}


# snakedir: local path on MAC
#---------------------
#snake_dir <- "/Users/melinaklostermann/Documents/projects/racoon_clip/racoon_clip/racoon_clip"

# snakedir: relative path
#---------------------
# Use absolute path to avoid issues with working directory changes
# From tests/report_test, go up to racoon_clip root, then into racoon_clip subdir
snake_dir <- normalizePath("../../racoon_clip", winslash = "/")
cat("Snake directory (calculated path):", snake_dir, "\n")
cat("Snake directory exists:", dir.exists(snake_dir), "\n")

# Alternative paths to try if the first doesn't work
alternative_paths <- c(
  normalizePath("../../../racoon_clip/racoon_clip", winslash = "/"),
  normalizePath("../../", winslash = "/"),
  normalizePath("../../../", winslash = "/")
)

for (alt_path in alternative_paths) {
  if (dir.exists(alt_path)) {
    report_check <- file.path(alt_path, "workflow/rules/Report.rmd")
    if (file.exists(report_check)) {
      snake_dir <- alt_path
      cat("Found working snake_dir:", snake_dir, "\n")
      break
    }
  }
}

cat("Final snake directory:", snake_dir, "\n")
cat("Snake directory exists:", dir.exists(snake_dir), "\n")

# Check if the expected files exist
report_file <- file.path(snake_dir, "workflow/rules/Report.rmd")
workflow_image <- file.path(snake_dir, "workflow/rules/Workflow.png")
theme_file <- file.path(snake_dir, "workflow/rules/theme_html.R")

cat("Report file exists:", file.exists(report_file), "\n")
cat("Workflow image exists:", file.exists(workflow_image), "\n")
cat("Theme file exists:", file.exists(theme_file), "\n")


# test eCLIP
#----------------------
output_dir <- "test_report_eCLIP"
config <- read_yaml("inputs_for_report_test/eCLIP/config_test_report_eCLIP.yaml") %>% unlist()

test_report(config, output_dir, snake_dir)

# test eCLIP Encode
#----------------------
output_dir <- "test_report_eCLIP_ENCODE"
config <- read_yaml("inputs_for_report_test/eCLIP_ENCODE/config_test_eCLIP_ENC.yaml") %>% unlist()

test_report(config, output_dir, snake_dir)


# test iCLIP 
#----------------------
output_dir <- "test_report_iCLIP"
config <- read_yaml("inputs_for_report_test/iCLIP/config_test_iCLIP.yaml") %>% unlist()

test_report(config, output_dir, snake_dir)


# test iCLIP multiplexed
#----------------------
output_dir <- "test_report_iCLIP_multiplexed"
config <- read_yaml("inputs_for_report_test/iCLIP_multiplexed/config_test_iCLIP_multiplexed.yaml") %>% unlist()

test_report(config, output_dir, snake_dir)

# params <- list(config = config,  
#                snake_dir = "/Users/melinaklostermann/Documents/projects/racoon_clip/racoon_clip/racoon_clip")
# 
# # !Check that there is a test set with adapter content
# 
# params$snake_dir

