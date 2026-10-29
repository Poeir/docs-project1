"""สร้าง erd-0-overview.tex (E-R Diagram ภาพรวม) จากรายการตาราง/คีย์/ความสัมพันธ์ด้านล่าง

ตำแหน่งตารางกำหนดเองในส่วน TABLES ส่วนเส้นความสัมพันธ์ให้สคริปต์หาเส้นทางแบบมุมฉากเอง
(A* บนกริด 0.1 ซม. หลีกเลี่ยงตาราง เส้นซ้อน และลดจำนวนเส้นตัดกัน/จุดหักมุม)

วิธีใช้:  python -I gen_overview.py      (ต้องมี xelatex ใน PATH — ใช้วัดความกว้างข้อความจริง)
"""
import heapq
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = (HERE.parent.parent / 'theme' / 'fonts').as_posix() + '/'
OUT = HERE / 'erd-0-overview.tex'

HEAD, ROW, PAD = 0.6, 0.5, 0.15      # ซม.: ความสูงหัวตาราง/แถว และช่องว่างซ้ายขวาของข้อความ
STUB = 0.6                           # ช่วงตรงที่ปลายเส้นเพื่อวางสัญลักษณ์ Crow's Foot
G = 10                               # จำนวนช่องกริดต่อ 1 ซม.

GROUP_STYLE = {
    'acc': 'gAcc', 'pts': 'gPts', 'plc': 'gPlc', 'evt': 'gEvt', 'trp': 'gTrp', 'std': 'gStd',
}

# id, ชื่อตาราง, กลุ่ม, x ซ้าย (หรือ ('r', x ขวา)), y บน (ต้องลงท้าย .x5), แถวคีย์
TABLES = [
    ('us',  'users', 'acc', 0.0, 1.45, [('id', 'PK'), ('email', 'UK'), ('deleted_by', 'FK'), ('status_changed_by', 'FK')]),
    ('aal', 'admin_audit_log', 'acc', ('r', -3.8), 7.05, [('id', 'PK'), ('admin_id', 'FK'), ('target_user_id', 'FK')]),
    ('ses', 'sessions', 'acc', ('r', -3.8), 4.25, [('id', 'PK'), ('user_id', 'FK')]),
    ('evt', 'email_verification_tokens', 'acc', ('r', -3.8), 2.05, [('id', 'PK'), ('user_id', 'FK')]),
    ('prt', 'password_reset_tokens', 'acc', ('r', -3.8), -0.25, [('id', 'PK'), ('user_id', 'FK')]),
    ('ect', 'email_change_tokens', 'acc', ('r', -3.8), -2.45, [('id', 'PK'), ('user_id', 'FK')]),

    ('erq', 'event_requests', 'evt', 6.4, 10.05, [('id', 'PK'), ('place_id', 'FK'), ('event_id', 'FK'), ('user_id', 'FK'), ('reviewed_by', 'FK')]),
    ('erp', 'event_request_photos', 'evt', 12.4, 11.05, [('id', 'PK'), ('request_id', 'FK')]),
    ('erep', 'event_reports', 'evt', 6.4, 6.45, [('id', 'PK'), ('event_id', 'FK'), ('user_id', 'FK'), ('resolved_by', 'FK')]),
    ('ev',  'events', 'evt', 11.4, 7.65, [('id', 'PK'), ('place_id', 'FK')]),
    ('ep',  'event_photos', 'evt', 16.4, 8.15, [('id', 'PK'), ('event_id', 'FK')]),
    ('pr',  'place_reports', 'plc', 12.4, 5.05, [('id', 'PK'), ('place_id', 'FK'), ('user_id', 'FK'), ('resolved_by', 'FK')]),

    ('pc',  'place_candidates', 'plc', 10.4, 1.65, [('google_place_id', 'PK'), ('decided_by', 'FK'), ('place_id', 'FK')]),
    ('psj', 'place_sync_jobs', 'plc', 10.4, -1.25, [('id', 'PK'), ('created_by', 'FK')]),
    ('psr', 'place_sync_results', 'plc', 15.6, -0.75, [('id', 'PK'), ('job_id', 'FK'), ('place_id', 'FK')]),
    ('pas', 'place_auto_sync_settings', 'plc', 10.4, -3.65, [('id', 'PK'), ('updated_by', 'FK')]),
    ('pl',  'places', 'plc', 20.6, 2.05, [('id', 'PK'), ('google_place_id', 'UK')]),
    ('pp',  'place_photos', 'plc', 26.8, 2.55, [('id', 'PK'), ('place_id', 'FK')]),

    ('pa',  'points_adjustments', 'pts', -6.6, -5.25, [('id', 'PK'), ('user_id', 'FK'), ('admin_id', 'FK')]),
    ('rd',  'redemptions', 'pts', 4.0, -3.45, [('id', 'PK'), ('user_id', 'FK'), ('admin_id', 'FK'), ('cancelled_by', 'FK'), ('reward_id', 'FK')]),
    ('rw',  'rewards', 'pts', 6.2, -7.65, [('id', 'PK')]),
    ('qs',  'qr_scans', 'pts', 3.2, -7.05, [('id', 'PK'), ('user_id', 'FK'), ('qr_id', 'FK')]),
    ('qr',  'qrs', 'pts', -2.6, -8.15, [('id', 'PK'), ('place_id', 'FK')]),

    ('tr',  'trips', 'trp', 10.4, -6.25, [('id', 'PK'), ('user_id', 'FK')]),
    ('td',  'trip_days', 'trp', 16.0, -4.65, [('id', 'PK'), ('trip_id', 'FK')]),
    ('ti',  'trip_items', 'trp', 21.6, -4.65, [('id', 'PK'), ('day_id', 'FK'), ('place_id', 'FK')]),

    ('kb',  'knowledge_base', 'std', 26.8, -2.95, [('id', 'PK')]),
    ('sr',  'survey_responses', 'std', 26.8, -4.75, [('id', 'PK')]),
    ('gf',  'google_fallback_usage', 'std', 26.8, -6.55, [('day', 'PK')]),
]

