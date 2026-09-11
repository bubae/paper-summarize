"""
논문 요약용 SVG 레이아웃 헬퍼.

손으로 좌표를 찍는 개념도 SVG가 요약 작성의 가장 큰 병목이라, 반복되는
레이아웃 7종을 함수로 뺐다. 사용법:

    import sys; sys.path.insert(0, '.claude/skills/paper-figures/assets')
    from svgkit import *

    s = Svg(780, 380, "제목", "부제")
    s.cards([("제목A","줄1","줄2"), ("제목B","줄1","줄2")], y=44, h=90, palette=["g","b"])
    s.table(["열1","열2"], [["a","b"],["c","d"]], x=20, y=150, widths=[120,200])
    s.note("결론 한 줄", y=300, kind="warn")
    print(s.done())

모든 함수는 절대 좌표를 반환하므로 필요하면 raw()로 직접 덧그릴 수 있다.
색 키: n(중립) b(파랑·주 경로) o(주황·기존/강조) g(초록·성과) r(빨강·문제)
       p(보라·대안) w(노랑 경고). CLAUDE.md 팔레트와 일치한다.
"""
import html

PAL = {
    "n": ("#f1f5f9", "#64748b", "#334155"),
    "b": ("#dbeafe", "#3b82f6", "#1e40af"),
    "o": ("#fef3c7", "#f59e0b", "#92400e"),
    "g": ("#dcfce7", "#16a34a", "#15803d"),
    "r": ("#fef2f2", "#ef4444", "#b91c1c"),
    "p": ("#f3e8ff", "#a855f7", "#7e22ce"),
    "w": ("#fffbea", "#eab308", "#92400e"),
    "i": ("#e0e7ff", "#6366f1", "#4338ca"),
}
def esc(t):
    """SVG 텍스트 이스케이프. <tspan> 마크업은 통과시킨다."""
    if "<tspan" in t or "</tspan>" in t:
        return t
    return html.escape(t, quote=False)


