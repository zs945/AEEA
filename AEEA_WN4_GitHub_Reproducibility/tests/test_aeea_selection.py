import unittest

from aeea_selection import (
    cap_agent_candidates,
    pareto_rank_and_crowding,
    pareto_select_elites,
    pareto_select_prompt_context,
)


class AeeaSelectionTest(unittest.TestCase):
    def setUp(self):
        self.population = ["left", "middle_a", "middle_b", "right", "dominated"]
        self.objectives = [
            [1.0, 4.0, 2.0],
            [2.0, 3.0, 2.0],
            [3.0, 2.0, 2.0],
            [4.0, 1.0, 2.0],
            [5.0, 5.0, 3.0],
        ]

    def test_nondomination_rank_precedes_crowding_distance(self):
        ranks, crowding = pareto_rank_and_crowding(self.objectives)
        self.assertEqual(ranks, [0, 0, 0, 0, 1])
        self.assertEqual(crowding[0], float("inf"))
        self.assertEqual(crowding[3], float("inf"))

    def test_elite_and_prompt_context_have_fixed_sizes(self):
        elites, _, elite_values = pareto_select_elites(
            self.population, self.objectives, elite_ratio=0.6
        )
        context, context_values = pareto_select_prompt_context(elites, elite_values)
        self.assertEqual(len(elites), 3)
        self.assertEqual(len(context), 1)
        self.assertEqual(len(context), len(context_values))

    def test_excess_agent_candidates_are_trimmed(self):
        selected, selected_values = cap_agent_candidates(
            self.population, self.objectives, target_count=3
        )
        self.assertEqual(len(selected), 3)
        self.assertNotIn("dominated", selected)
        self.assertEqual(len(selected), len(selected_values))

    def test_agent_shortfall_is_retained_for_ga_refill(self):
        selected, selected_values = cap_agent_candidates(
            self.population[:2], self.objectives[:2], target_count=3
        )
        self.assertEqual(selected, self.population[:2])
        self.assertEqual(selected_values, self.objectives[:2])


if __name__ == "__main__":
    unittest.main()
