# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A LaTeX conversion of `Proposal Project1.docx` — a Thai-language Khon Kaen University computer science project
proposal (โครงงานทางวิทยาการคอมพิวเตอร์). The `.docx` is the original source document; `latex/` is a from-scratch
LaTeX rebuild of it, split into per-section files so content can be edited piece by piece.

## Build

```
cd latex
xelatex main.tex   # must use XeLaTeX (not pdflatex) — required for the Thai font + line breaking
```

Run twice if references/labels look stale. Output is `latex/main.pdf`.

To preview a specific page without opening a PDF viewer:
```
pdftoppm -png -r 150 -f <page> -l <page> main.pdf preview
```
(`pdftoppm` ships with the TeX Live install on this machine.) Delete preview PNGs and `main.aux`/`main.log`/`main.out`
after inspecting — they're scratch artifacts, not part of the repo content.

## Architecture

- `latex/main.tex` — preamble only (fonts, packages, heading/indent formatting) plus a flat list of `\input{}`
  calls. Never put document content directly in this file.
- `latex/sections/*.tex` — one file per numbered section of the proposal (`00-cover`, `00-proposal-id`,
  `01-title` … `11-references`, `99-signature`). To edit content (e.g. fill in budget numbers, fix a citation),
  edit the relevant file here — not `main.tex`.
- `latex/fonts/` — TH Sarabun New TTFs, bundled locally (not system-installed) and loaded via a relative path
  (`Path = fonts/`) in `main.tex`'s `fontspec` setup. This makes the document portable across machines where the
  font isn't registered with the OS font system.
- `latex/images/` — figures extracted from the original `.docx` media, referenced by the theory section.
- `Progress/` — reference-only KKU thesis template materials (`cskkuproject.cls`, an example System Dev project,
  a blank chapter template), pulled in for later full-report work. Not part of the proposal build and not
  `\input` anywhere in `latex/main.tex` — don't confuse `cskkuproject.cls` with this repo's own preamble.

## Non-obvious formatting mechanics in `main.tex`

The heading/indentation system was tuned iteratively against a specific format spec (matching the original
Word document's look) and is easy to break by editing naively:

- **Cascading indent**: `\section`, `\subsection`, `\subsubsection` are redefined via `titlesec` so each level's
  title text starts exactly where the *previous* level's title text started (an outline "staircase" — e.g. `5.1`'s
  title lines up under `5.`'s title, not under the `5.` number). This is done with fixed-width `\makebox`es
  (`\lvlOneBox`/`\lvlTwoBox`/`\lvlThreeBox`) whose widths are *measured* via `\settowidth` against real font
  metrics (not guessed lengths), so the gap after a section number is exactly 4 real interword spaces and exactly
  2 after a subsection/subsubsection number.
- **Paragraph indent tracks heading level**: each heading's `titleformat` "before" hook does
  `\global\parindent=\lvl?` so body text indents to match whichever heading it currently falls under. Because this
  relies on `\global`, don't wrap section content in extra grouping (`{...}`) in the section files, or the
  parindent change won't escape the group.
- **Thai line breaking**: `\XeTeXlinebreaklocale "th"` + `\XeTeXlinebreakskip` enable XeTeX's built-in Thai
  word-segmentation for justification. Without this, Thai paragraphs produce heavy overfull `\hbox` warnings.
- Figure/table caption words are renamed to Thai (`\figurename`→`ภาพที่`, `\tablename`→`ตารางที่`) via the
  `caption` package rather than left as English.
- `\pagestyle{empty}` throughout — the original document has no headers/footers/page numbers, so none were added.

## Known content quirks (intentional, not bugs)

- Figure numbering in `04-theory.tex` and duplicate/gapped subsection numbers present in the original `.docx`
  were corrected to be sequential, since LaTeX's `\section`/`\subsection`/`\subsubsection` auto-number — you don't
  need to (and shouldn't) hardcode numbers in the section titles.
- The budget section (`10-budget.tex`) intentionally has no dollar/baht amounts filled in — the source document
  didn't have them either.
