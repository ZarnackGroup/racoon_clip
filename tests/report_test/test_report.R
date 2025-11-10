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
  
  # Track success status
  report_success <- FALSE
  
  # Use file.path for better path handling
  report_original_path <- file.path(snake_dir, "workflow/rules/Report.rmd")
  output_results_dir <- file.path(output_dir, "results")
  output_tmp_dir <- file.path(output_dir, "results/tmp")
  # Copy Report.rmd to results/ directory, not tmp/, so working directory is correct
  report_tmp_path <- file.path(output_results_dir, "Report.rmd")
  
  cat("Report original path:", report_original_path, "\n")
  cat("Report original exists:", file.exists(report_original_path), "\n")
  
  # Create directories recursively
  dir.create(output_tmp_dir, recursive = TRUE, showWarnings = FALSE)
  
  # Update config to have correct wdir path
  # Report.rmd expects wdir to point to the OUTPUT directory parent, then adds /results/
  # So if we're IN results/, we need wdir to be ".." to go: paste0("..", "/results/fastqc")
  config["wdir"] <- ".."
  
  # Check if source file exists before copying
  if (!file.exists(report_original_path)) {
    stop("Report template not found at: ", report_original_path)
  }
  
  file.copy(report_original_path, report_tmp_path, overwrite = TRUE)
  
  # copy workflow overview
  wf_image_original_path <- file.path(snake_dir, "workflow/rules/Workflow.png")
  # Copy workflow image to results/ directory to match Report.rmd location
  wf_image_tmp_path <- file.path(output_results_dir, "Workflow.png")
  
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
    report_success <- TRUE
  }, error = function(e) {
    cat("\n========================================\n")
    cat("ERROR during report generation\n")
    cat("========================================\n")
    cat("Error message:", e$message, "\n")
    if (!is.null(e$call)) {
      cat("Error call:", deparse(e$call), "\n")
    }
    # Print full error details
    cat("\nFull error object:\n")
    print(e)
    cat("\nTraceback:\n")
    print(traceback())
    cat("========================================\n")
    cat("FAILED: Report generation failed for:", output_dir, "\n")
    cat("========================================\n\n")
    report_success <- FALSE
  })
  
  cat("======================\n\n")
  
  # Return success status
  return(report_success)
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

# Track overall success
all_tests_passed <- TRUE

# test eCLIP
#----------------------
output_dir <- "test_report_eCLIP"
config <- read_yaml("inputs_for_report_test/eCLIP/config_test_report_eCLIP.yaml") %>% unlist()

success <- test_report(config, output_dir, snake_dir)
if (!success) all_tests_passed <- FALSE

# test eCLIP Encode
#----------------------
output_dir <- "test_report_eCLIP_ENCODE"
config <- read_yaml("inputs_for_report_test/eCLIP_ENCODE/config_test_eCLIP_ENC.yaml") %>% unlist()

success <- test_report(config, output_dir, snake_dir)
if (!success) all_tests_passed <- FALSE


# test iCLIP 
#----------------------
output_dir <- "test_report_iCLIP"
config <- read_yaml("inputs_for_report_test/iCLIP/config_test_iCLIP.yaml") %>% unlist()

success <- test_report(config, output_dir, snake_dir)
if (!success) all_tests_passed <- FALSE


# test iCLIP multiplexed
#----------------------
output_dir <- "test_report_iCLIP_multiplexed"
config <- read_yaml("inputs_for_report_test/iCLIP_multiplexed/config_test_iCLIP_multiplexed.yaml") %>% unlist()

success <- test_report(config, output_dir, snake_dir)
if (!success) all_tests_passed <- FALSE

# Exit with appropriate status code
if (!all_tests_passed) {
  cat("\n=== REPORT TESTS FAILED ===\n")
  quit(status = 1)
} else {
  cat("\n=== ALL REPORT TESTS PASSED ===\n")
  quit(status = 0)
}

# params <- list(config = config,  
#                snake_dir = "/Users/melinaklostermann/Documents/projects/racoon_clip/racoon_clip/racoon_clip")
# 
# # !Check that there is a test set with adapter content
# 
# params$snake_dir