# (ตารางลูก, คอลัมน์ FK, ตารางแม่, ปลายฝั่งแม่, ปลายฝั่งลูก, ชื่อความสัมพันธ์หรือ None)
ONE, ZO, ZM = 'one', 'zeroone', 'zeromany'
EDGES = [
    ('ses', 'user_id', 'us', ONE, ZM, 'มีเซสชัน'),
    ('evt', 'user_id', 'us', ONE, ZM, 'มีโทเคนยืนยันอีเมล'),
    ('prt', 'user_id', 'us', ONE, ZM, 'มีโทเคนตั้งรหัสผ่าน'),
    ('ect', 'user_id', 'us', ONE, ZO, 'มีโทเคนเปลี่ยนอีเมล'),
    ('aal', 'admin_id', 'us', ZO, ZM, 'เป็นผู้ดำเนินการ'),
    ('aal', 'target_user_id', 'us', ZO, ZM, 'เป็นผู้ถูกกระทำ'),
    ('us', 'status_changed_by', 'us', ZO, ZM, 'ระงับบัญชีโดย'),
    ('us', 'deleted_by', 'us', ZO, ZM, 'ลบบัญชีโดย'),

    ('qs', 'user_id', 'us', ONE, ZM, 'สแกน'),
    ('rd', 'user_id', 'us', ONE, ZM, 'แลก'),
    ('rd', 'admin_id', 'us', ZO, ZM, 'เจ้าหน้าที่ดำเนินการ'),
    ('rd', 'cancelled_by', 'us', ZO, ZM, 'เจ้าหน้าที่ยกเลิก'),
    ('pa', 'user_id', 'us', ONE, ZM, 'ถูกปรับพอยท์'),
    ('pa', 'admin_id', 'us', ZO, ZM, 'ผู้ปรับ'),
    ('qr', 'place_id', 'pl', ONE, ZO, 'ติดตั้งที่'),
    ('qs', 'qr_id', 'qr', ONE, ZM, 'ถูกสแกน'),
    ('rd', 'reward_id', 'rw', ZO, ZM, 'ถูกแลก'),

    ('pp', 'place_id', 'pl', ONE, ZM, 'มีรูปภาพ'),
    ('pr', 'place_id', 'pl', ONE, ZM, 'ถูกรายงาน'),
    ('psr', 'place_id', 'pl', ONE, ZM, 'มีผลซิงก์'),
    ('psr', 'job_id', 'psj', ONE, ZM, 'ประกอบด้วย'),
    ('pc', 'place_id', 'pl', ZO, ZM, 'นำเข้าเป็น'),
    ('pr', 'user_id', 'us', ZO, ZM, 'เป็นผู้แจ้ง'),
    ('pr', 'resolved_by', 'us', ZO, ZM, 'เป็นผู้ตอบรับรายงาน'),
    ('psj', 'created_by', 'us', ZO, ZM, 'เป็นผู้สร้างงาน'),
    ('pc', 'decided_by', 'us', ZO, ZM, 'เป็นผู้พิจารณา'),
    ('pas', 'updated_by', 'us', ZO, ZM, 'เป็นผู้แก้การตั้งค่า'),

    ('ev', 'place_id', 'pl', ZO, ZM, 'จัดขึ้นที่'),
    ('ep', 'event_id', 'ev', ONE, ZM, 'มีรูปภาพ'),
    ('erep', 'event_id', 'ev', ONE, ZM, 'ถูกรายงาน'),
    ('erq', 'event_id', 'ev', ZO, ZO, 'อนุมัติจาก'),
    ('erq', 'place_id', 'pl', ZO, ZM, 'ระบุสถานที่'),
    ('erp', 'request_id', 'erq', ONE, ZM, 'แนบรูปภาพ'),
    ('erep', 'user_id', 'us', ZO, ZM, 'เป็นผู้แจ้ง'),
    ('erep', 'resolved_by', 'us', ZO, ZM, 'เป็นผู้ตอบรับรายงาน'),
    ('erq', 'reviewed_by', 'us', ZO, ZM, 'เป็นผู้ตรวจสอบคำขอ'),
    ('erq', 'user_id', 'us', ONE, ZM, 'เป็นผู้ส่งคำขอ'),

    ('tr', 'user_id', 'us', ZO, ZM, 'สร้างแผน'),
    ('td', 'trip_id', 'tr', ONE, ZM, 'ประกอบด้วยวัน'),
    ('ti', 'day_id', 'td', ONE, ZM, 'ประกอบด้วยจุดแวะ'),
    ('ti', 'place_id', 'pl', ZO, ZM, 'อ้างอิงสถานที่'),
]

