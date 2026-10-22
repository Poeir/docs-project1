% =====================================================================
%  cskkumanual.cls  v1 — เล่มคู่มือการใช้งาน (User Manual) ของโครงงานคอมพิวเตอร์
%  สาขาวิชาวิทยาการคอมพิวเตอร์ วิทยาลัยการคอมพิวเตอร์ มหาวิทยาลัยขอนแก่น
%
%  รูปแบบหน้า ฟอนต์ ขนาด หัวข้อ ตาราง ภาพ สารบัญ ใช้ cskkucore.sty
%  ชุดเดียวกับเล่มรายงาน (cskkuproject.cls)
%  Compile ด้วย XeLaTeX (Overleaf: Compiler = XeLaTeX)
%
%  คำสั่งเฉพาะเล่มคู่มือ
%    \begin{screenshot}[width=..,grid]{ไฟล์ภาพ}{ชื่อภาพ}{label} ... \end{screenshot}
%        \callout{x}{y}{n}            หมายเลขกำกับบนภาพ (x,y = 0..1 จากมุมซ้ายบน)
%        \calloutline{x}{y}{tx}{ty}{n} หมายเลขพร้อมเส้นชี้ไปยังจุด (tx,ty)
%        \highlight{x}{y}{w}{h}       กรอบเน้นบริเวณ
%    \begin{calloutlist} \item ... \end{calloutlist}   คำอธิบายหมายเลข
%    \begin{steps} \item ... \end{steps}               ขั้นตอนการใช้งาน
%    \begin{note} / tip / warning / important          กล่องข้อความ
%    \btn{ปุ่ม}  \menu{เมนู > เมนูย่อย}  \keys{Ctrl+S}  \field{ช่อง}  \calloutmark{1}
%    \begin{terminal} ... \end{terminal}               คำสั่งใน Terminal
%    \begin{codefile}{ชื่อไฟล์} ... \end{codefile}       เนื้อหาไฟล์ตั้งค่า/โค้ด
%    \begin{faq} \question{...} คำตอบ ... \end{faq}     คำถามที่พบบ่อย
%    \begin{troubleshooting} \problem{อาการ}{สาเหตุ}{วิธีแก้} \end{troubleshooting}
%    \begin{envtable} \envvar{ชื่อ}{ค่าตัวอย่าง}{คำอธิบาย} \end{envtable}
%    \begin{glossarylist} \term{คำ}{ความหมาย} \end{glossarylist}
%    \begin{revisionhistory} \revision{ฉบับ}{วันที่}{รายละเอียด}{ผู้แก้ไข} \end{revisionhistory}
%    \begin{guide} ... \end{guide}                    กล่องแนวทางการเขียน (แสดงเมื่อใช้ตัวเลือก guides)
%    \writingguide{ไฟล์}                               หน้าแนวทางการเขียนเล่ม (แสดงเมื่อใช้ตัวเลือก guides)
%
%  ตัวเลือก guides: แสดงแนวทางการเขียนในเล่ม ลบออกจาก \documentclass ก่อนส่งเล่ม
% =====================================================================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{cskkumanual}[2026/10/21 v1.0.1 CS KKU Project User Manual]

\newif\ifcskku@titleasis \cskku@titleasisfalse
\DeclareOption{titleasis}{\cskku@titleasistrue}
\newif\ifcskku@guides \cskku@guidesfalse
\DeclareOption{guides}{\cskku@guidestrue}
\DeclareOption*{\PassOptionsToPackage{\CurrentOption}{cskkucore}}
\ProcessOptions\relax

% fix-cm: ฟอนต์คณิตศาสตร์ (Computer Modern) ปรับได้ทุกขนาด เช่น 13 bp / 16 bp
\RequirePackage{fix-cm}
\LoadClass[a4paper,oneside,12pt]{report}
\RequirePackage{cskkucore}
\RequirePackage{cskkufront}
\RequirePackage{tikz}
\usetikzlibrary{calc,shapes.geometric,positioning,arrows.meta}
\RequirePackage[most]{tcolorbox}

\doctype{เอกสารคู่มือการใช้งาน}
\coverstatement{รายงานเล่มนี้เป็นส่วนหนึ่งของการศึกษาวิชา}

