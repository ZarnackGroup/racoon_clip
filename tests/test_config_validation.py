import unittest

from racoon_clip.util import EXPERIMENT_TYPES, validate_user_config


SUPPORTED_KEYS = {
    "experiment_type",
    "demultiplex",
    "mir_genome_fasta",
    "quality_filter_barcodes",
}


class TestConfigValidation(unittest.TestCase):
    def test_unknown_config_keys_include_suggestions(self):
        config = {
            "experoment_type": "miReCLIP",
            "demuliplexing": False,
            "miR_genome_fasta": "mir.fa",
            "miR": True,
        }

        with self.assertRaises(ValueError) as error:
            validate_user_config(config, SUPPORTED_KEYS)

        message = str(error.exception)
        self.assertIn(
            "Unknown parameter 'experoment_type'. Did you mean 'experiment_type'?",
            message,
        )
        self.assertIn(
            "Unknown parameter 'demuliplexing'. Did you mean 'demultiplex'?",
            message,
        )
        self.assertIn(
            "Unknown parameter 'miR_genome_fasta'. Did you mean 'mir_genome_fasta'?",
            message,
        )
        self.assertIn("Unknown parameter 'miR'.", message)

    def test_invalid_experiment_type_lists_choices_and_suggests_match(self):
        with self.assertRaises(ValueError) as error:
            validate_user_config({"experiment_type": "mereCLIP"}, SUPPORTED_KEYS)

        message = str(error.exception)
        self.assertIn(
            "Unknown experiment_type 'mereCLIP'. Did you mean 'miReCLIP'?",
            message,
        )
        self.assertIn("Available values:", message)
        for choice in EXPERIMENT_TYPES:
            self.assertIn(choice, message)

    def test_legacy_input_parameters_explain_infiles_replacement(self):
        with self.assertRaises(ValueError) as error:
            validate_user_config(
                {"infile": "reads.fastq", "indir": "/reads"},
                SUPPORTED_KEYS | {"infiles"},
            )

        message = str(error.exception)
        self.assertIn("Unknown parameter 'infile'. Use 'infiles' instead.", message)
        self.assertIn(
            "Unknown parameter 'indir'. Use 'infiles' with a glob pattern",
            message,
        )

    def test_experiment_type_is_case_insensitive_like_cli(self):
        config = {"experiment_type": "mireclip"}

        validate_user_config(config, SUPPORTED_KEYS)

        self.assertEqual(config["experiment_type"], "miReCLIP")


if __name__ == "__main__":
    unittest.main()
