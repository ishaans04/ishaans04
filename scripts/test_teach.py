"""Checks for the Teach the Model engine."""
import unittest
from teach import COLS, ROWS, SEED, fresh_state, play, render, tile, train


class TeachRules(unittest.TestCase):
    def test_seed_points_are_learned(self):
        preds, loss = train(SEED)
        self.assertEqual(len(preds), COLS * ROWS)
        for p in SEED:
            self.assertEqual(1 if preds[p['r'] * COLS + p['c']] >= 0.5 else 0, p['label'])
        self.assertLess(loss, 0.1)

    def test_training_is_deterministic(self):
        self.assertEqual(train(SEED), train(SEED))

    def test_labels_alternate_and_relabel(self):
        state = fresh_state()
        play(state, 'a', 0, 0)
        self.assertEqual(state['next'], 0)
        play(state, 'b', 0, 0)
        cell = [q for q in state['points'] if q['r'] == 0 and q['c'] == 0]
        self.assertEqual(len(cell), 1)
        self.assertEqual(cell[0]['label'], 0)
        self.assertEqual(tile(state, 0)[0], 'n')

    def test_render_has_every_tile(self):
        block = render(fresh_state())
        self.assertEqual(block.count('<img src="assets/teach/p') + block.count('<img src="assets/teach/l'), COLS * ROWS)


if __name__ == '__main__':
    unittest.main()
