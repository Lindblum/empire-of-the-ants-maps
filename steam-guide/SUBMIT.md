# Steam guide: "Mission Maps"

Everything needed to publish the guide on the Empire of the Ants Steam community hub
(https://steamcommunity.com/app/2287330/guides/). The guide links to the hosted maps, so **host them first**.

## 0. Before you start
- [ ] Maps are online at `https://lindblum.github.io/empire-of-the-ants-maps/`, and a map page opens from that URL.
      If you host them elsewhere, replace that base URL throughout `guide-sections.txt`.
- [ ] Open one map in the Steam overlay browser (Shift+Tab in game) to check that it works there.

## 1. Create the guide
Community hub → Guides → **Create a Guide**.

| Field | Value |
|---|---|
| Title | `Mission Maps` |
| Description | `Interactive maps for every mission, hub, challenge, skirmish and co-op level: nests, foraging spots, golden beetles, butterflies, lost sisters, quest givers, scans and creatures, taken straight from the game files.` |
| Preview image | `images/guide-icon.png` (square, 512 × 512) |
| Category | **Maps or Levels** (also tick **Walkthroughs** and **Secrets or Easter Eggs** if this game's list offers them) |
| Language | English |

## 2. Upload the images
In the guide editor, upload these under "Images". Steam only shows images uploaded here, not external links.

| File | Use in section |
|---|---|
| `images/index.png` | Overview |
| `images/legend.png`, `images/H2M3E4_Strategic.png` | What's on the maps |
| `images/gallery_chapter-1.png` … `gallery_chapter-5.png` | Chapter 1 … Chapter 5 |
| `images/gallery_challenge-mode.png` | Challenge mode |
| `images/gallery_skirmish-multiplayer.png` | Skirmish & multiplayer |
| `images/gallery_co-op-horde.png` | Co-op & horde |
| `images/H2M0E0_Traversal.png`, `images/H5M1E1_Exploration.png` | Notes |

13 images in all, each under 1 MB. The galleries are regenerated from the built maps by
`python steam-guide/make_images.py` (run it again after a map rebuild).

## 3. Add the sections
`guide-sections.txt` holds 12 sections, separated by lines like
`==================== SECTION: Overview ====================`.
For each one: **Add Section**, type the title shown after `SECTION:`, and paste the text below the separator (not the separator itself).

Where a section has a line like `(IMAGE: index.png)`, delete it. Then put the cursor there and click the uploaded image's
**Add to section** button. Steam inserts its own `[previewimg=…]` tag; choose "Full size" or "Inline", whichever fits.

## 4. Preview and publish
- [ ] Preview: check the tables, lists and the spoiler block render, and click a few map links.
- [ ] Set visibility: start as **Friends only** or **Hidden** to check it, then **Public**.
- [ ] Submit. Public guides can take a little while to show in the hub list.

## Updating later
After a map rebuild, the links stay the same (one page per level file name), so the guide only needs editing if
levels are added or renamed. Re-run `make_images.py` and re-upload any gallery that changed. The section list in
"Contents" (Overview section) is plain text: Steam assigns section anchors only after publishing.
