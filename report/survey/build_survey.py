"""สร้าง survey-data.tex จากไฟล์ CSV ผลแบบสอบถามความพึงพอใจ

วิธีใช้ (รันจากโฟลเดอร์ report/):

    python survey/build_survey.py                 # อ่าน survey/survey-responses.csv
    python survey/build_survey.py path/to/file.csv

ไฟล์ CSV คือไฟล์ที่ export จากหน้าสรุปผลแบบสอบถามใน Admin Portal (คอลัมน์ id,
submitted_at, gender, age, age_group, occupation, ..., Q1..Q16, strengths, improvements)
ไฟล์ CSV ไม่ถูก commit (ดู .gitignore) เพราะมีคำตอบปลายเปิดและอาชีพที่ผู้ตอบพิมพ์เอง

ผลลัพธ์คือ survey/survey-data.tex ซึ่ง main.tex โหลดไว้ใน preamble ภายในมีแต่คำสั่ง
\\survey... (ตัวเลขและแถวของตาราง) ที่บทที่ 4, บทที่ 5 และบทคัดย่อเรียกใช้ จึงไม่ต้องแก้
ตัวเลขในไฟล์ .tex ด้วยมือ เมื่อได้ข้อมูลชุดใหม่ให้รันสคริปต์นี้แล้ว build รายงานใหม่

วิธีคำนวณตรงกับ backend/src/lib/surveyStats.js ของ dino-trip:
- รายข้อ: ค่าเฉลี่ยและ S.D. (n - 1) จากผู้ที่ตอบข้อนั้น ("ยังไม่เคยใช้" ไม่นำมาคิด)
- รายด้านและรวม: หาค่าเฉลี่ยของแต่ละคนก่อน แล้วจึงหาค่าเฉลี่ยและ S.D. ระหว่างผู้ตอบ
- แปลผลด้วยช่วงกว้าง 0.80 จากค่าเฉลี่ยที่ปัดสองตำแหน่ง

ข้อคำถามด้านล่างคัดลอกจาก backend/src/lib/surveyQuestions.js ถ้าแบบสอบถามเปลี่ยน
ต้องแก้ที่นี่ด้วย (ในรายงานสะกด "แชตบอต" ตามที่ใช้ทั้งเล่ม ส่วนในระบบสะกด "แชทบอท")
"""
import csv
import io
import math
import statistics as st
import sys
from collections import Counter
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_CSV = HERE / 'survey-responses.csv'
OUTPUT = HERE / 'survey-data.tex'

# จำนวนผู้ตอบขั้นต่ำที่ตั้งเป้าไว้ ถ้ายังไม่ถึง รายงานจะแสดงหมายเหตุสีแดงในบทที่ 4
TARGET_N = 30

DIMENSIONS = [
    ('function', 'ด้านการทำงานของระบบ'),
    ('chatbot', 'ด้านแชตบอต AI'),
    ('planner', 'ด้านการวางแผนเที่ยวด้วย AI'),
    ('usability', 'ด้านความง่ายในการใช้งาน'),
    ('design', 'ด้านการออกแบบและประสิทธิภาพ'),
    ('overall', 'ด้านความพึงพอใจโดยรวม'),
]

