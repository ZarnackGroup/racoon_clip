# -----------------
# test make report
# ------------------

# make function for testing

# If used inside snakemake:
# snakemake@params[[1]] --> output_dir
# snakemake@params[[2]] --> config
# snakemake@params[[3]] --> snake_dir

test_report <- function(config, output_dir, snake_dir){
  
  report_original_path <- paste0(snake_dir, "/workflow/rules/Report.rmd")
  dir.create(paste0(output_dir, "/results/tmp/"))
  report_tmp_path <- paste0(output_dir, "/results/tmp/Report.rmd")
  file.copy(report_original_path, report_tmp_path, overwrite = TRUE)
  
  # copy workflow overview
  wf_image_original_path <- paste0(snake_dir, "/workflow/rules/Workflow.png")
  wf_image_tmp_path <- paste0(output_dir, "/results/tmp/Workflow.png")
  file.copy(wf_image_original_path, wf_image_tmp_path, overwrite = TRUE)
  
  rmarkdown::render(report_tmp_path,
                    output_dir = paste0(output_dir, "/results/"),
                    params = list(config = config,  
                                  snake_dir = snake_dir),
                    output_format = "html_document"
  )
}


# local path on MAC
snake_dir <- "/Users/melinaklostermann/Documents/projects/racoon_clip/racoon_clip/racoon_clip"


# test eCLIP
output_dir <- "/Users/melinaklostermann/Documents/projects/racoon_clip/racoon_clip/tests/report_test/test_report_eCLIP"
config <- read_yaml("/Users/melinaklostermann/Documents/projects/racoon_clip/racoon_clip/tests/report_test/inputs_for_report_test/eCLIP/config_test_report_eCLIP.yaml") %>% unlist()


test_report(config, output_dir, snake_dir)


# !Check that there is a test set with adapter content



