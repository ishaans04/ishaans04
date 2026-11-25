# Profile maintenance

## What updates itself

- **Activity** (`.github/workflows/activity.yml`): daily at 01:17 UTC. Fetches public contribution data, then rewrites `assets/activity-night.svg`, `assets/activity-day.svg`, the four `assets/divider-*.svg` files and the refresh line in the README.
- **Teach the Model** (`.github/workflows/teach.yml`): runs when someone opens an issue titled `teach|ROW|COL` from a board tile. It adds the point, retrains the network, rewrites the board between the TEACH markers, replies and closes the issue.

## Setup

1. Settings > General > Features: keep **Issues** on.
2. Settings > Actions > General > Workflow permissions: **Read and write permissions**.
3. Run the activity workflow once from the Actions tab.

## Reset the board

Delete `assets/teach/state.json`; the next move starts again from the four seed points.

## Theme

Every large section ships as `*-night.svg` (dark GitHub theme) and `*-day.svg` (light theme), switched with `<picture>` and `prefers-color-scheme`. Dividers and board tiles carry their own colours and work on both.

## Fonts

Display type is Archivo Black (SIL Open Font License 1.1), subset to capitals, digits and punctuation, embedded as base64 in each SVG. `assets/fonts/display-metrics.json` holds glyph advances so the Python renderer can size text.

## Local checks

    python -m unittest discover -s scripts -p 'test_*.py'
    python scripts/update_activity.py --offline
