import unittest

from commands import parse_mission
from navigation import choose_escape_step, nearest_open_cell, plan_path


class PlanPathTests(unittest.TestCase):
    def test_finds_shortest_route_around_obstacle(self):
        blocked = {(1, 0), (1, 1)}
        path = plan_path((0, 1), (2, 1), 3, 3, blocked)

        self.assertIsNotNone(path)
        assert path is not None
        self.assertEqual(len(path) - 1, 4)
        self.assertEqual(path[0], (0, 1))
        self.assertEqual(path[-1], (2, 1))
        self.assertTrue(all(cell not in blocked for cell in path))

    def test_returns_none_when_goal_is_unreachable(self):
        blocked = {(1, 0), (1, 1), (1, 2)}

        self.assertIsNone(plan_path((0, 1), (2, 1), 3, 3, blocked))

    def test_rejects_blocked_start_or_goal(self):
        with self.assertRaisesRegex(ValueError, "start is blocked"):
            plan_path((0, 0), (1, 1), 2, 2, {(0, 0)})
        with self.assertRaisesRegex(ValueError, "goal is blocked"):
            plan_path((0, 0), (1, 1), 2, 2, {(1, 1)})


class ChooseEscapeStepTests(unittest.TestCase):
    def test_moves_to_a_safer_open_neighbor(self):
        next_cell = choose_escape_step((1, 1), (0.0, 1.0), 3, 3, set())

        self.assertEqual(next_cell, (2, 1))

    def test_stays_put_when_all_neighbors_are_blocked(self):
        blocked = {(0, 1), (2, 1), (1, 0), (1, 2)}

        self.assertEqual(
            choose_escape_step((1, 1), (0.0, 1.0), 3, 3, blocked),
            (1, 1),
        )

    def test_finds_nearest_open_cell_for_target_chase(self):
        self.assertEqual(
            nearest_open_cell((1, 1), 3, 3, {(1, 1)}),
            (0, 1),
        )

    def test_returns_none_when_grid_has_no_open_cells(self):
        self.assertIsNone(nearest_open_cell((0, 0), 1, 1, {(0, 0)}))


class ParseMissionTests(unittest.TestCase):
    def test_understands_find_red_object_command(self):
        self.assertEqual(parse_mission("AURA, find the red object"), "find_red")
        self.assertEqual(parse_mission("find the red target"), "find_red")

    def test_understands_tag_red_object_command(self):
        self.assertEqual(parse_mission("AURA, tag the red object"), "tag_red")

    def test_rejects_unsupported_commands(self):
        self.assertIsNone(parse_mission("follow me"))


if __name__ == "__main__":
    unittest.main()
