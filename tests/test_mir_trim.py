import gzip
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "racoon_clip/workflow/scripts/trim_mir_from_chimeric_reads.py"
SPEC = importlib.util.spec_from_file_location("trim_mir", SCRIPT)
trim_mir = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trim_mir)


class TestCanonicalMirnaCoordinates(unittest.TestCase):
    def test_complete_canonical_mirna(self):
        self.assertEqual(trim_mir.canonical_coordinates(3, "21M", 23, 2), (1, 0, 24))

    def test_missing_first_two_mirna_bases(self):
        self.assertEqual(trim_mir.canonical_coordinates(5, "19M", 23, 2), (1, 2, 22))

    def test_leading_bases_after_bowtie_trimming(self):
        self.assertEqual(trim_mir.canonical_coordinates(1, "2S21M", 23, 2), (5, 0, 28))

    def test_query_insertion_changes_target_start(self):
        self.assertEqual(trim_mir.canonical_coordinates(3, "10M1I11M", 23, 2), (1, 0, 25))

    def test_reference_deletion_changes_target_start(self):
        self.assertEqual(trim_mir.canonical_coordinates(3, "10M1D10M", 23, 2), (1, 0, 23))

    def test_only_forward_primary_sam_alignment_is_used(self):
        with tempfile.TemporaryDirectory() as directory:
            sam = Path(directory) / "alignments.sam"
            sam.write_text(
                "forward\t0\tmir-1\t3\t42\t21M\t*\t0\t0\t" + "A" * 21 + "\t" + "I" * 21 + "\n"
                "reverse\t16\tmir-1\t3\t42\t21M\t*\t0\t0\t" + "A" * 21 + "\t" + "I" * 21 + "\n"
                "secondary\t256\tmir-1\t3\t42\t21M\t*\t0\t0\t" + "A" * 21 + "\t" + "I" * 21 + "\n"
            )
            alignments = trim_mir.read_primary_alignments(sam, {"mir-1": 23}, 2)
            self.assertEqual(alignments, {"forward": ("mir-1", 0, 1, 24)})

    def test_fastq_is_trimmed_at_canonical_end(self):
        with tempfile.TemporaryDirectory() as directory:
            fastq = Path(directory) / "reads.fastq"
            output = Path(directory) / "trimmed.fastq.gz"
            fastq.write_text("@read1 description\n" + "A" * 23 + "TARGET\n+\n" + "I" * 29 + "\n")
            counts = trim_mir.trim_fastq(
                fastq,
                output,
                {"read1": ("mir-1", 2, 1, 24)},
                {1},
                {0, 1, 2, 3},
            )
            with gzip.open(output, "rt") as handle:
                records = handle.read()
            self.assertEqual(counts["written"], 1)
            self.assertEqual(records, "@mir-1_read1 description\nTARGET\n+\nIIIIII\n")


if __name__ == "__main__":
    unittest.main()
