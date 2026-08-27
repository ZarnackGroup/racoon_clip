import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = (
    Path(__file__).parents[1]
    / "racoon_clip/workflow/scripts/prepare_pureclip_genome.py"
)
SPEC = importlib.util.spec_from_file_location("prepare_pureclip_genome", SCRIPT)
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


class TestPreparePureclipGenome(unittest.TestCase):
    def paths(self, directory):
        directory = Path(directory)
        return (
            directory / "genome.fa",
            directory / "genome_no_extended_iupac_u_to_t.fa",
            directory / "results/tmp/genome_no_extended_iupac_u_to_t.fa",
            directory / "results/peaks/pureclip_genome_compatibility.txt",
        )

    def test_clean_fasta_uses_original_without_creating_a_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            source, preferred, fallback, status = self.paths(directory)
            source.write_text(">chr1 description\nACGTN\nacgtn\n")

            selected, symbols, has_uracil = prepare.prepare_pureclip_genome(
                source, preferred, fallback, status
            )

            self.assertEqual(selected, source.resolve())
            self.assertEqual(symbols, set())
            self.assertFalse(has_uracil)
            self.assertFalse(preferred.exists())
            self.assertFalse(fallback.exists())
            self.assertIn(f"GenomePath\t{source.resolve()}", status.read_text())

    def test_extended_symbols_and_uracil_are_changed_beside_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source, preferred, fallback, status = self.paths(directory)
            source.write_text(">chrY extended header\nACGYRDU\nacgtdu\n")

            selected, symbols, has_uracil = prepare.prepare_pureclip_genome(
                source, preferred, fallback, status
            )

            self.assertEqual(selected, preferred.resolve())
            self.assertEqual(symbols, {"D", "R", "Y", "d"})
            self.assertTrue(has_uracil)
            self.assertEqual(
                preferred.read_text(), ">chrY extended header\nACGNNNT\nacgtNt\n"
            )
            self.assertIn("ExtendedIupacToN\ttrue", status.read_text())
            self.assertIn("UracilToT\ttrue", status.read_text())

    def test_existing_compatible_fasta_is_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            source, preferred, fallback, status = self.paths(directory)
            source.write_text(">chr1\nAUY\n")
            preferred.write_text(">existing\nATT\n")

            selected, _, _ = prepare.prepare_pureclip_genome(
                source, preferred, fallback, status
            )

            self.assertEqual(selected, preferred.resolve())
            self.assertEqual(preferred.read_text(), ">existing\nATT\n")
            self.assertFalse(fallback.exists())

    def test_unwritable_source_directory_uses_temporary_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            source, preferred, fallback, status = self.paths(directory)
            source.write_text(">chr1\nAUY\n")

            with mock.patch.object(prepare.os, "access", return_value=False):
                selected, _, _ = prepare.prepare_pureclip_genome(
                    source, preferred, fallback, status
                )

            self.assertEqual(selected, fallback.resolve())
            self.assertEqual(fallback.read_text(), ">chr1\nATN\n")
            self.assertFalse(preferred.exists())


if __name__ == "__main__":
    unittest.main()
