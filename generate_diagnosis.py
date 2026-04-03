from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import simpleSplit
from datetime import datetime
import math
import json
import sys
import os

# ── Font registration (auto-download Liberation fonts) ──────────────────────

_font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts')
pdfmetrics.registerFont(TTFont('Serif',       os.path.join(_font_dir, 'LiberationSerif-Regular.ttf')))
pdfmetrics.registerFont(TTFont('SerifBold',   os.path.join(_font_dir, 'LiberationSerif-Bold.ttf')))
pdfmetrics.registerFont(TTFont('SerifItalic', os.path.join(_font_dir, 'LiberationSerif-Italic.ttf')))
pdfmetrics.registerFont(TTFont('Sans',        os.path.join(_font_dir, 'LiberationSans-Regular.ttf')))
pdfmetrics.registerFont(TTFont('SansBold',    os.path.join(_font_dir, 'LiberationSans-Bold.ttf')))

BG       = HexColor('#0c0c0a')
CARD     = HexColor('#131311')
RULE     = HexColor('#1e1c18')
GOLD     = HexColor('#a8865c')
GOLD_LT  = HexColor('#c4a06a')
GOLD_DK  = HexColor('#3a2e1e')
CREAM    = HexColor('#e0d8c8')
CREAM_DM = HexColor('#7a7268')
CREAM_FT = HexColor('#242018')
IDEAL_CL = HexColor('#3a4a5a')

W, H = A4
MAR  = 18 * mm
TW   = W - 2 * MAR
def bg(c):
    c.setFillColor(BG); c.rect(0, 0, W, H, fill=1, stroke=0)

def hdr(c, left='THE SECOND LIFE', right=''):
    c.setFont('Sans', 6.5); c.setFillColor(HexColor('#302e28'))
    c.drawString(MAR, H - 11*mm, left)
    if right: c.drawRightString(W - MAR, H - 11*mm, right)
    c.setStrokeColor(RULE); c.setLineWidth(0.3)
    c.line(MAR, H - 13.5*mm, W - MAR, H - 13.5*mm)

def ftr(c, name):
    c.setStrokeColor(RULE); c.setLineWidth(0.3)
    c.line(MAR, 16*mm, W - MAR, 16*mm)
    c.setFont('Sans', 6); c.setFillColor(HexColor('#302e28'))
    c.drawString(MAR, 11*mm, 'CONFIDENTIAL — For personal reflection only. Not medical or psychological advice.')
    c.drawRightString(W - MAR, 11*mm, f'Identity Diagnosis — {name}')

def rl(c, x, y, w=None, col=RULE, t=0.35):
    if w is None: w = TW
    c.setStrokeColor(col); c.setLineWidth(t); c.line(x, y, x+w, y)

def micro(c, txt, x, y, col=CREAM_DM, font='SansBold', sz=6.5):
    c.setFont(font, sz); c.setFillColor(col); c.drawString(x, y, txt.upper())

def wrap(c, txt, x, y, w, font='Serif', sz=10, col=CREAM, ld=15):
    c.setFont(font, sz); c.setFillColor(col)
    for ln in simpleSplit(txt, font, sz, w):
        c.drawString(x, y, ln); y -= ld
    return y

def wh(txt, font, sz, w, ld=15):
    return len(simpleSplit(txt, font, sz, w)) * ld