# (ข้อ, ด้าน, ข้อความ, ตอบ "ยังไม่เคยใช้" ได้หรือไม่)
QUESTIONS = [
    (1, 'function', 'ความครอบคลุมของฟีเจอร์สำหรับการวางแผนท่องเที่ยว', False),
    (2, 'function', 'ความถูกต้องของข้อมูลสถานที่ท่องเที่ยว', False),
    (3, 'function', 'ความตรงกับความต้องการของผลการค้นหาสถานที่', False),
    (4, 'chatbot', 'ความตรงกับคำถามของคำตอบจากแชตบอต', True),
    (5, 'chatbot', 'ความน่าเชื่อถือของข้อมูลจากแชตบอต', True),
    (6, 'chatbot', 'ความรวดเร็วในการตอบของแชตบอต', True),
    (7, 'planner', 'ความเหมาะสมของแผนเที่ยวกับความสนใจของท่าน', True),
    (8, 'planner', 'ความเป็นไปได้ในการทำตามตารางเวลาของแผนเที่ยว', True),
    (9, 'planner', 'การช่วยประหยัดเวลาในการวางแผนเที่ยว', True),
    (10, 'planner', 'ความรวดเร็วในการสร้างแผนเที่ยว', True),
    (11, 'usability', 'ความง่ายในการใช้งานระบบ', False),
    (12, 'usability', 'ความง่ายในการค้นหาข้อมูลที่ต้องการ', False),
    (13, 'design', 'ความสวยงามของการออกแบบหน้าจอ', False),
    (14, 'design', 'ความเร็วในการโหลดหน้าเว็บ', False),
    (15, 'overall', 'ความพึงพอใจโดยรวมต่อระบบ', False),
    (16, 'overall', 'ความตั้งใจที่จะแนะนำระบบให้ผู้อื่น', False),
]
SATISFACTION_ITEM = 15  # "ความพึงพอใจโดยรวมต่อระบบ"

DEMOGRAPHICS = [
    ('gender', 'เพศ', [('male', 'ชาย'), ('female', 'หญิง'), ('unspecified', 'ไม่ระบุ')]),
    ('age_group', 'อายุ', [('under20', 'ต่ำกว่า 20 ปี'), ('20-29', '20--29 ปี'), ('30-39', '30--39 ปี'), ('40plus', '40 ปีขึ้นไป')]),
    ('occupation', 'อาชีพ', [('student', 'นักศึกษา'), ('staff', 'บุคลากร'), ('tourist', 'นักท่องเที่ยวทั่วไป'), ('other', 'อื่น ๆ')]),
]

EXPERIENCE = [
    ('exp_plan_method', 'วิธีวางแผนเที่ยวหลักก่อนใช้ Dino', [
        ('search', 'ค้นหาจากเว็บไซต์/Google'),
        ('social', 'โซเชียลมีเดีย/รีวิว (Facebook, TikTok, Instagram)'),
        ('maps', 'Google Maps'),
        ('friends', 'สอบถามเพื่อนหรือคนรู้จัก'),
        ('app', 'แอป/เว็บวางแผนเที่ยวโดยเฉพาะ'),
        ('ai', 'ใช้ AI เช่น ChatGPT, Gemini'),
        ('none', 'ไม่ได้วางแผน ไปตามสถานการณ์'),
    ]),
    ('exp_plan_time', 'เวลาที่ใช้วางแผนเที่ยวหนึ่งครั้งโดยปกติ', [
        ('lt30m', 'น้อยกว่า 30 นาที'),
        ('30m-1h', '30 นาที -- 1 ชั่วโมง'),
        ('1-3h', 'มากกว่า 1 -- 3 ชั่วโมง'),
        ('gt3h', 'มากกว่า 3 ชั่วโมง'),
    ]),
    ('exp_ai_usage', 'การใช้แชตบอต AI (เช่น ChatGPT, Gemini) ก่อนใช้ Dino', [
        ('often', 'ใช้เป็นประจำ'),
        ('sometimes', 'เคยใช้บ้าง'),
        ('never', 'ไม่เคยใช้'),
    ]),
    ('exp_khonkaen', 'การรู้จักหรือเคยเที่ยวขอนแก่นมาก่อน', [
        ('local', 'อาศัยอยู่ในขอนแก่น/พื้นที่ใกล้เคียง'),
        ('visited', 'เคยมาเที่ยวแล้ว'),
        ('never', 'ยังไม่เคยมา'),
    ]),
]

