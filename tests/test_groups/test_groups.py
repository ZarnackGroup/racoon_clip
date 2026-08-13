import tempfile
import unittest
from pathlib import Path

from racoon_clip.group_handling import resolve_groups


EXPERIMENT_TYPES = ("eCLIP", "miReCLIP")
SAMPLES = ["sample_a", "sample_b", "sample_c"]


class TestGroupHandling(unittest.TestCase):
    def resolve(self, content):
        if content is None:
            return resolve_groups(SAMPLES)
        with tempfile.TemporaryDirectory() as directory:
            group_file = Path(directory) / "groups.txt"
            group_file.write_text(content)
            return resolve_groups(SAMPLES, group_file)

    def assert_for_both_experiment_types(self, content, expected):
        for experiment_type in EXPERIMENT_TYPES:
            with self.subTest(experiment_type=experiment_type):
                self.assertEqual(dict(self.resolve(content)), expected)

    def test_no_groups_merges_all_samples(self):
        self.assert_for_both_experiment_types(
            None,
            {"all_samples": SAMPLES},
        )

    def test_complete_multi_sample_groups(self):
        self.assert_for_both_experiment_types(
            "group_1 sample_a\ngroup_1 sample_b\ngroup_1 sample_c\n",
            {
                "group_1": ["sample_a", "sample_b", "sample_c"],
            },
        )

    def test_singleton_group_is_preserved(self):
        self.assert_for_both_experiment_types(
            "group_1 sample_a\ngroup_1 sample_b\nsingleton sample_c\n",
            {
                "group_1": ["sample_a", "sample_b"],
                "singleton": ["sample_c"],
            },
        )

    def test_unassigned_samples_become_singleton_groups(self):
        self.assert_for_both_experiment_types(
            "group_1 sample_a\ngroup_1 sample_b\n",
            {
                "group_1": ["sample_a", "sample_b"],
                "sample_c": ["sample_c"],
            },
        )

    def test_sample_can_belong_to_multiple_groups(self):
        self.assert_for_both_experiment_types(
            "group_1 sample_a\ngroup_1 sample_b\ngroup_2 sample_a\ngroup_2 sample_c\n",
            {
                "group_1": ["sample_a", "sample_b"],
                "group_2": ["sample_a", "sample_c"],
            },
        )

    def test_mixed_execution_scenario(self):
        self.assert_for_both_experiment_types(
            "multi sample_a\nmulti sample_b\nsingleton sample_a\n",
            {
                "multi": ["sample_a", "sample_b"],
                "singleton": ["sample_a"],
                "sample_c": ["sample_c"],
            },
        )

    def test_unknown_sample_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown sample"):
            self.resolve("group_1 unknown_sample\n")


if __name__ == "__main__":
    unittest.main()