def draw_radar(c, cx, cy, R, scores):
    keys   = ['surfaceAlignment','internalAlignment','nextVersionAlignment','deathbedAlignment']
    angles = [90, 0, 270, 180]
    labels = ['Surface','Internal','Next\nVersion','Deathbed']
    vals   = [min(100, max(0, scores.get(k,{}).get('value',0))) for k in keys]
    ideal  = [88, 85, 88, 82]

    def pt(a, r):
        rad = math.radians(a)
        return cx + r*math.cos(rad), cy + r*math.sin(rad)

    for pct in [25, 50, 75, 100]:
        pts = [pt(a, R*pct/100) for a in angles]
        p = c.beginPath(); p.moveTo(*pts[0])
        for q in pts[1:]: p.lineTo(*q)
        p.close()
        c.setStrokeColor(CREAM_FT); c.setLineWidth(0.3); c.drawPath(p, stroke=1, fill=0)

    for a in angles:
        c.setStrokeColor(CREAM_FT); c.setLineWidth(0.3)
        c.line(cx, cy, *pt(a, R))

    ipts = [pt(angles[i], R*ideal[i]/100) for i in range(4)]
    c.setStrokeColor(IDEAL_CL); c.setLineWidth(0.8); c.setDash([2,3])
    p = c.beginPath(); p.moveTo(*ipts[0])
    for q in ipts[1:]: p.lineTo(*q)
    p.close(); c.drawPath(p, stroke=1, fill=0); c.setDash([])

    dpts = [pt(angles[i], R*vals[i]/100) for i in range(4)]
    p = c.beginPath(); p.moveTo(*dpts[0])
    for q in dpts[1:]: p.lineTo(*q)
    p.close()
    c.setFillColor(HexColor('#1e1810')); c.setStrokeColor(GOLD); c.setLineWidth(1.5)
    c.drawPath(p, stroke=1, fill=1)
    for q in dpts:
        c.setFillColor(GOLD_LT); c.circle(q[0], q[1], 2.5, fill=1, stroke=0)

    for i,(a,lbl) in enumerate(zip(angles, labels)):
        lx, ly = pt(a, R+16)
        c.setFont('Sans', 6.5); c.setFillColor(CREAM_DM)
        lines = lbl.split('\n')
        for j,ln in enumerate(lines):
            c.drawCentredString(lx, ly - j*8, ln)

    leg_y = cy - R - 11*mm
    c.setFillColor(GOLD); c.rect(cx-18*mm, leg_y, 7, 4.5, fill=1, stroke=0)
    c.setFont('Sans', 6); c.setFillColor(CREAM_DM)
    c.drawString(cx-18*mm+9, leg_y+0.5, 'Your map')
    c.setStrokeColor(IDEAL_CL); c.setLineWidth(0.8); c.setDash([2,3])
    c.rect(cx+2*mm, leg_y, 7, 4.5, stroke=1, fill=0); c.setDash([])
    c.drawString(cx+2*mm+9, leg_y+0.5, 'Fully aligned')
