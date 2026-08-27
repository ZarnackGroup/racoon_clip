import ast
import unittest
from pathlib import Path
from racoon_clip.star_handling import (
    generated_star_index_paths,
    star_annotation_arguments,
)


class TestStarHandling(unittest.TestCase):
    def test_gtf_cli_option_is_optional_and_defaults_to_empty(self):
        main_path = Path(__file__).parents[1] / "racoon_clip" / "__main__.py"
        tree = ast.parse(main_path.read_text())
        gtf_option = next(
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and any(
                isinstance(arg, ast.Constant) and arg.value == "--gtf"
                for arg in node.args
            )
        )
        keywords = {keyword.arg: keyword.value
                    for keyword in gtf_option.keywords}
        required = ast.literal_eval(keywords["required"]) \
            if "required" in keywords else False
        self.assertFalse(required)
        self.assertEqual(ast.literal_eval(keywords["default"]), "")

    def test_annotation_arguments_are_empty_without_gtf(self):
        self.assertEqual(star_annotation_arguments("", 44), "")
        self.assertEqual(star_annotation_arguments(None, 44), "")

    def test_annotation_arguments_include_gtf_and_overhang(self):
        self.assertEqual(
            star_annotation_arguments("annotation file.gtf", 44),
            "--sjdbGTFfile 'annotation file.gtf' --sjdbOverhang 44",
        )

    def test_generated_index_uses_gtf_when_available(self):
        self.assertEqual(
            generated_star_index_paths("genome.gtf", "genome.fa"),
            ("genome_idx/", "genome_idx.chpnt"),
        )

    def test_generated_index_uses_fasta_without_gtf(self):
        self.assertEqual(
            generated_star_index_paths("", "genome.fa"),
            ("genome_idx/", "genome_idx.chpnt"),
        )


if __name__ == "__main__":
    unittest.main()
