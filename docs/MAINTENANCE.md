# Profile maintenance

Everything is static SVG + CSS: no JavaScript, no external services, Python standard library only.

## What updates itself

- **Activity** (`.github/workflows/activity.yml`): runs daily at 01:17 UTC. It fetches public contribution data, then rewrites `assets/activity-*.svg`, the 3D contribution skyline `assets/skyline-*.svg`, the four `assets/divider-*.svg` files and the refresh line in the README.
- **Education** (same workflow): reruns `scripts/build_record.py` so time enrolled and year of study stay current. A failure here never blocks the activity refresh.
- **Teach the Model** (`.github/workflows/teach.yml`): runs when someone opens an issue titled `teach|ROW|COL` from a board tile. It adds the point, retrains the network, rewrites the board between the TEACH markers, replies to the issue and closes it.

Both workflows declare their own write permissions, so the repository default can stay read-only. Keep **Issues** on (Settings > General > Features).

## Built by hand (rerun after editing)

| Script | Builds |
| --- | --- |
| `scripts/build_3d.py` | Extruded hero tagline, isometric Square One fort, rotating model globe in the Play panel |
| `scripts/build_buttons.py` | Keycap buttons in `assets/buttons/` (nav, demos, contact) |
| `scripts/render_activity.py` | Activity panel, skyline and dividers from `assets/activity.json` |
| `scripts/build_record.py` | About panel, Internship and Education panels, and the README block between the RECORD markers |

`build_3d.py` writes between `<!--3D:name-->` markers, so it is safe to run repeatedly. To change the tagline, edit `TAGLINE` and rerun it.

## Clickable rows

GitHub allows one link per image, so the About and Internship panels are cut into horizontal slices and each clickable row is its own image. The README gives every slice `align="top"`. That removes the baseline gap GitHub leaves under inline images, so the slices meet edge to edge. To change the record, the CGPA or the internship rows, edit the facts at the top of `build_record.py` and rerun it. The /4 CGPA is computed from the /10 figure.

## Performance rules

Animated panels must stay cheap, because GitHub renders every panel as an `<img>` and browsers redraw the whole image on each animation frame.

- Animate only `transform` and `opacity`. No filters, blur, masks or animated gradients.
- Prefer one animation per group over one per element. The globe spins 11 whole rings, each one dotted stroke, instead of animating ~200 dots; that cut its main-thread time by about 4x.
- Entrance animations run once and stop.
- Every panel honours `prefers-reduced-motion`.

## Reset the board

Delete `assets/teach/state.json`. The next move starts again from the four seed points.

## Theme

Every large section ships as `*-night.svg` (dark GitHub theme) and `*-day.svg` (light theme, inverted palette), switched with `<picture>` and `prefers-color-scheme`. Dividers and board tiles carry their own colours and work on both.

## Fonts

Display type is Archivo Black (SIL Open Font License 1.1), subset to capitals, digits and punctuation, embedded as base64 in each SVG. `assets/fonts/display-metrics.json` holds glyph advances so the renderers can size text.

## Local checks

    python -m unittest discover -s scripts -p 'test_*.py'
    python scripts/update_activity.py --offline
    python scripts/build_3d.py
    python scripts/build_buttons.py
    python scripts/build_record.py
