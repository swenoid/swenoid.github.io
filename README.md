# Swenoid research website

Static research website prepared for `https://swenoid.github.io/` and the
`swenoid/swenoid.github.io` repository. It has no runtime dependencies, tracking,
third-party embeds, or build step.

## Local preview

Run `npm run dev` and open <http://localhost:4173>. No dependency installation is
needed. The preview server listens only on this computer and supports video seeking.
To use another port, run `SWENOID_PORT=4174 npm run dev`.

Run `npm run check` to check JavaScript syntax, local references, and media coverage.

## Content

The page follows the author-provided manuscript **Swenoid: An Open-Source and
Customizable Humanoid Robot**, by Martin Orrje, Arvid Eriksson, and David Broman.
Results that depend on the unavailable `results_macros.tex` are omitted. The
five completed dance trials and four falls are explicit in the supplied prose.
Commanded walking speeds are labeled as commands, not measured outcomes.

The PDF in the personal-site repository is an earlier manuscript with a different
title and abstract. It is not presented here as the current paper. Add the current
PDF and publication metadata when they are ready. The provisional citation uses
the supplied title and authors without inventing a venue, publication year, or DOI.

All 14 videos in the original personal-site snapshot are represented in
`media.json`, including footage not embedded in its HTML page. Earlier footage and
simulation clips are labeled separately from the paper's experiments. Videos are
local H.264/AAC MP4s with fast-start metadata; they load only when opened. The
gallery has keyboard-accessible filters, a native video dialog, downloads, and a
no-JavaScript fallback at `video-index.html`.

`media-provenance.json` records the read-only source snapshot and inventory.
The original personal website is not modified or used as a deployment target.
The robot portrait is an image extracted from the older paper; the surrounding
research text follows the newly supplied manuscript. Original assets retain their
existing ownership and attribution. Dataset demonstration videos are credited to
AMASS; the underlying motion dataset is not included.

To regenerate browser media from a separate source snapshot, install ffmpeg and cwebp and
run `python3 scripts/import-media.py /path/to/personal-site-snapshot`.

## Publishing after review

The site is ready to serve directly from the root of a `main` branch with GitHub
Pages. `.nojekyll` disables Jekyll processing. Review the local preview first;
publication requires a separate push and enabling Pages for `main` / root. No
GitHub Actions workflow or deployment is triggered by this local preview.