% ข้อมูลเพิ่มเติมของระบบ (แสดงในบทนำและประวัติการแก้ไข)
\cskku@field{systemVersion}{1.0}
\cskku@field{systemURL}{https://example.kku.ac.th}
% เรียกใช้ในเนื้อหา: \systemname \systemversion \systemurl
\newcommand*\systemname{\@titleTH}
\newcommand*\systemversion{\@systemVersion}
\newcommand*\systemurl{\expandafter\url\expandafter{\@systemURL}}

% ---------------------------------------------------------------------
% สี (เลือกให้พิมพ์ขาวดำแล้วยังแยกออก)
% ---------------------------------------------------------------------
\definecolor{cskkuCallout}{HTML}{D62839}
\definecolor{cskkuStep}{HTML}{1F4E79}
\definecolor{cskkuNote}{HTML}{1F6FB2}
\definecolor{cskkuNoteBg}{HTML}{EAF2FA}
\definecolor{cskkuTip}{HTML}{2E7D32}
\definecolor{cskkuTipBg}{HTML}{EAF5EA}
\definecolor{cskkuWarn}{HTML}{B85C00}
\definecolor{cskkuWarnBg}{HTML}{FFF3E0}
\definecolor{cskkuImp}{HTML}{B71C1C}
\definecolor{cskkuImpBg}{HTML}{FDECEC}
\definecolor{cskkuFrame}{HTML}{9AA4AE}
\definecolor{cskkuGrid}{HTML}{00A3E0}
\definecolor{cskkuTermBg}{HTML}{F1F3F5}
\definecolor{cskkuGuide}{HTML}{6A3FA0}
\definecolor{cskkuGuideBg}{HTML}{F6F1FC}

% ---------------------------------------------------------------------
% คำนำ (ส่วนต้น) — ลงชื่อผู้จัดทำท้ายคำนำ
% ---------------------------------------------------------------------
\newenvironment{preface}{%
  \clearpage
  \cskkuUnnumberedChapter{คำนำ}}
 {\par\vspace{\baselineskip}%
  \begin{flushright}
    \begin{tabular}{@{}c@{}}\cskku@studentnamesprefixTH\end{tabular}
  \end{flushright}%
  \clearpage}

% ---------------------------------------------------------------------
% ประวัติการแก้ไขเอกสาร
% ---------------------------------------------------------------------
\newcommand\revision[4]{#1 & #2 & #3 & #4\\ \hline}
\newenvironment{revisionhistory}{%
  \clearpage
  \cskkuUnnumberedChapter{ประวัติการแก้ไขเอกสาร}%
  \addtocounter{table}{-1}%
  \setlength\LTleft{0pt}\setlength\LTright{0pt plus 1fill}%
  \begin{longtable}{|C{1.4cm}|C{2.6cm}|L{\dimexpr\linewidth-7.2cm-8\tabcolsep-5\arrayrulewidth\relax}|L{3.2cm}|}
  \hline
  \textbf{ฉบับที่} & \textbf{วันที่} & \textbf{รายละเอียดการแก้ไข} & \textbf{ผู้แก้ไข}\\ \hline
  \endhead}
 {\end{longtable}\clearpage}

% ---------------------------------------------------------------------
% ภาพหน้าจอพร้อมหมายเลขกำกับ (TikZ ซ้อนบนภาพ)
% พิกัด (x,y) เป็นสัดส่วนของภาพ 0..1 วัดจาก "มุมซ้ายบน" ของภาพ
% ใช้ตัวเลือก grid เพื่อแสดงตารางพิกัดช่วยหาตำแหน่ง แล้วลบออกก่อนส่ง
% ---------------------------------------------------------------------
\newlength\cskku@ssw
\newif\ifcskku@ssgrid
\newif\ifcskku@ssborder
\pgfkeys{
  /cskku/ss/.is family, /cskku/ss,
  width/.code   = {\setlength\cskku@ssw{#1}},
  grid/.code    = {\cskku@ssgridtrue},
  border/.code  = {\cskku@ssbordertrue},
  noborder/.code= {\cskku@ssborderfalse},
}
\tikzset{
  cskkucallout/.style={circle, fill=cskkuCallout, draw=white, line width=0.9pt,
    text=white, font=\normalfont\small\bfseries, inner sep=0pt,
    minimum size=15bp},
  cskkucalloutinline/.style={circle, fill=cskkuCallout, text=white,
    font=\normalfont\footnotesize\bfseries, inner sep=0pt, minimum size=12.5bp},
  cskkustep/.style={rectangle, rounded corners=2pt, fill=cskkuStep, text=white,
    font=\normalfont\footnotesize\bfseries, inner sep=0pt,
    minimum width=13bp, minimum height=13bp},
}
\newcommand\cskku@drawgrid{%
  \foreach \cskku@g in {1,...,19}{%
    \draw[cskkuGrid, line width=0.2pt, opacity=0.55, dashed]
      (\cskku@g/20,0) -- (\cskku@g/20,1) (0,\cskku@g/20) -- (1,\cskku@g/20);}%
  \foreach \cskku@g in {1,...,9}{%
    \draw[cskkuGrid, line width=0.45pt, opacity=0.9]
      (\cskku@g/10,0) -- (\cskku@g/10,1) (0,\cskku@g/10) -- (1,\cskku@g/10);
    \node[font=\normalfont\scriptsize, fill=white, fill opacity=0.85, text opacity=1,
          inner sep=1pt, anchor=north] at (\cskku@g/10,1) {0.\cskku@g};
    \node[font=\normalfont\scriptsize, fill=white, fill opacity=0.85, text opacity=1,
          inner sep=1pt, anchor=west] at (0,1-\cskku@g/10) {0.\cskku@g};}}

\NewDocumentEnvironment{screenshot}{O{}mmm}{%
  \setlength\cskku@ssw{0.9\linewidth}%
  \cskku@ssgridfalse\cskku@ssbordertrue
  \pgfkeys{/cskku/ss,#1}%
  \begin{figure}[H]
  \centering
  \begin{tikzpicture}
    \node[anchor=south west, inner sep=0pt, outer sep=0pt] (cskkuimg) at (0,0)
      {\includegraphics[width=\cskku@ssw]{#2}};
    \ifcskku@ssborder
      \draw[cskkuFrame, line width=0.5pt]
        (cskkuimg.south west) rectangle (cskkuimg.north east);
    \fi
    \begin{scope}[x={(cskkuimg.south east)}, y={(cskkuimg.north west)}]
      \ifcskku@ssgrid\cskku@drawgrid\fi
}{%
    \end{scope}
  \end{tikzpicture}
  \caption{#3}\label{#4}
  \end{figure}}

% ใช้ภายใน screenshot เท่านั้น
\newcommand\callout[3]{\node[cskkucallout] at (#1,{1-(#2)}) {#3};}
\newcommand\calloutline[5]{%
  \draw[cskkuCallout, line width=1pt] (#1,{1-(#2)}) -- (#3,{1-(#4)});
  \fill[cskkuCallout] (#3,{1-(#4)}) circle (1.6pt);
  \node[cskkucallout] at (#1,{1-(#2)}) {#5};}
\newcommand\highlight[4]{%
  \draw[cskkuCallout, line width=1.4pt, rounded corners=2pt]
    (#1,{1-(#2)}) rectangle ({(#1)+(#3)},{1-(#2)-(#4)});}

% หมายเลขกำกับในเนื้อความ เช่น "คลิกปุ่ม \calloutmark{2}"
\DeclareRobustCommand\calloutmark[1]{%
  \tikz[baseline=(cskkucm.base)]\node[cskkucalloutinline] (cskkucm) {#1};}

% คำอธิบายหมายเลขใต้ภาพ: หมายเลขรูปแบบเดียวกับบนภาพ
\newlist{calloutlist}{enumerate}{1}
\setlist[calloutlist]{label=\calloutmark{\arabic*}, ref=\arabic*,
  leftmargin=*, labelindent=\cskku@curindent, labelsep=0.6em,
  topsep=2bp, itemsep=1bp, parsep=0pt}

% ---------------------------------------------------------------------
% ขั้นตอนการใช้งาน
% ---------------------------------------------------------------------
\DeclareRobustCommand\cskku@stepmark[1]{%
  \tikz[baseline=(cskkust.base)]\node[cskkustep] (cskkust) {#1};}
\newlist{steps}{enumerate}{2}
\setlist[steps,1]{label=\cskku@stepmark{\arabic*}, ref=\arabic*,
  leftmargin=*, labelindent=\cskku@curindent, labelsep=0.6em,
  topsep=2bp, itemsep=2bp, parsep=0pt}
\setlist[steps,2]{label=\alph*), leftmargin=*, labelsep=0.5em, itemsep=0pt}
% รายการย่อยในขั้นตอน (enumerate) เป็นรายการซ้อนระดับที่สอง a) b) c) และเริ่มที่ข้อความของขั้นตอน
\AtBeginEnvironment{steps}{\let\step\item
  \setlist*[enumerate,1]{label=\alph*), ref=\alph*, labelindent=0pt}%
  \setlist*[enumerate,2]{label=\roman*), ref=\roman*}%
  \setlist*[itemize,1]{labelindent=0pt}}
% ผลลัพธ์ที่ควรเห็นหลังทำขั้นตอน
\newcommand\result[1]{\par{\color{cskkuStep}\textbf{ผลลัพธ์:}}\ #1}

% ---------------------------------------------------------------------
% กล่องหมายเหตุ / เคล็ดลับ / คำเตือน / สำคัญ
% ---------------------------------------------------------------------
\DeclareRobustCommand\cskku@icon[3]{% #1 shape, #2 color, #3 text
  \tikz[baseline=-0.32em]\node[#1, fill=#2, text=white, inner sep=0pt,
    minimum size=11.5bp, font=\normalfont\footnotesize\bfseries] {#3};}
\tcbset{
  cskkubox/.style={enhanced, breakable,
    boxrule=0pt, leftrule=3pt, arc=1.5pt, outer arc=1.5pt,
    left=7bp, right=7bp, top=3bp, bottom=3bp,
    before skip=0.5\baselineskip, after skip=0.5\baselineskip,
    left skip=\cskku@curindent,
    fontupper=\normalfont, coltitle=black,
    attach title to upper, after title={\ \ }},
}
\newtcolorbox{note}[1][]{cskkubox, colback=cskkuNoteBg, colframe=cskkuNote,
  title={\cskku@icon{circle}{cskkuNote}{i}\ \textbf{\color{cskkuNote}หมายเหตุ}}, #1}
\newtcolorbox{tip}[1][]{cskkubox, colback=cskkuTipBg, colframe=cskkuTip,
  title={\cskku@icon{circle}{cskkuTip}{\ding{51}}\ \textbf{\color{cskkuTip}เคล็ดลับ}}, #1}
\newtcolorbox{warning}[1][]{cskkubox, colback=cskkuWarnBg, colframe=cskkuWarn,
  title={\cskku@icon{regular polygon, regular polygon sides=3}{cskkuWarn}{!}\ %
         \textbf{\color{cskkuWarn}คำเตือน}}, #1}
\newtcolorbox{important}[1][]{cskkubox, colback=cskkuImpBg, colframe=cskkuImp,
  title={\cskku@icon{circle}{cskkuImp}{!}\ \textbf{\color{cskkuImp}สำคัญ}}, #1}

% ---------------------------------------------------------------------
% แนวทางการเขียน (สำหรับนักศึกษา) — แสดงเฉพาะเมื่อใช้ตัวเลือก guides
%   \begin{guide} ... \end{guide}   หรือ  \begin{guide}[หัวเรื่อง] ... \end{guide}
%   \writingguide{chapters/writing-guide}   หน้าแนวทางการเขียนทั้งเล่ม (ส่วนต้น)
% เมื่อลบตัวเลือก guides ออก กล่องและหน้าแนวทางทั้งหมดจะหายไปเอง ไม่ต้องลบทีละกล่อง
% ---------------------------------------------------------------------
\tcbset{
  cskkuguide/.style={enhanced, breakable,
    colback=cskkuGuideBg, frame hidden,
    borderline={0.8pt}{0pt}{cskkuGuide, dash pattern=on 3pt off 2pt},
    arc=2pt, outer arc=2pt, left=8bp, right=8bp, top=3bp, bottom=4bp,
    before skip=0.6\baselineskip, after skip=0.8\baselineskip,
    fontupper=\normalfont\small, coltitle=cskkuGuide, colbacktitle=cskkuGuideBg,
    fonttitle=\normalfont\small\bfseries, toptitle=3bp, bottomtitle=0bp,
    titlerule=0pt, boxed title style={empty}},
}
\NewDocumentEnvironment{guide}{O{แนวทางการเขียน} +b}{%
  \ifcskku@guides
    \par
    \begin{tcolorbox}[cskkuguide, title={\ding{46}\ #1}]%
      \setlength\parindent{0pt}\setlength\parskip{2bp}%
      \setlist*[itemize,1]{labelindent=0pt, leftmargin=*, label=\textbullet}%
      \setlist*[enumerate,1]{labelindent=0pt, leftmargin=*}%
      #2%
    \end{tcolorbox}%
  \fi}{}
\newcommand\writingguide[1]{%
  \ifcskku@guides
    \clearpage
    \cskkuUnnumberedChapter{แนวทางการเขียนเล่มคู่มือการใช้งาน}%
    \input{#1}%
    \clearpage
  \fi}
% เตือนบนทุกหน้าเมื่อเปิดแนวทางการเขียน เพื่อไม่ให้ส่งเล่มที่ยังมีกล่องแนวทาง
\ifcskku@guides
  \AddToHook{shipout/foreground}{%
    \setlength\unitlength{1bp}%
    \put(108,-43){\makebox[0pt][l]{\normalfont\footnotesize
      \color{cskkuGuide}\ding{46}\ ฉบับร่างที่แสดงแนวทางการเขียน
      — ลบตัวเลือก guides ใน main.tex ก่อนส่งเล่ม}}}
\fi

% ---------------------------------------------------------------------
% องค์ประกอบหน้าจอในเนื้อความ (ไม่ทำให้ระยะบรรทัดเปลี่ยน)
% ---------------------------------------------------------------------
\DeclareRobustCommand\btn[1]{%
  \smash{\tikz[baseline=(cskkub.base)]\node[draw=cskkuFrame, fill=black!6,
    rounded corners=1.5pt, inner xsep=3bp, inner ysep=1.2bp, line width=0.5pt,
    font=\normalfont\small] (cskkub) {#1};}}
\DeclareRobustCommand\field[1]{%
  \smash{\tikz[baseline=(cskkuf.base)]\node[draw=cskkuFrame, fill=white,
    rounded corners=0pt, inner xsep=3bp, inner ysep=1.2bp, line width=0.5pt,
    dash pattern=on 1.5pt off 1pt, font=\normalfont\small] (cskkuf) {#1};}}
\DeclareRobustCommand\key[1]{%
  \smash{\tikz[baseline=(cskkuk.base)]\node[draw=black!55, fill=white,
    rounded corners=2pt, inner xsep=2.5bp, inner ysep=1bp, line width=0.5pt,
    font=\ttfamily\small] (cskkuk) {#1};}}
\ExplSyntaxOn
\NewDocumentCommand\keys{m}{
  \seq_set_split:Nnn \l_tmpa_seq {+} {#1}
  \seq_map_indexed_inline:Nn \l_tmpa_seq
    { \int_compare:nNnT {##1} > {1} {\,+\,} \key{##2} }}
\NewDocumentCommand\menu{m}{
  \seq_set_split:Nnn \l_tmpb_seq {>} {#1}
  \seq_map_indexed_inline:Nn \l_tmpb_seq
    { \int_compare:nNnT {##1} > {1} {\,\ensuremath{\blacktriangleright}\,} \textbf{##2} }}
\ExplSyntaxOff
% ชื่อไฟล์ / คำสั่งสั้นในบรรทัด (พิมพ์ตามตัวอักษร ไม่แปลง -- เป็นขีดยาว
% ใช้ _ ได้โดยตรง ตัดบรรทัดได้หลัง / . _ - : เมื่อยาว — ดู \cskkuCode ใน cskkucore.sty)
\newcommand\filename[1]{\cskkuCode{#1}}
\newcommand\cmd[1]{\cskkuCode{#1}}

% ---------------------------------------------------------------------
% คำสั่งใน Terminal และไฟล์ตั้งค่า (คัดลอกไปใช้ได้ตรงตามตัวอักษร)
% ---------------------------------------------------------------------
\lstdefinestyle{cskkuterminal}{style=cskku, numbers=none,
  backgroundcolor=\color{cskkuTermBg}, rulecolor=\color{cskkuTermBg},
  framesep=5bp, xleftmargin=\dimexpr\cskku@curindent+5bp\relax,
  framexleftmargin=5bp, xrightmargin=5bp, framexrightmargin=5bp}
\lstnewenvironment{terminal}[1][]{\lstset{style=cskkuterminal,#1}}{}
\lstnewenvironment{codefile}[2][]{%
  \lstset{style=cskku, title={\normalfont\small\textbf{ไฟล์}~\texttt{#2}}, #1}}{}

% ---------------------------------------------------------------------
% คำถามที่พบบ่อย
% ---------------------------------------------------------------------
\newenvironment{faq}{%
  \par
  \newcommand\question[1]{%
    \par\addvspace{6bp}%
    {\setlength\parindent{\cskku@curindent}%
     \hangindent=\dimexpr\cskku@curindent+2.4em\relax\hangafter=1
     \makebox[2.4em][l]{\textbf{\color{cskkuStep}ถาม}}\textbf{##1}\par}%
    \nobreak
    \noindent\hangindent=\dimexpr\cskku@curindent+2.4em\relax\hangafter=1
    \hspace*{\cskku@curindent}%
    \makebox[2.4em][l]{\textbf{\color{cskkuTip}ตอบ}}\ignorespaces}}
 {\par}

% ---------------------------------------------------------------------
% ตารางสำเร็จรูป (longtable: ตัดข้ามหน้าได้ หัวตารางพิมพ์ซ้ำทุกหน้า)
% ใส่ชื่อตารางได้: \begin{troubleshooting}[ชื่อตาราง][label]
% หน้าที่ต่อจะพิมพ์ "ตารางที่ n ชื่อตาราง (ต่อ)" ให้อัตโนมัติ (คู่มือข้อ 8.3)
% ---------------------------------------------------------------------
\newcommand\cskku@ltcaption[2]{% #1 = caption or -NoValue-, #2 = label
  \IfValueTF{#1}
    {\def\cskku@ltcap{\caption{#1}\IfValueT{#2}{\label{#2}}\\}%
     \def\cskku@ltcapcont{\caption[]{#1~\cskkuContinued}\\}}
    {\let\cskku@ltcap\@empty\let\cskku@ltcapcont\@empty
     \addtocounter{table}{-1}}}% longtable นับเลขตารางเองแม้ไม่มีชื่อ

\newcommand\problem[3]{#1 & #2 & #3\\ \hline}
\NewDocumentEnvironment{troubleshooting}{oo}{%
  \cskku@ltcaption{#1}{#2}%
  \begin{longtable}{|L{0.29\linewidth}|L{0.29\linewidth}|L{\dimexpr0.42\linewidth-6\tabcolsep-4\arrayrulewidth\relax}|}
  \cskku@ltcap
  \hline
  \textbf{อาการ / ข้อความที่พบ} & \textbf{สาเหตุที่เป็นไปได้} & \textbf{วิธีแก้ไข}\\ \hline
  \endfirsthead
  \cskku@ltcapcont
  \hline
  \textbf{อาการ / ข้อความที่พบ} & \textbf{สาเหตุที่เป็นไปได้} & \textbf{วิธีแก้ไข}\\ \hline
  \endhead}
 {\end{longtable}}

\newcommand\envvar[3]{\cskkuCode{#1} & \cskkuCode{#2} & #3\\ \hline}
\NewDocumentEnvironment{envtable}{oo}{%
  \cskku@ltcaption{#1}{#2}%
  \begin{longtable}{|L{0.3\linewidth}|L{0.28\linewidth}|L{\dimexpr0.42\linewidth-6\tabcolsep-4\arrayrulewidth\relax}|}
  \cskku@ltcap
  \hline
  \textbf{ตัวแปร} & \textbf{ค่าตัวอย่าง} & \textbf{คำอธิบาย}\\ \hline
  \endfirsthead
  \cskku@ltcapcont
  \hline
  \textbf{ตัวแปร} & \textbf{ค่าตัวอย่าง} & \textbf{คำอธิบาย}\\ \hline
  \endhead}
 {\end{longtable}}

\newcommand\term[2]{\textbf{#1} & #2\\}
\newenvironment{glossarylist}{%
  \addtocounter{table}{-1}%
  \setlength\LTleft{\cskku@curindent}\setlength\LTright{0pt plus 1fill}%
  \renewcommand\arraystretch{1.15}%
  \begin{longtable}{@{}L{0.28\linewidth}L{\dimexpr0.72\linewidth-\cskku@curindent-2\tabcolsep\relax}@{}}}
 {\end{longtable}}

\endinput
