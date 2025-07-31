#!bash

rm -R /home/mek24iv/racoon_devel/racoon_clip/tests/test_workflow/expected_output/out_eCLIP_ENCODE/results
racoon_clip run --cores 6 --configfile /home/mek24iv/racoon_devel/racoon_clip/example_data/example_eCLIP_ENCODE/config_test_eCLIP_ENC.yaml

# rm -R /home/mklostermann/projects/04_minimal_examples_racoon/test_eCLIP/results
# racoon_clip run --cores 6 --configfile /home/mklostermann/projects/04_minimal_examples_racoon/test_eCLIP/config_test_eCLIP.yaml

# rm -R /home/mklostermann/projects/04_minimal_examples_racoon/test_iCLIP
# racoon_clip run --cores 6 --configfile /home/mklostermann/projects/04_minimal_examples_racoon/test_iCLIP/config_test_iCLIP.yaml

# rm -R /home/mklostermann/projects/04_minimal_examples_racoon/test_iCLIP_multiplexed
# racoon_clip run --cores 6 --configfile /home/mklostermann/projects/04_minimal_examples_racoon/test_iCLIP_multiplexed/config_test_iCLIP_multiplexed.yaml