LEVELS_EN = {'มากที่สุด': 'highest', 'มาก': 'high', 'ปานกลาง': 'moderate', 'น้อย': 'low', 'น้อยที่สุด': 'lowest'}
THAI_MONTHS = ['มกราคม', 'กุมภาพันธ์', 'มีนาคม', 'เมษายน', 'พฤษภาคม', 'มิถุนายน', 'กรกฎาคม', 'สิงหาคม', 'กันยายน', 'ตุลาคม', 'พฤศจิกายน', 'ธันวาคม']
BS = chr(92)
ROW_END = ' ' + BS * 2 + ' ' + BS + 'hline\n'


def round2(x):
    # ปัดแบบเดียวกับ Math.round(x * 100) / 100 ในระบบ
    return math.floor(x * 100 + 0.5) / 100


def fmt(x):
    return '-' if x is None else '%.2f' % round2(x)


def level(m):
    v = round2(m)
    if v >= 4.21:
        return 'มากที่สุด'
    if v >= 3.41:
        return 'มาก'
    if v >= 2.61:
        return 'ปานกลาง'
    if v >= 1.81:
        return 'น้อย'
    return 'น้อยที่สุด'


def stat(xs):
    if not xs:
        return {'n': 0, 'mean': None, 'sd': None, 'level': '-'}
    m = st.mean(xs)
    return {'n': len(xs), 'mean': m, 'sd': st.stdev(xs) if len(xs) > 1 else None, 'level': level(m)}


def tex(s):
    for ch in '&%#_':
        s = s.replace(ch, BS + ch)
    return s


def bold(s):
    return BS + 'textbf{' + s + '}'


def percent(count, n):
    return '%.2f' % round2(count * 100 / n) if n else '0.00'


def join_thai(parts):
    return parts[0] if len(parts) == 1 else ' '.join(parts[:-1]) + ' และ' + parts[-1]


def thai_date_range(rows):
    # submitted_at เป็นเวลา UTC แปลงเป็นเวลาไทยก่อนตัดวันที่
    days = sorted({(datetime.strptime(r['submitted_at'][:19], '%Y-%m-%dT%H:%M:%S') + timedelta(hours=7)).date() for r in rows})
    a, b = days[0], days[-1]
    def one(d, with_month=True, with_year=True):
        out = str(d.day)
        if with_month:
            out += ' ' + THAI_MONTHS[d.month - 1]
        if with_year:
            out += ' ' + str(d.year + 543)
        return out
    if a == b:
        return one(a)
    if (a.year, a.month) == (b.year, b.month):
        return '%d--%s' % (a.day, one(b))
    return one(a, with_year=a.year != b.year) + ' -- ' + one(b)


def answers(row, nos):
    return [int(row['Q%d' % no]) for no in nos if row.get('Q%d' % no, '') != '']


