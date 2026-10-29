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

## Dino full report (`report/`)

The project report, built on the KKU template v2 (`NewTemplate/Template_Project_2026_v2_3.zip`; a worked example
is in `NewTemplate/Example_A_SystemDev_Project_2026_v2_1.zip`). Build with `cd report && latexmk main.tex`
(XeLaTeX + biber, configured in `.latexmkrc`). `cskkuproject.cls` + `cskkucore.sty`/`cskkufront.sty`/`cskkubib.sty`
and `theme/` are the template's own files — don't edit them; put project-specific preamble in `main.tex`.
Content: `frontmatter/`, `chapters/chapter1-5.tex`, `backmatter/` (appendices, biography, advisor form).

- The class is loaded with `nobiblatex` on purpose: this report keeps APA author-year citations (`\textcite`,
  `\parencite`), so `main.tex` loads biblatex `style=apa` itself and re-defines `\printreferences` with the
  template's heading. Don't drop `nobiblatex` unless switching to the template's numeric `[1]` style.
- Chapter titles come from the class (`\chapteronetitle` …) per the department guide.
- Template rules: plain `\begin{enumerate}` (no `[label=...]`), no hand-typed heading numbers, no manual
  `\vspace` in body text (the advisor form is the exception).
- The E-R overview `images/erd/erd-0-overview.tex` (all 29 tables, key columns only) is generated — edit table
  positions/keys/relationships in `images/erd/gen_overview.py` and rerun `python -I gen_overview.py` from that
  folder (it measures text with xelatex and auto-routes the lines). The five per-section ERDs are Mermaid `.mmd` files.

## Dino user manual (`manual/`)

A separate XeLaTeX document — the user manual (เอกสารคู่มือการใช้งาน) for the Dino project. It uses `cskkumanual.cls`
from `NewTemplate/Template_Manual_2026_1.zip` (same core `.sty` files as the report) but keeps the 3-chapter structure
of the "ไปนำแหน่" manual PDF at the repo root rather than the template's 8-chapter layout. Build with
`cd manual && latexmk main.tex`. Content lives in `preface.tex` (inside the class's `preface` environment, which prints
the authors' names) and `chapter1-3.tex`.
Screenshots go in `manual/images/screens/<name>.png`; `\appscreen{<name>}{caption}` shows a red placeholder box until the
file exists (it can't be called `\screenshot` — the class defines a `screenshot` environment for annotated screenshots).
`\fillin{...}` marks text still needing confirmation against the real app/repo — grep for it before submitting.
