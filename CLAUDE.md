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
from `NewTemplate/Template_Manual_2026_1.zip` (same core `.sty` files as the report) and follows the template's
8-chapter layout (restructured 2026-10-29): `chapters/ch1-overview` … `ch8-troubleshooting`, `appendix-a-glossary`,
`appendix-b-api`, plus `chapters/preface.tex` (inside the class's `preface` environment, which prints the authors'
names) and `references.bib`. Ch4 = tourist (Guest + member) usage, ch5 = admin web panel, ch6 = server-side
administration (upgrade, monitoring; backup section removed at user request). The admin data-maintenance section is ch5 "การเพิ่มและอัปเดตฐานข้อมูล" (sec:data-update), written from the admin role only. Build with `cd manual && latexmk main.tex`
(XeLaTeX + biber). The revision-history page was removed on purpose — don't add it back.
- Use the class macros: `steps` + `\result`, `\btn`/`\field`/`\menu`/`\keys`/`\cmd`/`\filename`, `note`/`tip`/
  `warning`/`important` boxes, `troubleshooting`/`faq`/`glossarylist`, and `screenshot` + `\callout`/`\calloutline` +
  `calloutlist` for numbered screenshots (coordinates are 0–1 fractions from the top-left; add the `grid` option
  temporarily to find them). Plain screenshots use `\appscreen{<name>}{caption}` from `images/screens/<name>.png|jpg`,
  which shows a red placeholder box until the file exists.
- Formal plain style (user request 2026-10-29), done as overrides in `main.tex` only: body is black-and-white, only
  the callout numbers drawn on screenshots stay red; `note`/`tip`/`warning`/`important` render as a plain paragraph
  starting with "หมายเหตุ : " (not bold, with a colon); `\result{...}` prints its text as an ordinary sentence with no "ผลลัพธ์:" label;
  inside `\cmd`/`\filename` write characters literally (`~`, `_`, `\`) — they don't expand LaTeX macros; `steps`/`calloutlist` are numbered 1) 2); `\btn`/`\field`/`\menu` print as quoted
  text (so write "คลิกปุ่ม \btn{X}", "เมนู \btn{X}" — the word ปุ่ม/เมนู must be in the source); `\keys` is plain text;
  button/menu names drop any on-screen symbol or icon prefix (write `\btn{สร้างแผนใหม่}`, not `\btn{+ สร้างแผนใหม่}`);
  terminal/code blocks have a black frame on white. Don't reintroduce colored boxes, icons, or button chips.
  Never put two หมายเหตุ paragraphs back to back — keep one and turn the other into ordinary body text.
- `appendix-b-api.tex`'s REST table is generated from `main repo/backend/openapi.yaml` — regenerate it when the API
  changes rather than hand-editing rows.
- `\fillin{...}` marks text still needing confirmation against the real app/repo — grep for it before submitting.
