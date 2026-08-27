import unittest
from unittest.mock import patch

from racoon_clip.input_handling import build_sample_file_map, resolve_infiles


class TestResolveInfiles(unittest.TestCase):
    @patch("racoon_clip.input_handling.os.access", return_value=True)
    @patch("racoon_clip.input_handling.os.path.isfile", return_value=True)
    @patch("racoon_clip.input_handling.glob.glob")
    def test_mixed_explicit_paths_and_globs(self, mock_glob, _isfile, _access):
        matches = {
            "run1/*.fastq.gz": ["run1/b.fastq.gz", "run1/a.fastq.gz"],
            "run2/sample?.fq.gz": ["run2/sample1.fq.gz"],
        }
        mock_glob.side_effect = matches.__getitem__

        result = resolve_infiles(
            "run1/*.fastq.gz explicit.fastq run2/sample?.fq.gz"
        )

        self.assertEqual(
            result,
            [
                "run1/a.fastq.gz",
                "run1/b.fastq.gz",
                "explicit.fastq",
                "run2/sample1.fq.gz",
            ],
        )

    @patch("racoon_clip.input_handling.os.access", return_value=True)
    @patch("racoon_clip.input_handling.os.path.isfile", return_value=True)
    @patch(
        "racoon_clip.input_handling.glob.glob",
        side_effect=[["a.fastq.gz", "b.fastq.gz"], ["b.fastq.gz"]],
    )
    def test_overlapping_patterns_are_deduplicated(self, _glob, _isfile, _access):
        result = resolve_infiles("*.fastq.gz b*.fastq.gz")

        self.assertEqual(result, ["a.fastq.gz", "b.fastq.gz"])

    def test_empty_input_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "'infiles' is empty"):
            resolve_infiles("")

    @patch("racoon_clip.input_handling.glob.glob", return_value=[])
    def test_unmatched_pattern_is_rejected(self, _glob):
        with self.assertRaisesRegex(ValueError, "No files found matching"):
            resolve_infiles("missing/*.fastq.gz")

    @patch("racoon_clip.input_handling.os.access", return_value=True)
    @patch("racoon_clip.input_handling.os.path.isfile", return_value=True)
    def test_invalid_extension_is_rejected(self, _isfile, _access):
        with self.assertRaisesRegex(ValueError, "Input files must end"):
            resolve_infiles("reads.fasta")

    @patch("racoon_clip.input_handling.os.access", return_value=True)
    @patch("racoon_clip.input_handling.os.path.isfile", return_value=True)
    def test_demultiplex_requires_exactly_one_file(self, _isfile, _access):
        with self.assertRaisesRegex(ValueError, "requires exactly one"):
            resolve_infiles("sample1.fastq sample2.fastq", demultiplex=True)


class TestSampleFileMap(unittest.TestCase):
    def test_files_from_different_directories_are_mapped_exactly(self):
        files = ["run1/sample1.fastq.gz", "run2/sample2.fq"]

        samples, mapping = build_sample_file_map(files)

        self.assertEqual(samples, ["sample1", "sample2"])
        self.assertEqual(
            mapping,
            {"sample1": "run1/sample1.fastq.gz", "sample2": "run2/sample2.fq"},
        )

    def test_duplicate_basenames_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "Multiple input files resolve"):
            build_sample_file_map(
                ["run1/sample.fastq.gz", "run2/sample.fastq.gz"]
            )

    def test_configured_sample_order_is_preserved(self):
        samples, mapping = build_sample_file_map(
            ["sample1.fastq", "sample2.fastq"],
            configured_samples="sample2 sample1",
        )

        self.assertEqual(samples, ["sample2", "sample1"])
        self.assertEqual(list(mapping), ["sample2", "sample1"])

    def test_unknown_configured_sample_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "no matching input file"):
            build_sample_file_map(
                ["sample1.fastq"],
                configured_samples="sample1 missing",
            )


if __name__ == "__main__":
    unittest.main()
