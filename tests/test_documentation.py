import ast
import re
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).parents[1]
DOCS_DIR = REPOSITORY_ROOT / "docs"


class TestDocumentationConsistency(unittest.TestCase):
    def test_navigation_pages_exist(self):
        expected_pages = [
            "installation",
            "tutorial",
            "examples",
            "tutorial_customise",
            "sample_groups",
            "tutorial_mir",
            "tutorial_container",
            "cluster_execution",
            "all_options",
            "tutorial_output",
            "methods_description",
            "troubleshooting",
            "updates",
            "citations",
        ]

        for page in expected_pages:
            self.assertTrue((DOCS_DIR / f"{page}.rst").is_file(), page)

        index = (DOCS_DIR / "index.rst").read_text()
        for page in expected_pages:
            self.assertRegex(index, rf"(?m)^\s+{re.escape(page)}\s*$")

        positions = [index.index(f"   {page}\n") for page in expected_pages]
        self.assertEqual(positions, sorted(positions))

    def test_supported_experiment_types_are_documented(self):
        util_tree = ast.parse(
            (REPOSITORY_ROOT / "racoon_clip" / "util.py").read_text()
        )
        assignment = next(
            node
            for node in util_tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name)
                and target.id == "EXPERIMENT_TYPES"
                for target in node.targets
            )
        )
        experiment_types = ast.literal_eval(assignment.value)
        guide = (DOCS_DIR / "tutorial_customise.rst").read_text()

        for experiment_type in experiment_types:
            self.assertIn(f"``{experiment_type}``", guide)

    def test_config_keys_are_covered_by_parameter_reference(self):
        config_text = (
            REPOSITORY_ROOT / "racoon_clip" / "config" / "config.yaml"
        ).read_text()
        keys = set(re.findall(
            r"^([A-Za-z_][A-Za-z0-9_]*):", config_text, flags=re.MULTILINE
        ))

        main_tree = ast.parse(
            (REPOSITORY_ROOT / "racoon_clip" / "__main__.py").read_text()
        )
        create_config_dicts = next(
            node
            for node in main_tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "create_config_dicts"
        )
        for node in ast.walk(create_config_dicts):
            if not isinstance(node, ast.Dict):
                continue
            keys.update(
                key.value
                for key in node.keys
                if isinstance(key, ast.Constant) and isinstance(key.value, str)
            )

        keys -= {"log", "snakebase", "workflow_type"}
        reference = (DOCS_DIR / "all_options.rst").read_text()

        for key in sorted(keys):
            documented = (
                f"**{key}**" in reference
                or f"``{key}``" in reference
                or f"**{key}:" in reference
            )
            self.assertTrue(documented, f"Missing parameter documentation: {key}")

    def test_local_images_exist(self):
        directive = re.compile(r"^\.\. (?:image|figure)::\s+(.+)$")
        for rst_file in DOCS_DIR.glob("*.rst"):
            for line in rst_file.read_text().splitlines():
                match = directive.match(line)
                if not match:
                    continue
                image_path = (rst_file.parent / match.group(1)).resolve()
                self.assertTrue(
                    image_path.is_file(),
                    f"{rst_file.name} references missing image {match.group(1)}",
                )

    def test_doc_targets_exist(self):
        doc_role = re.compile(r":doc:`(?:[^`<>]+<)?([^`<>]+)>?`")
        for rst_file in DOCS_DIR.glob("*.rst"):
            for target in doc_role.findall(rst_file.read_text()):
                target_path = target.strip().split("#", 1)[0]
                if target_path.startswith("/"):
                    target_path = target_path[1:]
                self.assertTrue(
                    (DOCS_DIR / f"{target_path}.rst").is_file(),
                    f"{rst_file.name} references missing document {target}",
                )

    def test_heading_underlines_are_long_enough(self):
        adornment = re.compile(r"^([=\-^])\1*$")
        for rst_file in DOCS_DIR.glob("*.rst"):
            lines = rst_file.read_text().splitlines()
            for line_number, (title, underline) in enumerate(
                zip(lines, lines[1:]), 1
            ):
                if not adornment.fullmatch(underline):
                    continue
                self.assertGreaterEqual(
                    len(underline),
                    len(title),
                    f"{rst_file.name}:{line_number} has a short heading underline",
                )

    def test_review_gated_invalid_cli_spellings_do_not_spread(self):
        gated_spellings = {
            "--experiment_type": 3,
            "--genome_fasta": 3,
            "--adapter_file": 2,
            "--barcodes_fasta": 1,
        }
        sources = "\n".join(
            path.read_text()
            for path in [REPOSITORY_ROOT / "README.md", *DOCS_DIR.glob("*.rst")]
        )
        for spelling, expected_count in gated_spellings.items():
            self.assertEqual(
                sources.count(spelling),
                expected_count,
                f"Unexpected occurrence count for review-gated {spelling}",
            )


if __name__ == "__main__":
    unittest.main()