LEGEND_AT = (-8.4, 10.9)
MINW = {'us': 4.6, 'pl': 3.6}
LEGEND = [('gAcc', 'บัญชีผู้ใช้และการยืนยันตัวตน'), ('gPts', 'พอยท์สะสมและของรางวัล'),
          ('gPlc', 'สถานที่ การรายงาน และการซิงก์ข้อมูล'), ('gEvt', 'กิจกรรมและคำขอเพิ่มกิจกรรม'),
          ('gTrp', 'ประวัติแผนการเดินทาง'), ('gStd', 'ตารางอิสระ')]


# ---------------------------------------------------------------- วัดความกว้างข้อความ
def tex(s):
    return s.replace('_', r'\_')


def measure(strings):
    """คืนความกว้าง (ซม.) ของข้อความแต่ละชุด (font, text) โดยให้ XeLaTeX วัดจริง"""
    work = Path(tempfile.gettempdir()) / 'erd-overview-measure'
    work.mkdir(exist_ok=True)
    lines = [r'\documentclass{article}', r'\usepackage{fontspec}',
             r'\setmainfont{THSarabunNew}[Path=' + FONTS + r', Extension=.ttf, UprightFont=*-Regular, BoldFont=*-Bold]',
             r'\XeTeXlinebreaklocale "th"',
             r'\newcommand\sm{\fontsize{13bp}{17bp}\selectfont}',
             r'\newcommand\ft{\fontsize{11bp}{14bp}\selectfont}',
             r'\begin{document}', r'\newbox\mb']
    for i, (font, s) in enumerate(strings):
        cmd = {'sm': r'\sm', 'smb': r'\sm\bfseries', 'ft': r'\ft'}[font]
        lines.append(r'\setbox\mb\hbox{%s %s}\typeout{MW:%d:\the\wd\mb}' % (cmd, tex(s), i))
    lines.append(r'\end{document}')
    (work / 'm.tex').write_text('\n'.join(lines), encoding='utf-8')
    subprocess.run(['xelatex', '-interaction=nonstopmode', '-no-pdf', 'm.tex'], cwd=work,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log = (work / 'm.log').read_text(encoding='utf-8', errors='replace')
    out = {}
    for m in re.finditer(r'MW:(\d+):([\d.]+)pt', log):
        out[strings[int(m.group(1))]] = float(m.group(2)) / 72.27 * 2.54
    if len(out) != len(strings):
        sys.exit('measure failed: see ' + str(work / 'm.log'))
    return out


def ceil01(v):
    return int(-(-v * 10 // 1)) / 10


# ---------------------------------------------------------------- เรขาคณิตของตาราง
class Table:
    pass


def build_tables():
    strings = set()
    for _, name, _, _, _, rows in TABLES:
        strings.add(('smb', name))
        for c, k in rows:
            strings.add(('sm', c))
            strings.add(('sm', k))
    for e in EDGES:
        if e[5]:
            strings.add(('ft', e[5]))
    W = measure(sorted(strings))
    keyw = max(W[('sm', k)] for k in ('PK', 'FK', 'UK')) + 2 * PAD
    tabs = {}
    for tid, name, grp, x, top, rows in TABLES:
        t = Table()
        t.id, t.name, t.grp, t.rows = tid, name, grp, rows
        namew = max(W[('sm', c)] for c, _ in rows) + 2 * PAD
        t.keyw = keyw
        t.w = max(MINW.get(tid, 0), ceil01(max(W[('smb', name)] + 4 * PAD, namew + keyw)))
        assert abs(round((top - 0.05) * 10) - (top - 0.05) * 10) < 1e-6, (tid, 'top must end in .x5')
        t.top = top
        t.h = HEAD + ROW * len(rows)
        t.bot = top - t.h
        t.x = x[1] - t.w if isinstance(x, tuple) else x
        t.x = round(t.x * 10) / 10
        t.x1 = t.x + t.w
        t.rowy = {c: top - HEAD - ROW * (i + 0.5) for i, (c, _) in enumerate(rows)}
        tabs[tid] = t
    return tabs, W


# ---------------------------------------------------------------- ตัวหาเส้นทาง
DX = [(1, 0), (0, 1), (-1, 0), (0, -1)]   # E N W S
BEND, CROSS, NEAR, NEARBOX = 12, 45, 5, 2


class Router:
    def __init__(self, tabs):
        xs = [t.x for t in tabs.values()] + [t.x1 for t in tabs.values()]
        ys = [t.top for t in tabs.values()] + [t.bot for t in tabs.values()]
        self.ox, self.oy = int(min(xs) * G) - 40, int(min(ys) * G) - 40
        self.nx = int(max(xs) * G) - self.ox + 40
        self.ny = int(max(ys) * G) - self.oy + 40
        n = self.nx * self.ny
        self.block = bytearray(n)
        self.occH = bytearray(n)
        self.occV = bytearray(n)
        self.occB = bytearray(n)
        self.nearH = bytearray(n)
        self.nearV = bytearray(n)
        self.nearbox = bytearray(n)
        for t in tabs.values():
            x0, x1 = self.gx(t.x), self.gx(t.x1)
            y0, y1 = int((t.bot * G) // 1), int(-(-(t.top * G) // 1))
            for gx in range(x0 - 7, x1 + 8):
                for gy in range(y0 - 7, y1 + 8):
                    if not self.inside(gx, gy):
                        continue
                    i = self.idx(gx, gy)
                    dist = max(x0 - 1 - gx, gx - x1 - 1, y0 - 1 - gy, gy - y1 - 1)
                    if dist <= 0:
                        self.block[i] = 1
                    else:
                        self.nearbox[i] = max(self.nearbox[i], (0, 4, 3, 2, 1, 1, 1)[min(dist, 6)])
        self.ports = {}   # (table, side) -> [positions]

    def gx(self, v):
        return int(round(v * G))

    def inside(self, gx, gy):
        return 0 <= gx - self.ox < self.nx and 0 <= gy - self.oy < self.ny

    def idx(self, gx, gy):
        return (gy - self.oy) * self.nx + (gx - self.ox)

    def free_for_stub(self, cells, horiz):
        same = self.occH if horiz else self.occV
        for gx, gy in cells:
            if not self.inside(gx, gy):
                return False
            i = self.idx(gx, gy)
            if self.block[i] or same[i] or self.occB[i]:
                return False
        return True

    def child_starts(self, t, col, extra=0.0):
        y = self.gx(t.rowy[col])
        s = int(round((STUB + extra) * G))
        res = []
        for side, x, d in (('W', self.gx(t.x), 2), ('E', self.gx(t.x1), 0)):
            sx = x - s if side == 'W' else x + s
            step = -1 if side == 'W' else 1
            stub = [(x + step * k, y) for k in range(2, s + 1)]
            if self.free_for_stub(stub, True):
                res.append(((sx, y), d, (x / G, y / G), side))
        return res

    def parent_goals(self, t, exclude=()):
        goals = {}
        s = int(STUB * G)
        x0, x1 = self.gx(t.x), self.gx(t.x1)
        top, bot = t.top, t.bot
        yt, yb = self.gx(top + STUB - 0.05) , self.gx(bot - STUB + 0.05)
        ylo, yhi = int(-(-(bot * G) // 1)) + 3, int((top * G) // 1) - 3
        for side, positions in (('W', range(ylo, yhi + 1)), ('E', range(ylo, yhi + 1)),
                                ('N', range(x0 + 3, x1 - 2)), ('S', range(x0 + 3, x1 - 2))):
            if side in exclude:
                continue
            used = self.ports.get((t.id, side), [])
            for p in positions:
                if any(abs(p - u) < 4 for u in used):
                    continue
                if side == 'W':
                    a, d, port, stub = (x0 - s, p), 0, (x0 / G, p / G), [(x0 - k, p) for k in range(2, s)]
                elif side == 'E':
                    a, d, port, stub = (x1 + s, p), 2, (x1 / G, p / G), [(x1 + k, p) for k in range(2, s)]
                elif side == 'N':
                    a, d, port, stub = (p, yt), 3, (p / G, top), [(p, yt - k) for k in range(0, s - 2)]
                else:
                    a, d, port, stub = (p, yb), 1, (p / G, bot), [(p, yb + k) for k in range(0, s - 2)]
                if self.free_for_stub(stub, side in 'WE'):
                    goals[(a, d)] = (port, side, p)
        return goals

    def route(self, starts, goals, prect):
        px0, px1, py0, py1 = prect
        def h(x, y):
            dx = px0 - x if x < px0 else (x - px1 if x > px1 else 0)
            dy = py0 - y if y < py0 else (y - py1 if y > py1 else 0)
            return dx + dy
        heap, best, prev = [], {}, {}
        for (sx, sy), d, sp, side in starts:
            st = (sx, sy, d)
            best[st] = 0
            prev[st] = (None, (sp, side))
            heapq.heappush(heap, (h(sx, sy), 0, st))
        block, occH, occV, occB = self.block, self.occH, self.occV, self.occB
        nearH, nearV, nearbox = self.nearH, self.nearV, self.nearbox
        while heap:
            f, g, st = heapq.heappop(heap)
            if g > best.get(st, 1e18):
                continue
            x, y, d = st
            if ((x, y), d) in goals:
                return self.unwind(prev, st), goals[((x, y), d)]
            for nd in (d, (d + 1) % 4, (d + 3) % 4):
                ddx, ddy = DX[nd]
                nx, ny = x + ddx, y + ddy
                if not self.inside(nx, ny):
                    continue
                i = self.idx(nx, ny)
                if block[i] or occB[i]:
                    continue
                c = 1
                horiz = nd in (0, 2)
                if nd != d:
                    ci = self.idx(x, y)
                    if occH[ci] or occV[ci]:
                        continue
                    c += BEND
                if horiz:
                    if occH[i]:
                        continue
                    if occV[i]:
                        c += CROSS
                    c += NEAR * nearH[i]
                else:
                    if occV[i]:
                        continue
                    if occH[i]:
                        c += CROSS
                    c += NEAR * nearV[i]
                c += NEARBOX * nearbox[i]
                ng = g + c
                ns = (nx, ny, nd)
                if ng < best.get(ns, 1e18):
                    best[ns] = ng
                    prev[ns] = (st, None)
                    heapq.heappush(heap, (ng + h(nx, ny), ng, ns))
        return None, None

    def unwind(self, prev, st):
        cells = []
        while True:
            p, info = prev[st]
            cells.append((st[0], st[1]))
            if p is None:
                return list(reversed(cells)), info
            st = p

    def commit(self, pts_grid):
        """ทำเครื่องหมายช่องกริดที่เส้นผ่าน (pts_grid = จุดหักมุมรวมปลายทั้งสองข้าง)"""
        for (ax, ay), (bx, by) in zip(pts_grid, pts_grid[1:]):
            if ay == by:
                for x in range(min(ax, bx), max(ax, bx) + 1):
                    i = self.idx(x, ay)
                    self.occH[i] = 1
                    for k in (-2, -1, 1, 2):
                        if self.inside(x, ay + k):
                            j = self.idx(x, ay + k)
                            self.nearH[j] = min(255, self.nearH[j] + (2 if abs(k) == 1 else 1))
            else:
                for y in range(min(ay, by), max(ay, by) + 1):
                    i = self.idx(ax, y)
                    self.occV[i] = 1
                    for k in (-2, -1, 1, 2):
                        if self.inside(ax + k, y):
                            j = self.idx(ax + k, y)
                            self.nearV[j] = min(255, self.nearV[j] + (2 if abs(k) == 1 else 1))
        for x, y in pts_grid[1:-1]:
            self.occB[self.idx(x, y)] = 1


def simplify(cells):
    pts = [cells[0]]
    for a, b, c in zip(cells, cells[1:], cells[2:]):
        if (b[0] - a[0], b[1] - a[1]) != (c[0] - b[0], c[1] - b[1]):
            pts.append(b)
    pts.append(cells[-1])
    return pts


# ---------------------------------------------------------------- สร้างไฟล์ TikZ
def main():
    tabs, W = build_tables()
    tl = list(tabs.values())
    bad = False
    for i, a in enumerate(tl):
        for b in tl[i + 1:]:
            if a.x < b.x1 + 0.3 and b.x < a.x1 + 0.3 and a.bot < b.top + 0.3 and b.bot < a.top + 0.3:
                print('too close: %s (%.1f..%.1f, %.2f..%.2f) / %s (%.1f..%.1f, %.2f..%.2f)' % (
                    a.name, a.x, a.x1, a.bot, a.top, b.name, b.x, b.x1, b.bot, b.top))
                bad = True
    if bad or '--check' in sys.argv:
        for t in tl:
            print('  %-26s w=%.1f x=%.1f..%.1f y=%.2f..%.2f' % (t.name, t.w, t.x, t.x1, t.top, t.bot))
        sys.exit(1 if bad else 0)
    R = Router(tabs)
    order = sorted(range(len(EDGES)), key=lambda k: (
        EDGES[k][2] == 'us',
        abs(tabs[EDGES[k][0]].rowy[EDGES[k][1]] - (tabs[EDGES[k][2]].top + tabs[EDGES[k][2]].bot) / 2)
        + abs((tabs[EDGES[k][0]].x + tabs[EDGES[k][0]].x1) / 2 - (tabs[EDGES[k][2]].x + tabs[EDGES[k][2]].x1) / 2)))
    routed = {}
    for k in order:
        child, col, parent, pc, cc, lab = EDGES[k]
        ct, pt = tabs[child], tabs[parent]
        extra = W[('ft', lab)] + 0.25 if lab else 0.0
        starts = R.child_starts(ct, col, extra)
        if child == parent:   # เส้นอ้างอิงตนเองออกทางขวาเท่านั้น ไม่ให้ชนเส้นของตารางบัญชีทางซ้าย
            starts = [st for st in starts if st[3] == 'E']
        goals = R.parent_goals(pt, exclude=('W', 'E') if child == parent else ())
        prect = (R.gx(pt.x) - 6, R.gx(pt.x1) + 6, R.gx(pt.bot) - 6, R.gx(pt.top) + 6)
        cells, ginfo = R.route(starts, goals, prect)
        if cells is None:
            sys.exit('no route: %s.%s -> %s' % (child, col, parent))
        cells, (cport, cside) = cells
        gpos, gside, gp = ginfo
        R.ports.setdefault((parent, gside), []).append(gp)
        cx, cy = cport
        sx = R.gx(cx)
        sy = R.gx(cy)
        px, py = gpos
        full = [(sx, sy)] + cells + [(R.gx(px), R.gx(py))]
        pts = simplify(full)
        R.commit(pts)
        routed[k] = (pts, cside, gside, (cx, cy), gpos)

    o = []
    o.append('% สร้างโดย gen_overview.py — แก้ตำแหน่งตาราง/ความสัมพันธ์ในสคริปต์แล้วรันใหม่ อย่าแก้ไฟล์นี้ด้วยมือ')
    o.append(r'\begin{tikzpicture}[x=1cm, y=1cm,')
    o.append(r'  gAcc/.style={fill=blue!14}, gPts/.style={fill=orange!22}, gPlc/.style={fill=green!17},')
    o.append(r'  gEvt/.style={fill=magenta!14}, gTrp/.style={fill=violet!16}, gStd/.style={fill=gray!14},')
    o.append(r'  rel/.style={semithick, rounded corners=2pt},')
    o.append(r'  lab/.style={font=\fontsize{11bp}{13bp}\selectfont, fill=white, inner sep=1pt},')
    o.append(r'  pics/one/.style={code={\draw[semithick] (-0.15,-0.14) -- (-0.15,0.14); \draw[semithick] (-0.27,-0.14) -- (-0.27,0.14);}},')
    o.append(r'  pics/zeroone/.style={code={\draw[semithick] (-0.15,-0.14) -- (-0.15,0.14); \draw[semithick, fill=white] (-0.38,0) circle (0.09);}},')
    o.append(r'  pics/zeromany/.style={code={\draw[semithick] (0,-0.16) -- (-0.28,0) -- (0,0.16); \draw[semithick, fill=white] (-0.40,0) circle (0.09);}},')
    o.append(']')
    f = lambda v: ('%.2f' % v).rstrip('0').rstrip('.')
    P = lambda x, y: '(%s,%s)' % (f(x), f(y))
    o.append(r'\fontsize{13bp}{15bp}\selectfont')
    for t in tabs.values():
        dash = ', dashed' if t.grp == 'std' else ''
        o.append('%% %s' % t.name)
        o.append(r'\filldraw[thick, %s%s] %s rectangle %s;' % (GROUP_STYLE[t.grp], dash, P(t.x, t.top), P(t.x1, t.top - HEAD)))
        o.append(r'\node[font=\bfseries] at %s {%s};' % (P((t.x + t.x1) / 2, t.top - HEAD / 2), tex(t.name)))
        o.append(r'\filldraw[thick, fill=white%s] %s rectangle %s;' % (dash, P(t.x, t.top - HEAD), P(t.x1, t.bot)))
        for i in range(1, len(t.rows)):
            y = t.top - HEAD - ROW * i
            o.append(r'\draw[gray!60] %s -- %s;' % (P(t.x, y), P(t.x1, y)))
        o.append(r'\draw[gray!60] %s -- %s;' % (P(t.x1 - t.keyw, t.top - HEAD), P(t.x1 - t.keyw, t.bot)))
        for c, kk in t.rows:
            y = t.rowy[c]
            o.append(r'\node[anchor=west] at %s {%s}; \node at %s {%s};' % (
                P(t.x + PAD, y), tex(c), P(t.x1 - t.keyw / 2, y), kk))
    rot_child = {'W': 0, 'E': 180}
    rot_parent = {'W': 0, 'E': 180, 'N': -90, 'S': 90}
    labels = []
    for k, (pts, cside, gside, cpt, gpt) in sorted(routed.items()):
        child, col, parent, pcard, ccard, lab = EDGES[k]
        coords = [(x / G, y / G) for x, y in pts]
        coords[0] = cpt
        coords[-1] = gpt
        o.append('%% %s.%s -> %s' % (tabs[child].name, col, tabs[parent].name))
        o.append(r'\draw[rel] ' + ' -- '.join(P(*c) for c in coords) + ';')
        o.append(r'\pic[rotate=%d] at %s {%s}; \pic[rotate=%d] at %s {%s};' % (
            rot_child[cside], P(*cpt), ccard, rot_parent[gside], P(*gpt), pcard))
        if lab:
            (ax, ay) = coords[0]
            wlab = W[('ft', lab)]
            sgn = -1 if cside == 'W' else 1
            labels.append(r'\node[lab, anchor=south] at %s {%s};' % (P(ax + sgn * (0.55 + wlab / 2 + 0.05), ay + 0.03), lab))
    o.extend(labels)
    lx, ly = LEGEND_AT
    o.append(r'\node[anchor=west, font=\bfseries] at %s {สีของตาราง};' % P(lx, ly))
    for i, (sty, txt) in enumerate(LEGEND, 1):
        y = ly - 0.55 * i
        dash = ', dashed' if sty == 'gStd' else ''
        o.append(r'\filldraw[thick, %s%s] %s rectangle %s; \node[anchor=west] at %s {%s};' % (
            sty, dash, P(lx + 0.05, y - 0.18), P(lx + 0.65, y + 0.18), P(lx + 0.8, y), txt))
    o.append(r'\end{tikzpicture}')
    OUT.write_text('\n'.join(o) + '\n', encoding='utf-8')
    print('written', OUT.name, '| tables', len(tabs), '| edges', len(routed))
    for t in tabs.values():
        print('  %-26s w=%.1f x=%.1f..%.1f y=%.2f..%.2f' % (t.name, t.w, t.x, t.x1, t.top, t.bot))


if __name__ == '__main__':
    main()
