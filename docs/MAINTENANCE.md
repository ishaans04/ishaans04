# Profile maintenance

The root README is the public profile. All visible artwork is served from this repository. SVG files contain their own CSS animations and embedded character images; they have no scripts, network requests, or external font dependencies. Motion is disabled when the reader prefers reduced motion. The dark panels intentionally retain their palette in either GitHub theme.

## Edit the profile

Edit `README.md` for project descriptions, links, or stack changes. Keep the four pinned projects first. Additional projects belong in the archive dropdown.

Edit `scripts/build_assets.py`, then run:

```sh
python scripts/build_assets.py
```

Character sources and attribution are in [the artwork notes](../assets/ARTWORK.md).

## Refresh activity

The workflow runs daily at 01:17 UTC (06:47 IST), or through **Actions → Refresh mission control → Run workflow**. It needs only the repository's built-in token, with `contents: write` permission. No personal access token or other secret is required.

For a local refresh with GitHub CLI authentication:

```sh
python scripts/update_activity.py
```

To rebuild the layout from the committed public dataset without fetching:

```sh
python scripts/update_activity.py --offline
```

- The calendar uses GitHub's own credited contribution calendar and date boundaries.
- Project rows cover the last 30 UTC contribution dates, including today; they show credited commits, not all branch pushes.
- Public collaborations retain their owner-qualified names. Same-named repositories are separate projects.
- Private repositories are filtered before data is saved. Profile maintenance commits are excluded from project rows and sampled commit times.
- The chart shows the six most active public repositories; the daily log includes all active public repositories returned by GitHub.
- The time-of-day view samples up to 100 author timestamps from each of the eight most active public repositories, over a 90-day lookback. Duplicate commit hashes are counted once. The highlighted window is the busiest consecutive three hours in IST within that sample.
- API errors or incomplete contribution pages fail the refresh before replacing the saved dashboard.

The refresh updates only `assets/activity.json`, `assets/activity.svg`, and the marked README activity block. An unchanged refresh creates no commit.

## Verify

The telemetry checks use only Python's standard library:

```sh
python -m unittest discover -s scripts -p 'test_*.py'
```

For visual review, install Playwright and have Microsoft Edge available, then run `python scripts/verify_profile.py`. It uses GitHub's Markdown renderer and saves desktop, light-theme, mobile, and individual-asset previews in the ignored `tmp/` directory. It checks SVG structure, image loading, text bounds, details/table rendering, and mobile page overflow.