class Svg:
    def __init__(self, w=800, h=400, title=None, sub=None, mid=""):
        self.w, self.h, self.mid = w, h, mid
        self.o = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" font-family="sans-serif">']
        self._defs = []
        if title:
            self.o.append(f'<text x="{w/2:.0f}" y="17" text-anchor="middle" font-size="14.5" font-weight="bold">{esc(title)}</text>')
        if sub:
            self.o.append(f'<text x="{w/2:.0f}" y="33" text-anchor="middle" font-size="9.5" fill="#666">{esc(sub)}</text>')

    # ---------- 기본 ----------
    def raw(self, s): self.o.append(s); return self
    def text(self, x, y, t, size=10, anchor="start", bold=False, fill="#334155", italic=False):
        st = ' font-weight="bold"' if bold else ''
        it = ' font-style="italic"' if italic else ''
        self.o.append(f'<text x="{x:.0f}" y="{y:.0f}" text-anchor="{anchor}" font-size="{size}" fill="{fill}"{st}{it}>{esc(t)}</text>')
        return self
    def box(self, x, y, w, h, kind="n", r=6, width=1.2):
        f, st, _ = PAL[kind]
        self.o.append(f'<rect x="{x:.0f}" y="{y:.0f}" width="{w:.0f}" height="{h:.0f}" rx="{r}" fill="{f}" stroke="{st}" stroke-width="{width}"/>')
        return self
    def arrow(self, x1, y1, x2, y2, kind="n", dash="", width=1.4):
        mid = f"ar{self.mid}{len(self._defs)}"
        col = PAL[kind][1]
        self._defs.append(f'<marker id="{mid}" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="{col}"/></marker>')
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.o.append(f'<path d="M{x1:.0f},{y1:.0f} L{x2:.0f},{y2:.0f}" stroke="{col}" stroke-width="{width}" fill="none"{d} marker-end="url(#{mid})"/>')
        return self
    def divider(self, x, y1, y2):
        self.o.append(f'<line x1="{x:.0f}" y1="{y1:.0f}" x2="{x:.0f}" y2="{y2:.0f}" stroke="#cbd5e1" stroke-dasharray="5 4"/>')
        return self

    # ---------- 레이아웃 7종 ----------
    def cards(self, items, y, h=88, x=20, w=None, gap=11, palette=None, title_size=10.5, body_size=9.5):
        """items: [(제목, 줄1, 줄2, ...), ...] · palette: 카드별 색 키 리스트"""
        n = len(items)
        w = w if w else (self.w - 2*x - gap*(n-1)) / n
        for i, it in enumerate(items):
            k = (palette[i] if palette else "n")
            cx = x + i*(w+gap)
            self.box(cx, y, w, h, k, r=7, width=1.6)
            self.text(cx+w/2, y+19, it[0], title_size, "middle", True, PAL[k][2])
            for j, line in enumerate(it[1:]):
                self.text(cx+11, y+38+j*15, line, body_size)
        return self

    def table(self, header, rows, x, y, widths, rh=22, hkind="n", cellfills=None, bold_rows=(), fsize=8.8):
        """cellfills: rows와 같은 shape의 색 키 배열 또는 None"""
        hx = x
        for j, col in enumerate(header):
            f, st, _ = PAL[hkind] if not isinstance(hkind, list) else PAL[hkind[j]]
            self.o.append(f'<rect x="{hx:.0f}" y="{y:.0f}" width="{widths[j]}" height="{rh}" fill="#e2e8f0" stroke="#94a3b8"/>')
            self.text(hx+widths[j]/2, y+rh*0.68, col, fsize+0.4, "middle", True)
            hx += widths[j]
        for i, row in enumerate(rows):
            ry = y + rh*(i+1)
            cx = x
            for j, cell in enumerate(row):
                fill = "#fff"
                if cellfills and cellfills[i][j]:
                    fill = PAL[cellfills[i][j]][0]
                self.o.append(f'<rect x="{cx:.0f}" y="{ry:.0f}" width="{widths[j]}" height="{rh}" fill="{fill}" stroke="#e8edf3"/>')
                anchor = "start" if j == 0 else "middle"
                tx = cx+8 if j == 0 else cx+widths[j]/2
                self.text(tx, ry+rh*0.68, str(cell), fsize, anchor, i in bold_rows)
                cx += widths[j]
        return self

    def steps(self, items, y, h=54, x=20, kind="b", numbered=True):
        """가로 단계 흐름. items: [(제목, 설명), ...]"""
        n = len(items)
        w = (self.w - 2*x - 22*(n-1)) / n
        for i, (t, d) in enumerate(items):
            cx = x + i*(w+22)
            self.box(cx, y, w, h, kind, width=1.6)
            lab = f"{'①②③④⑤⑥⑦'[i]} " if numbered and i < 7 else ""
            self.text(cx+w/2, y+20, lab+t, 10.5, "middle", True, PAL[kind][2])
            self.text(cx+w/2, y+38, d, 9, "middle")
            if i < n-1:
                self.arrow(cx+w+2, y+h/2, cx+w+19, y+h/2, kind)
        return self

    def stack(self, items, y, x=None, w=300, rh=26, gap=4):
        """세로 계층 스택. items: [(라벨, 색키), ...] 위에서 아래로"""
        x = x if x is not None else (self.w-w)/2
        for i, (lab, k) in enumerate(items):
            ry = y + i*(rh+gap)
            self.box(x, ry, w, rh, k, r=5, width=1.6)
            self.text(x+w/2, ry+rh*0.68, lab, 10, "middle", True, PAL[k][2])
        return self

    def quad(self, x, y, w, h, xlab, ylab, quads):
        """4사분면. quads: [(좌상),(우상),(좌하),(우하)] 각각 (제목, 줄1, 줄2, 색키)"""
        self.o.append(f'<line x1="{x}" y1="{y+h}" x2="{x+w}" y2="{y+h}" stroke="#333" stroke-width="1.4"/>')
        self.o.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+h}" stroke="#333" stroke-width="1.4"/>')
        self.text(x+w/2, y+h+20, xlab, 10, "middle")
        self.o.append(f'<text x="{x-30:.0f}" y="{y+h/2:.0f}" font-size="10" transform="rotate(-90 {x-30:.0f} {y+h/2:.0f})" text-anchor="middle">{esc(ylab)}</text>')
        for qi, q in enumerate(quads):
            col, row = qi % 2, qi // 2
            qx, qy = x + col*w/2 + 2, y + row*h/2 + 2
            f = PAL[q[3]][0]
            self.o.append(f'<rect x="{qx:.0f}" y="{qy:.0f}" width="{w/2-4:.0f}" height="{h/2-4:.0f}" fill="{f}" fill-opacity="0.6"/>')
            self.text(qx+w/4, qy+20, q[0], 10, "middle", True, PAL[q[3]][2])
            for j, line in enumerate(q[1:3]):
                self.text(qx+w/4, qy+38+j*15, line, 9, "middle")
        return self

    def note(self, lines, y, x=20, w=None, kind="w", h=None, title=None):
        """하단 결론 박스. lines: 문자열 또는 리스트"""
        if isinstance(lines, str): lines = [lines]
        w = w if w else self.w - 2*x
        h = h if h else (20 + (18 if title else 0) + 17*len(lines))
        self.box(x, y, w, h, kind, r=6, width=1.6)
        yy = y + 18
        if title:
            self.text(x+10, yy, title, 10.5, "start", True, PAL[kind][2]); yy += 18
        for ln in lines:
            self.text(x+10, yy, ln, 10); yy += 17
        return self

    def scoreboard(self, items, y, x=20, h=66, palette=None):
        """숫자 카드. items: [(라벨, 큰수치, 설명), ...]"""
        n = len(items); w = (self.w-2*x-10*(n-1))/n
        for i, (lab, num, desc) in enumerate(items):
            k = palette[i] if palette else "b"
            cx = x + i*(w+10)
            self.box(cx, y, w, h, k, r=7, width=1.8)
            self.text(cx+w/2, y+18, lab, 10, "middle", True, PAL[k][2])
            self.text(cx+w/2, y+42, num, 20, "middle", True, PAL[k][2])
            self.text(cx+w/2, y+58, desc, 8.5, "middle", fill="#555")
        return self

    def done(self):
        head = f'<defs>{"".join(self._defs)}</defs>' if self._defs else ""
        return self.o[0] + "\n" + head + "\n" + "\n".join(self.o[1:]) + "\n</svg>\n"


def figure(svg_str, caption):
    return f"<figure>\n{svg_str}<figcaption>{caption}</figcaption>\n</figure>\n"