def generate(data, path):
    c    = canvas.Canvas(path, pagesize=A4)
    name = data.get('firstName','You')
    today = datetime.now().strftime('%B %d, %Y')

    bg(c); hdr(c, 'THE SECOND LIFE', 'IDENTITY DIAGNOSIS')
    y = H - 22*mm

    c.setFillColor(GOLD_DK)
    c.roundRect(MAR, y-4.5*mm, 27*mm, 4.5*mm, 2, fill=1, stroke=0)
    c.setFont('SansBold', 6); c.setFillColor(GOLD)
    c.drawString(MAR+3*mm, y-3*mm, 'CONFIDENTIAL')
    y -= 4.5*mm + 7*mm

    c.setFont('SerifItalic', 28); c.setFillColor(CREAM)
    c.drawString(MAR, y, 'Your Identity Diagnosis')
    y -= 9*mm

    c.setFont('SansBold', 9); c.setFillColor(GOLD)
    c.drawString(MAR, y, f'— {name}')
    c.setFont('Sans', 8); c.setFillColor(CREAM_DM)
    c.drawRightString(W-MAR, y, today)
    y -= 7*mm

    rl(c, MAR, y, TW, GOLD_DK, 0.6); y -= 10*mm

    align_range = data.get('alignmentRange','29–43% aligned')
    try:
        nums = [int(s.replace('%','').strip()) for s in align_range.replace('–','-').split('-')]
        mis  = f"{100-nums[1]}–{100-nums[0]}% misaligned"
    except:
        mis = "57–71% misaligned"

    micro(c, 'Your misalignment score', MAR, y); y -= 11*mm
    c.setFont('SerifBold', 40); c.setFillColor(GOLD_LT)
    c.drawString(MAR, y, mis); y -= 8*mm
    y = wrap(c, data.get('alignmentSummary',''), MAR, y, TW, 'SerifItalic', 10.5, CREAM_DM, 14)
    y -= 11*mm

    rl(c, MAR, y, TW); y -= 10*mm

    y = wrap(c, data.get('introContext',''), MAR, y, TW, 'Serif', 9.5, CREAM_DM, 14)
    y -= 5*mm
    c.setFont('SerifItalic', 9); c.setFillColor(GOLD)
    c.drawString(MAR, y, 'Read what follows slowly. Some of it will sting. That\'s how you\'ll know it\'s accurate.')
    y -= 12*mm

    rl(c, MAR, y, TW); y -= 10*mm

    micro(c, "What's actually happening", MAR, y); y -= 8*mm
    y = wrap(c, data.get('tldr',''), MAR, y, TW, 'Serif', 10.5, CREAM, 16)
    y -= 10*mm
    rl(c, MAR, y, TW, GOLD_DK, 0.5)

    ftr(c, name); c.showPage()

    bg(c); hdr(c, 'THE SECOND LIFE', f'{name.upper()} — PATTERN ANALYSIS')
    y = H - 21*mm

    wound  = data.get('wound',{})
    belief_h = wh(f'"{wound.get("belief","")}"', 'SerifItalic', 9, TW-10*mm, 12)
    origin_h = wh(wound.get('origin',''), 'Serif', 8.5, TW-10*mm, 11)
    adult_h  = wh('Now: '+wound.get('adultSignature',''), 'SansBold', 7.5, TW-10*mm, 10)
    card_h   = belief_h + origin_h + adult_h + 24*mm

    c.setFillColor(CARD)
    c.roundRect(MAR, y-card_h, TW, card_h, 3, fill=1, stroke=0)
    c.setFillColor(GOLD); c.rect(MAR, y-card_h, 2.5, card_h, fill=1, stroke=0)

    wy = y - 5*mm
    micro(c, 'The Original Program', MAR+5*mm, wy, GOLD); wy -= 6*mm
    c.setFont('SerifBold', 13); c.setFillColor(CREAM)
    c.drawString(MAR+5*mm, wy, wound.get('name','')); wy -= 7*mm
    wy = wrap(c, f'"{wound.get("belief","")}"', MAR+5*mm, wy, TW-10*mm, 'SerifItalic', 9, CREAM_DM, 12)
    wy -= 3*mm
    wy = wrap(c, wound.get('origin',''), MAR+5*mm, wy, TW-10*mm, 'Serif', 8.5, CREAM_DM, 11)
    wy -= 3*mm
    wrap(c, 'Now: '+wound.get('adultSignature',''), MAR+5*mm, wy, TW-10*mm, 'SansBold', 7.5, GOLD, 10)

    y = y - card_h - 7*mm

    micro(c, 'The Misalignment Gap', MAR, y); y -= 6*mm
    gaps  = data.get('gaps',[])
    col_w = (TW - 8*mm) / 2
    for gap in gaps:
        rh = 14*mm
        c.setFillColor(CARD); c.roundRect(MAR, y-rh, col_w, rh, 2, fill=1, stroke=0)
        micro(c, 'Living like', MAR+3*mm, y-3.5*mm, CREAM_DM)
        wrap(c, gap.get('living',''), MAR+3*mm, y-8*mm, col_w-5*mm, 'Serif', 7.5, CREAM, 10)
        c.setFont('SansBold', 9); c.setFillColor(GOLD_LT)
        c.drawCentredString(MAR+col_w+4*mm, y-rh/2, '→')
        rx = MAR+col_w+8*mm
        c.setFillColor(CARD); c.roundRect(rx, y-rh, col_w, rh, 2, fill=1, stroke=0)
        c.setFillColor(GOLD_DK); c.rect(rx, y-rh, 2, rh, fill=1, stroke=0)
        micro(c, 'Actually', rx+3*mm, y-3.5*mm, GOLD)
        wrap(c, gap.get('versus',''), rx+3*mm, y-8*mm, col_w-5*mm, 'Serif', 7.5, CREAM, 10)
        y -= rh + 2.5*mm

    y -= 6*mm

    radar_w = 62*mm
    score_x = MAR + radar_w + 8*mm
    score_w = TW - radar_w - 8*mm

    micro(c, '4 Alignment Axes', MAR, y)
    micro(c, 'Alignment Scores', score_x, y)
    y -= 5*mm

    radar_cx = MAR + radar_w/2
    radar_cy = y - 28*mm
    draw_radar(c, radar_cx, radar_cy, 22*mm, data.get('scores',{}))

    sy = y
    sc = data.get('scores',{})
    score_meta = [
        ('surfaceAlignment',     'Surface',      'How much external life reflects real values'),
        ('internalAlignment',    'Internal',     'How connected you are to what you actually want'),
        ('nextVersionAlignment', 'Next Version', "How close you are to who you're built to become"),
        ('deathbedAlignment',    'Deathbed',     "How much you'd regret this path at life's end"),
    ]
    for key, lbl, exp in score_meta:
        s   = sc.get(key,{})
        val = int(s.get('value',0))
        why = s.get('why','')
        micro(c, lbl, score_x, sy)
        c.setFont('SerifBold', 14); c.setFillColor(GOLD_LT)
        c.drawRightString(score_x+score_w, sy+2, f"{val}%")
        sy -= 7
        c.setFont('SerifItalic', 6.5); c.setFillColor(HexColor('#3a3830'))
        c.drawString(score_x, sy, exp); sy -= 7
        c.setFillColor(CREAM_FT)
        c.roundRect(score_x, sy, score_w, 3, 1.5, fill=1, stroke=0)
        fw = max(3, score_w*val/100)
        c.setFillColor(GOLD); c.roundRect(score_x, sy, fw, 3, 1.5, fill=1, stroke=0)
        sy -= 9
        for ln in simpleSplit(why, 'Serif', 7.5, score_w)[:2]:
            c.setFont('Serif', 7.5); c.setFillColor(CREAM_DM)
            c.drawString(score_x, sy, ln); sy -= 9
        sy -= 4

    insight_y   = min(radar_cy - 24*mm, sy) - 12*mm
    belief_text = wound.get('belief','')
    insight_h   = wh(f'"{belief_text}"', 'SerifItalic', 10.5, TW-12*mm, 15) + 14*mm

    if insight_y - insight_h > 22*mm:
        c.setFillColor(HexColor('#0f0f0d'))
        c.roundRect(MAR, insight_y-insight_h, TW, insight_h, 3, fill=1, stroke=0)
        c.setFillColor(GOLD_DK)
        c.rect(MAR, insight_y-insight_h, 2, insight_h, fill=1, stroke=0)
        micro(c, 'The belief running your life', MAR+6*mm, insight_y-5*mm, CREAM_DM)
        wrap(c, f'"{belief_text}"', MAR+6*mm, insight_y-11*mm, TW-12*mm, 'SerifItalic', 10.5, CREAM_DM, 15)

    ftr(c, name); c.showPage()

    bg(c); hdr(c, 'THE SECOND LIFE', f'{name.upper()} — FULL ANALYSIS')
    y = H - 21*mm
    micro(c, 'Full Analysis', MAR, y); y -= 9*mm

    raw_paras  = [p.strip() for p in data.get('analysis','').split('\n\n') if p.strip()]
    body_paras = raw_paras[:-1]

    bridge_1 = (
        f"I've worked with hundreds of people who got to exactly this moment. "
        f"Read something that named their pattern, felt it land, recognized themselves completely. "
        f"Most sat with that feeling and moved on. "
        f"On average it takes people 247 days between the moment they understand what's running their life "
        f"and the moment they actually do something about it."
    )
    bridge_2 = (
        f"{name}, you answered these questions honestly. You didn't filter. You went there. "
        f"A smaller group treated the moment of recognition as the starting point. "
        f"Those are the ones whose lives actually changed. "
        f"That already tells me which group you're in."
    )
    bridge_3 = (
        f"There's one more piece I want you to read. "
        f"It's about why the clarity you're feeling right now almost never becomes change on its own — "
        f"and what the people who actually shift do differently."
    )

    disc = ("This document is a reflective tool for personal insight only. It is not a clinical assessment, "
            "psychological evaluation, or substitute for professional mental health care. The analysis is based "
            "solely on your self-reported answers and does not constitute medical, psychiatric, therapeutic, or "
            "legal advice of any kind. Benoit Malige and The Second Life are not licensed mental health "
            "professionals. If you are experiencing emotional distress, thoughts of self-harm, or a mental health "
            "crisis, please contact a qualified healthcare provider or a crisis helpline immediately. By reading "
            "this document you acknowledge that it is intended for self-reflection purposes only and that you "
            "assume full responsibility for any decisions made as a result of reading it.")

    b1h = wh(bridge_1, 'Serif', 9.5, TW-10*mm, 15)
    b2h = wh(bridge_2, 'Serif', 9.5, TW-10*mm, 15)
    b3h = wh(bridge_3, 'Serif', 9.5, TW-10*mm, 15)
    bridge_card_h = b1h + b2h + b3h + 38*mm
    disc_h = wh(disc, 'Sans', 7, TW, 10) + 14*mm

    for i, para in enumerate(body_paras):
        est_h = wh(para, 'Serif', 10.5, TW, 17) + 14*mm
        if y - est_h < 22*mm:
            ftr(c, name); c.showPage()
            bg(c); hdr(c, 'THE SECOND LIFE', f'{name.upper()} — FULL ANALYSIS')
            y = H - 21*mm
        y = wrap(c, para, MAR, y, TW, 'Serif', 10.5, CREAM, 17)
        y -= 10*mm
        if i < len(body_paras) - 1:
            c.setFillColor(GOLD_DK)
            c.circle(W/2, y+4*mm, 1.5, fill=1, stroke=0)
            y -= 2*mm

    if y - bridge_card_h - disc_h < 22*mm:
        ftr(c, name); c.showPage()
        bg(c); hdr(c, 'THE SECOND LIFE', f'{name.upper()} — FULL ANALYSIS')
        y = H - 21*mm

    total_card_h = b1h + b2h + b3h + 36*mm
    c.setFillColor(CARD)
    c.roundRect(MAR, y-total_card_h, TW, total_card_h, 3, fill=1, stroke=0)
    c.setFillColor(GOLD_DK)
    c.rect(MAR, y-total_card_h, 2.5, total_card_h, fill=1, stroke=0)

    cy2 = y - 5*mm
    cy2 = wrap(c, bridge_1, MAR+5*mm, cy2, TW-10*mm, 'Serif', 9.5, CREAM_DM, 15)
    cy2 -= 5*mm
    rl(c, MAR+5*mm, cy2, TW-10*mm, RULE, 0.3)
    cy2 -= 6*mm
    cy2 = wrap(c, bridge_2, MAR+5*mm, cy2, TW-10*mm, 'Serif', 9.5, CREAM, 15)
    cy2 -= 5*mm
    rl(c, MAR+5*mm, cy2, TW-10*mm, RULE, 0.3)
    cy2 -= 6*mm
    cy2 = wrap(c, bridge_3, MAR+5*mm, cy2, TW-10*mm, 'SerifItalic', 9.5, CREAM, 15)
    cy2 -= 6*mm
    link = 'Read: The Awareness Trap  →'
    c.setFont('SansBold', 8); c.setFillColor(GOLD)
    c.drawString(MAR+5*mm, cy2, link)
    lw = c.stringWidth(link, 'SansBold', 8)
    c.linkURL('https://dep-awareness.carrd.co',
              (MAR+5*mm, cy2-2, MAR+5*mm+lw, cy2+9), relative=0)

    y = y - total_card_h - 8*mm
    rl(c, MAR, y, TW); y -= 7*mm
    micro(c, 'Important Notice', MAR, y); y -= 6*mm
    wrap(c, disc, MAR, y, TW, 'Sans', 7, CREAM_DM, 10)

    ftr(c, name); c.save()
    print(f"PDF saved: {path}")
if __name__ == '__main__':
    if len(sys.argv) == 3:
        with open(sys.argv[1]) as f:
            data = json.load(f)
        generate(data, sys.argv[2])
    else:
        print("Usage: python generate_diagnosis.py input.json output.pdf")
