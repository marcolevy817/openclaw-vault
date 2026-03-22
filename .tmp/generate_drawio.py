#!/usr/bin/env python3
"""Generate draw.io diagram for 'How To Trade The News' video script."""

def xml_escape(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

cells = []
cell_id = 10

def new_id():
    global cell_id
    cell_id += 1
    return str(cell_id)

def box(x, y, w, h, label, fill="#1a1a2e", font_color="#ffffff", font_size=14, bold=True, rounded=1, border="#ffffff"):
    cid = new_id()
    b = "1" if bold else "0"
    cells.append(f'<mxCell id="{cid}" value="{xml_escape(label)}" style="rounded={rounded};whiteSpace=wrap;html=1;fillColor={fill};strokeColor={border};fontColor={font_color};fontSize={font_size};fontStyle={b};arcSize=12;" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return cid

def arrow(src, tgt, label="", curved=1, color="#555555"):
    cid = new_id()
    cells.append(f'<mxCell id="{cid}" value="{xml_escape(label)}" style="edgeStyle=orthogonalEdgeStyle;curved={curved};rounded=1;orthogonalLoop=1;jettySize=auto;exitX=0.5;exitY=1;exitDx=0;exitDy=0;entryX=0.5;entryY=0;entryDx=0;entryDy=0;strokeColor={color};strokeWidth=2;fontSize=11;" edge="1" source="{src}" target="{tgt}" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>')
    return cid

def arrow_right(src, tgt, label="", color="#555555"):
    cid = new_id()
    cells.append(f'<mxCell id="{cid}" value="{xml_escape(label)}" style="edgeStyle=orthogonalEdgeStyle;curved=1;rounded=1;orthogonalLoop=1;jettySize=auto;exitX=1;exitY=0.5;exitDx=0;exitDy=0;entryX=0;entryY=0.5;entryDx=0;entryDy=0;strokeColor={color};strokeWidth=2;fontSize=11;" edge="1" source="{src}" target="{tgt}" parent="1"><mxGeometry relative="1" as="geometry"/></mxCell>')

def label_only(x, y, w, h, text, font_size=13, color="#333333", bold=False):
    cid = new_id()
    b = "1" if bold else "0"
    cells.append(f'<mxCell id="{cid}" value="{xml_escape(text)}" style="text;html=1;strokeColor=none;fillColor=none;align=center;verticalAlign=middle;whiteSpace=wrap;rounded=0;fontSize={font_size};fontColor={color};fontStyle={b};" vertex="1" parent="1"><mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return cid

# ─── SECTION 0: TITLE ───────────────────────────────────────────────
# Center of canvas around x=1200
title = box(950, 50, 500, 90, "HOW TO TRADE THE NEWS", fill="#0f3460", font_size=26, border="#e94560")

# Agenda bubbles branching down from title
agenda_items = [
    ("Why News Moves Markets", "#e94560"),
    ("The Economic Calendar", "#533483"),
    ("The Three Windows", "#0f3460"),
    ("Risk Management", "#c84b31"),
    ("Common Mistakes", "#2b2d42"),
]
agenda_ids = []
for i, (item, color) in enumerate(agenda_items):
    ax = 500 + i * 260
    aid = box(ax, 220, 220, 55, item, fill=color, font_size=13)
    agenda_ids.append(aid)
    arrow(title, aid, color=color)

# ─── SECTION 1: WHY NEWS MOVES MARKETS (x=200) ──────────────────────
sec1_y = 450
label_only(100, sec1_y - 50, 600, 40, "WHY NEWS MOVES MARKETS", font_size=18, color="#e94560", bold=True)

nr = box(250, sec1_y, 200, 55, "News Release", fill="#e94560")
ev = box(250, sec1_y + 110, 200, 55, "Expectation vs Reality", fill="#c84b31")
pm = box(250, sec1_y + 220, 200, 55, "Price Move = Opportunity", fill="#0f3460")
arrow(nr, ev, color="#e94560")
arrow(ev, pm, color="#c84b31")

# Three outcomes
beat = box(50, sec1_y + 360, 150, 55, "BEATS ↑\nBullish move", fill="#2d6a4f", font_size=12)
meet = box(225, sec1_y + 360, 150, 55, "MEETS →\nNo move", fill="#555555", font_size=12)
miss = box(400, sec1_y + 360, 150, 55, "MISSES ↓\nBearish move", fill="#c84b31", font_size=12)
arrow(pm, beat, color="#2d6a4f")
arrow(pm, meet, color="#555555")
arrow(pm, miss, color="#c84b31")

# ─── SECTION 2: ECONOMIC CALENDAR (x=800) ───────────────────────────
sec2_x = 800
sec2_y = 450
label_only(sec2_x, sec2_y - 50, 600, 40, "THE ECONOMIC CALENDAR", font_size=18, color="#533483", bold=True)

cal_header = box(sec2_x + 50, sec2_y, 500, 55, "ForexFactory · Investing.com · TradingEconomics", fill="#533483", font_size=13)

cols = ["Event", "Previous", "Forecast", "Actual", "Impact"]
col_colors = ["#2b2d42", "#2b2d42", "#2b2d42", "#2b2d42", "#e94560"]
for i, (col, col_color) in enumerate(zip(cols, col_colors)):
    box(sec2_x + 50 + i*100, sec2_y + 80, 95, 45, col, fill=col_color, font_size=12)

label_only(sec2_x + 50, sec2_y + 145, 500, 30, "Focus on RED / HIGH-IMPACT events only", font_size=12, color="#e94560", bold=True)

tier1 = [
    ("Fed / FOMC", "#e94560"),
    ("Non-Farm Payrolls", "#c84b31"),
    ("CPI (Inflation)", "#c84b31"),
    ("Central Bank Decisions", "#533483"),
    ("Earnings Season", "#0f3460"),
]
label_only(sec2_x + 50, sec2_y + 185, 200, 30, "TIER 1 EVENTS:", font_size=13, color="#333333", bold=True)
for i, (item, color) in enumerate(tier1):
    box(sec2_x + 50 + (i % 3) * 170, sec2_y + 225 + (i // 3) * 65, 155, 50, item, fill=color, font_size=12)

# ─── SECTION 3: THE THREE WINDOWS (x=1550) ──────────────────────────
sec3_x = 1550
sec3_y = 450
label_only(sec3_x, sec3_y - 50, 720, 40, "THE THREE WINDOWS", font_size=18, color="#0f3460", bold=True)

pre = box(sec3_x, sec3_y, 210, 65, "PRE-EVENT", fill="#0f3460", font_size=16)
at  = box(sec3_x + 250, sec3_y, 210, 65, "AT RELEASE", fill="#533483", font_size=16)
post= box(sec3_x + 500, sec3_y, 210, 65, "POST-EVENT", fill="#2d6a4f", font_size=16)

# Pre checklist
pre_items = ["Know consensus number", "Know previous number", "Size down 25–50%", "Identify key levels", "Write your plan"]
for i, item in enumerate(pre_items):
    box(sec3_x, sec3_y + 100 + i*60, 210, 50, f"✓  {item}", fill="#1a3a5c", font_size=11, bold=False)

# At release
fakeout = box(sec3_x + 250, sec3_y + 100, 210, 55, "Wait 1st 60 sec\n(chaos — stay out)", fill="#7b2d8b", font_size=11)
entries = ["Retest Entry", "Consolidation Breakout", "Level-to-Level"]
for i, e in enumerate(entries):
    box(sec3_x + 250, sec3_y + 175 + i*65, 210, 55, e, fill="#533483", font_size=12)

# Post event
post_items = ["Wait for spike + consolidation", "Enter continuation", "Stop below consol low (long)", "Institutions repositioning = hours/days"]
for i, item in enumerate(post_items):
    box(sec3_x + 500, sec3_y + 100 + i*65, 210, 55, item, fill="#1a4a35", font_size=11, bold=False)

# ─── SECTION 4: RISK MANAGEMENT (x=2350) ────────────────────────────
sec4_x = 2350
sec4_y = 450
label_only(sec4_x, sec4_y - 50, 700, 40, "RISK MANAGEMENT", font_size=18, color="#c84b31", bold=True)

rules = [
    ("RULE 1", "Size down. Every time.", "#c84b31"),
    ("RULE 2", "Define stop BEFORE entry.\nFactor in slippage.", "#e94560"),
    ("RULE 3", "In a position? Close it\nor hedge it before news.", "#533483"),
    ("RULE 4", "Know your market's risks.\nNo two are the same.", "#0f3460"),
]
for i, (rule, desc, color) in enumerate(rules):
    box(sec4_x + (i%2)*330, sec4_y + (i//2)*150, 140, 50, rule, fill=color, font_size=15)
    box(sec4_x + (i%2)*330 + 145, sec4_y + (i//2)*150, 175, 50, desc, fill="#2b2d42", font_size=11, bold=False)

# Market grid
markets = [
    ("FUTURES", "Limit moves\nSlippage common", "#0f3460"),
    ("FOREX",   "Spreads 10x normal\nHigh liquidity", "#533483"),
    ("CRYPTO",  "No circuit breakers\n24/7 extreme moves", "#c84b31"),
    ("STOCKS",  "Earnings halts\nGap risk overnight", "#2d6a4f"),
]
label_only(sec4_x, sec4_y + 360, 700, 30, "MARKET-SPECIFIC RISKS:", font_size=13, color="#333333", bold=True)
for i, (mkt, note, color) in enumerate(markets):
    bx = sec4_x + (i%2)*330
    by = sec4_y + 400 + (i//2)*120
    box(bx, by, 140, 100, mkt, fill=color, font_size=14)
    box(bx+145, by, 175, 100, note, fill="#f5f5f5", font_color="#333333", font_size=11, bold=False, border="#cccccc")

# ─── SECTION 5: COMMON MISTAKES (x=3150) ────────────────────────────
sec5_x = 3150
sec5_y = 450
label_only(sec5_x, sec5_y - 50, 700, 40, "COMMON MISTAKES", font_size=18, color="#2b2d42", bold=True)

wrongs = [
    ("Chasing the move", "Spike happened, you weren't in.\nYou buy the top — market reverses."),
    ("Letting winner → loser", "Trade is green, you get greedy.\nIt reverses. Define target BEFORE."),
    ("Sizing up on 'obvious' trades", "No sure thing in markets.\nThe market humbles the confident."),
]
for i, (mistake, fix) in enumerate(wrongs):
    box(sec5_x, sec5_y + i*160, 220, 65, f"✗  {mistake}", fill="#c84b31", font_size=12)
    box(sec5_x + 240, sec5_y + i*160, 280, 65, fix, fill="#2b2d42", font_size=11, bold=False)

# Closing quote
box(sec5_x, sec5_y + 520, 520, 80,
    '"Trade the market you see,\nnot the market you think you\'ll see"',
    fill="#0f3460", font_size=15, border="#e94560")

# ─── BUILD XML ───────────────────────────────────────────────────────
xml = '''<?xml version="1.0" encoding="UTF-8"?>
<mxfile host="app.diagrams.net" modified="2026-03-21" version="21.0.0">
  <diagram name="How To Trade The News" id="trade-the-news">
    <mxGraphModel dx="1200" dy="800" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="0" pageScale="1" pageWidth="1654" pageHeight="1169" math="0" shadow="0" background="#ffffff">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
'''
xml += '\n'.join(cells)
xml += '''
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>'''

with open('/root/.openclaw/workspace/.tmp/how_to_trade_the_news.drawio', 'w') as f:
    f.write(xml)

print("Done — saved to how_to_trade_the_news.drawio")