def main():
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_CSV
    if not src.exists():
        sys.exit('ไม่พบไฟล์ %s' % src)
    rows = list(csv.DictReader(io.open(src, encoding='utf-8-sig')))
    if not rows:
        sys.exit('ไฟล์ %s ไม่มีข้อมูล' % src)
    n = len(rows)
    if len({r['id'] for r in rows}) != n:
        sys.exit('พบ id ซ้ำในไฟล์ CSV กรุณาตรวจสอบก่อน')

    all_nos = [q[0] for q in QUESTIONS]
    item = {no: stat([int(r['Q%d' % no]) for r in rows if r.get('Q%d' % no, '') != '']) for no in all_nos}

    def respondent_means(nos):
        return [st.mean(a) for a in (answers(r, nos) for r in rows) if a]

    dim = {key: stat(respondent_means([q[0] for q in QUESTIONS if q[1] == key])) for key, _ in DIMENSIONS}
    overall = stat(respondent_means(all_nos))

    # ---- แถวของตาราง ----
    def count_rows(groups, with_total):
        out = ''
        for column, label, options in groups:
            counts = Counter(r[column] for r in rows)
            unknown = set(counts) - {v for v, _ in options}
            if unknown:
                sys.exit('คอลัมน์ %s มีค่าที่ไม่รู้จัก: %s' % (column, ', '.join(sorted(unknown))))
            out += bold(tex(label)) + ' & &' + ROW_END
            for value, text in options:
                out += '%s & %d & %s' % (tex(text), counts.get(value, 0), percent(counts.get(value, 0), n)) + ROW_END
            if with_total:
                out += 'รวม & %d & 100.00' % n + ROW_END
        return out

    item_rows = ''
    for key, label in DIMENSIONS:
        d = dim[key]
        item_rows += ' & '.join(bold(x) for x in (tex(label), str(d['n']), fmt(d['mean']), fmt(d['sd']), d['level'])) + ROW_END
        for no, qdim, text, _ in QUESTIONS:
            if qdim != key:
                continue
            s = item[no]
            item_rows += '%d. %s & %d & %s & %s & %s' % (no, tex(text), s['n'], fmt(s['mean']), fmt(s['sd']), s['level']) + ROW_END
    item_rows += ' & '.join(bold(x) for x in ('รวมทุกด้าน', str(overall['n']), fmt(overall['mean']), fmt(overall['sd']), overall['level'])) + ROW_END

    # ---- ค่าที่ใช้ในเนื้อความ ----
    def extremes(stats, labels, pick):
        scored = {k: round2(v['mean']) for k, v in stats.items() if v['mean'] is not None}
        target = pick(scored.values())
        return join_thai([labels[k] for k in stats if scored.get(k) == target]), '%.2f' % target, level(target)

    dim_labels = dict(DIMENSIONS)
    item_labels = {no: 'ข้อ %d %s' % (no, text) for no, _, text, _ in QUESTIONS}
    top_dim, top_dim_mean, top_dim_level = extremes(dim, dim_labels, max)
    low_dim, low_dim_mean, low_dim_level = extremes(dim, dim_labels, min)
    top_item, top_item_mean, _ = extremes(item, item_labels, max)
    low_item, low_item_mean, _ = extremes(item, item_labels, min)

    def top_option(column, options):
        counts = Counter(r[column] for r in rows)
        best = max(counts.values())
        return join_thai([text for value, text in options if counts.get(value, 0) == best]), best

    by_column = {c: opts for c, _, opts in DEMOGRAPHICS + EXPERIENCE}
    top_occ, top_occ_n = top_option('occupation', by_column['occupation'])
    top_age, top_age_n = top_option('age_group', by_column['age_group'])
    top_method, top_method_n = top_option('exp_plan_method', by_column['exp_plan_method'])
    top_time, top_time_n = top_option('exp_plan_time', by_column['exp_plan_time'])

    satisfied = sum(1 for r in rows if r['Q%d' % SATISFACTION_ITEM] != '' and int(r['Q%d' % SATISFACTION_ITEM]) >= 4)
    straight = sum(1 for r in rows if len(set(answers(r, all_nos))) == 1)
    skip_ns = sorted({item[q[0]]['n'] for q in QUESTIONS if q[3]})
    skip_range = str(skip_ns[0]) if len(skip_ns) == 1 else '%d--%d' % (skip_ns[0], skip_ns[-1])

    provisional = ''
    if n < TARGET_N:
        provisional = (BS + 'textcolor{red}{[ข้อมูลชั่วคราว: มีผู้ตอบ %d คน จากเป้าหมายอย่างน้อย %d คน '
                       'ตัวเลขในหัวข้อนี้จะเปลี่ยนเมื่อสร้างไฟล์ survey-data.tex ใหม่จากข้อมูลชุดสุดท้าย]}' % (n, TARGET_N)
                       + BS + 'par')

    macros = [
        ('surveyN', str(n)),
        ('surveyTargetN', str(TARGET_N)),
        ('surveyDateRange', thai_date_range(rows)),
        ('surveyOverallMean', fmt(overall['mean'])),
        ('surveyOverallSD', fmt(overall['sd'])),
        ('surveyOverallLevel', overall['level']),
        ('surveyOverallLevelEN', LEVELS_EN[overall['level']]),
        ('surveyTopDim', top_dim), ('surveyTopDimMean', top_dim_mean), ('surveyTopDimLevel', top_dim_level),
        ('surveyLowDim', low_dim), ('surveyLowDimMean', low_dim_mean), ('surveyLowDimLevel', low_dim_level),
        ('surveyTopItem', top_item), ('surveyTopItemMean', top_item_mean),
        ('surveyLowItem', low_item), ('surveyLowItemMean', low_item_mean),
        ('surveySatisfiedCount', str(satisfied)), ('surveySatisfiedPercent', percent(satisfied, item[SATISFACTION_ITEM]['n'])),
        ('surveyStraightCount', str(straight)),
        ('surveySkipRange', skip_range),
        ('surveyStrengthCount', str(sum(1 for r in rows if r.get('strengths', '').strip()))),
        ('surveyImproveCount', str(sum(1 for r in rows if r.get('improvements', '').strip()))),
        ('surveyTopOccupation', top_occ), ('surveyTopOccupationCount', str(top_occ_n)), ('surveyTopOccupationPercent', percent(top_occ_n, n)),
        ('surveyTopAge', top_age), ('surveyTopAgeCount', str(top_age_n)), ('surveyTopAgePercent', percent(top_age_n, n)),
        ('surveyTopPlanMethod', tex(top_method)), ('surveyTopPlanMethodCount', str(top_method_n)),
        ('surveyTopPlanTime', top_time), ('surveyTopPlanTimeCount', str(top_time_n)),
        ('surveyProvisionalNote', provisional),
        ('surveyDemographicRows', '%\n' + count_rows(DEMOGRAPHICS, True)),
        ('surveyExperienceRows', '%\n' + count_rows(EXPERIENCE, False)),
        ('surveyItemRows', '%\n' + item_rows),
    ]

    lines = [
        '% สร้างอัตโนมัติโดย survey/build_survey.py -- อย่าแก้ไฟล์นี้ด้วยมือ',
        '%% แหล่งข้อมูล: %s (ผู้ตอบ %d คน, %s)' % (src.name, n, thai_date_range(rows)),
        '% เมื่อได้ข้อมูลชุดใหม่ ให้รัน python survey/build_survey.py จากโฟลเดอร์ report/ แล้ว build รายงานใหม่',
    ]
    for name, value in macros:
        lines.append(BS + 'newcommand{' + BS + name + '}{' + value + '}')
    io.open(OUTPUT, 'w', encoding='utf-8', newline='\n').write('\n'.join(lines) + '\n')

    out = sys.stdout
    if hasattr(out, 'reconfigure'):
        out.reconfigure(encoding='utf-8')
    print('เขียน %s แล้ว' % OUTPUT)
    print('ผู้ตอบ %d คน (%s) ค่าเฉลี่ยรวม %s S.D. %s ระดับ%s' % (n, thai_date_range(rows), fmt(overall['mean']), fmt(overall['sd']), overall['level']))
    for key, label in DIMENSIONS:
        print('  %-32s n=%2d  %s  %s  %s' % (label, dim[key]['n'], fmt(dim[key]['mean']), fmt(dim[key]['sd']), dim[key]['level']))
    if n < TARGET_N:
        print('คำเตือน: ผู้ตอบยังไม่ถึงเป้าหมาย %d คน รายงานจะแสดงหมายเหตุสีแดงในบทที่ 4' % TARGET_N)
    print('อย่าลืมอ่านทวนย่อหน้าที่มี TODO(survey) ใน chapter4.tex เพราะเขียนจากคำตอบปลายเปิดด้วยมือ')


if __name__ == '__main__':
    main()
