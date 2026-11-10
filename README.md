# Empire of the Ants – interactive maps

Interactive maps for every level of *Empire of the Ants* (Microids / Tower Five, 2024): nests, foraging spots,
resources, creatures, golden beetles, butterflies, lost sisters, quest givers, checkpoints and scans, all extracted
from the game files. Open **`index.html`**, pick a map, and click a marker for its icon, screenshot, text and details.

**Live:** https://lindblum.github.io/empire-of-the-ants-maps/

> Fan-made and unofficial. Game assets (icons, screenshots, minimaps, text) belong to Microids and Tower Five.
> Leaflet 1.9.4 loads from the unpkg CDN, so viewing needs internet access.

## Contents
| Path | What |
|---|---|
| `index.html`, `maps/<level>.html` | Map index and one Leaflet map per level (60) |
| `maps/assets/` | Icons, screenshots, minimap and terrain backgrounds |
| `data/markers.csv` | Every marker: level, category, title, world x/y/z (cm), map x/y, details, description |
| `data/levels.csv` | Per level: name, group, background type, alignment note, marker counts |
| `data/EotA_Missions.xlsx`, `data/EotA_Creatures.xlsx` | Missions (objectives, clans, setup) and the 46 creatures (stats, powers, levels) |
| `steam-guide/` | Steam guide text, images and `make_images.py` |

## Backgrounds
- **In-game minimap** (35 levels), aligned via the minimap camera and ortho width, with an automatic
  rotation/scale/mirror fit where a level reuses or rotates another level's render. The fit and its score are shown in
  each map's sidebar. `H1M3E3_TutorialStrategic` and `H1M4E3_TutorialCombat` are approximate.
- **Territory regions only** (`HMM4_Strategic`, `HCoopM1`, `HCoopM2`, `HCoop_Horde2`): the game has no rendered
  minimap, so the region map is drawn translucent.
- **Terrain relief + grid** (18 levels with no minimap, toggle top right):
  - 14 come from the stitched Landscape heightmaps of the level's `*_Terrain` sublevel. Overlapping landscapes are
    drawn largest first, and the backdrop is dimmed.
  - The 4 cave levels are rendered from the placed ground meshes. Only upward-facing surfaces up to 3 m above the
    nearest marker are kept, so cave roofs drop out.

## How it's built
The pipeline lives in the companion modding project `empire-of-the-ants-mod-spiders`, which is not published:
1. **Extract:** a small .NET 8 exporter on CUE4Parse 1.2.2 (UE 5.4.2, unversioned properties, so a `.usmap` from
   UE4SS is needed, converted v4 → v3). It dumps level JSON, UI sprites, terrain heightmaps (`--tex-only Heightmap`)
   and cave meshes (`--geo`).
2. **Process:** `extract_levels.py` collects actors and positions per level, incl. sublevels.
3. **Build:** `build_leaflet.py --all` writes this folder. Helpers: `map_common.py` (categories, minimap fit),
   `terrain.py` (heightmaps), `meshrelief.py` (caves).
4. **Tables:** `build_xlsx.py`, `build_creatures.py`.

Notes for anyone repeating this:
- Unversioned serialization omits default values, so a nest without `Clan` belongs to the player (Alpha), and a
  foraging spot without `ForagingType` is Food.
- HUD minimap sprites are channel-packed masks (R = fill, G = detail, B = outline). They are rendered white with
  black detail.
- Text comes from `TextData/Empire_Localization.txt`. Mission data comes from `BP_MissionDatabase` and each level's
  `BP_MissionLevel`.

## Limitations
- Positions are as placed at level start. Scripted spawns and patrol routes are not shown, and ambient creatures
  appear at their spawner.
- Cave reliefs flatten stacked passages into one layer.
- `H3M6E4_TacticCave` has only two markers, so its map covers a small area.
