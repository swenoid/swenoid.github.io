# Swenoid website

Static project website for `https://swenoid.github.io/` and the
`swenoid/swenoid.github.io` repository. The 3D viewer bundle is included locally; there is no tracking,
third-party embed, or required build step.

## Local preview

Run `npm run dev` and open <http://localhost:4173>. The server listens only on
this computer and supports video seeking. Use `SWENOID_PORT=4174 npm run dev`
to choose another port.

Run `npm run check` to validate JavaScript, local links, media coverage, and
the five-stage comparison.

## Content and video playback

The site introduces the hardware, simulation workflow, and demonstrations
directly. The video section shows five individual demonstrations and one
five-stage wave comparison. A separate Gallery groups the push-up video with
three photographs. The comparison contains SMPL, reshaped SMPL,
kinematically retargeted Swenoid, a policy in Isaac Gym, and hardware.

The five wave recordings are encoded into one video with one playback clock.
Play, pause, seek, and loop therefore keep all stages together. Each source
recording is uniformly retimed to the shared 3.6-second cycle. The source
recordings are preserved in `assets/videos`; playback rates and source durations
are documented in `wave-comparison.json`.

All five panels have the same height with 24-pixel gaps, preserving each clip’s
aspect ratio. Desktop uses one row; phones use a three-plus-two layout. Switching layouts
preserves the playback position and pause state. Native inline players show the
complete frame, organized under Motion tracking, Locomotion, and Drawing.
Each group has one heading; individual players have no visible labels or descriptions. Videos request
no preload and do not autoplay. `video-index.html` provides the same gallery
without JavaScript. A copyable BibTeX citation appears at the bottom of the page.

`wave-comparison.json` records the source clips, durations and playback rates.
To rebuild both layouts, install ffmpeg and ImageMagick, then run:

```sh
python3 scripts/build-wave-comparison.py
python3 scripts/build-video-index.py
```

## 3D simulation model

The viewer sits below the specifications near the top of the page. It supports
mouse, touch and keyboard rotation, zoom, and reset. The model and the pinned
`@google/model-viewer` 4.4.0 bundle are served locally; the viewer loads as it
approaches the viewport. A still image remains available without JavaScript.
Upstream bundle licenses are in `assets/vendor/model-viewer/`.

`assets/models/swenoid.glb` contains the 91 visual meshes from the prepared
MuJoCo model, with the physical material colors and repaired left shoulder motor
used in the figure. It is a static 3D view, without a physics simulation.
`assets/models/swenoid.json` records the source commit, pose, bounds and checksum.

To rebuild from the prepared figure scene, install mujoco, numpy and trimesh,
then run:

```sh
python3 scripts/export-simulation-model.py /path/to/render-scene.xml /path/to/render-provenance.json
```

The input scene references the original visual meshes and material partitions.
The exporter preserves their geometry and does not edit the simulation source.

## Media sources

`media.json` lists the 11 selected recordings. Additional locomotion, walking
development, and wave development footage are omitted from both galleries.
`media-provenance.json` records the source snapshot, full original inventory,
the excluded recordings, and the author-supplied drawing replacement. The drawing
player uses `IMG_4474.MOV`, converted at full length to portrait H.264/AAC with
BT.709 tone mapping for consistent SDR playback. The imported source files are preserved.
The original personal website is not modified or used as a deployment target.
Original assets retain their ownership and attribution; AMASS is credited for
the human motion source.

To regenerate browser media from a separate source snapshot, install ffmpeg
and cwebp and run `python3 scripts/import-media.py /path/to/personal-site-snapshot`.
The importer preserves the author-supplied drawing replacement.

The hardware illustration uses `attachments-transparent.webp`, with a transparent
background. Its original asset remains alongside it.

## Publishing after review

The site can serve directly from `main` / root with GitHub Pages. `.nojekyll`
disables Jekyll. Local preview does not push, publish, or enable Pages.
