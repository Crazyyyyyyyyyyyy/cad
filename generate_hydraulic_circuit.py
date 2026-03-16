#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXB360 挖掘机行走液压回路图生成脚本
Generate EXB360 Excavator Travel Hydraulic Circuit DXF (AutoCAD 2025 compatible)

Components included / 包含元件:
  - 变量液压泵 (Variable displacement piston pump)
  - 先导控制阀 (Pilot control valve)
  - 行走换向阀 (3-position 4-way travel directional control valve)
  - 左/右行走马达 (Left / Right travel hydraulic motors, 2-speed)
  - 平衡阀 (Counterbalance / brake valves)
  - 主溢流阀 (Main relief valve)
  - 单向阀 (Check valves)
  - 吸/回油过滤器 (Suction and return filters)
  - 压力表 (Pressure gauges)
  - 二速电磁阀 (2-speed solenoid valves)
  - 油箱 (Hydraulic reservoir)
"""

import math
import ezdxf
from ezdxf.enums import TextEntityAlignment

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _layer(name):
    return {"layer": name}


def arrowhead(msp, tip, angle_deg, size=4, layer="元件轮廓"):
    """Draw a filled-looking arrowhead at *tip* pointing in *angle_deg*."""
    a = math.radians(angle_deg)
    w = size * 0.38
    bx = tip[0] - size * math.cos(a)
    by = tip[1] - size * math.sin(a)
    w1x = bx + w * math.sin(a)
    w1y = by - w * math.cos(a)
    w2x = bx - w * math.sin(a)
    w2y = by + w * math.cos(a)
    msp.add_lwpolyline(
        [tip, (w1x, w1y), (w2x, w2y), tip],
        dxfattribs=_layer(layer),
    )


def text(msp, s, x, y, h=5, layer="文字标注", align=TextEntityAlignment.LEFT):
    msp.add_text(s, dxfattribs={"layer": layer, "height": h}).set_placement(
        (x, y), align=align
    )


def hline(msp, x1, y, x2, layer="液压线路"):
    msp.add_line((x1, y), (x2, y), dxfattribs=_layer(layer))


def vline(msp, x, y1, y2, layer="液压线路"):
    msp.add_line((x, y1), (x, y2), dxfattribs=_layer(layer))


def rect(msp, cx, cy, w, h, layer="元件轮廓"):
    hw, hh = w / 2, h / 2
    msp.add_lwpolyline(
        [
            (cx - hw, cy - hh),
            (cx + hw, cy - hh),
            (cx + hw, cy + hh),
            (cx - hw, cy + hh),
            (cx - hw, cy - hh),
        ],
        dxfattribs=_layer(layer),
    )


# ---------------------------------------------------------------------------
# Hydraulic symbol drawers
# ---------------------------------------------------------------------------

def draw_tank(msp, cx, cy, w=70, h=35):
    """油箱 – open-top reservoir symbol."""
    rect(msp, cx, cy + h / 2, w, h)
    # fluid level dashed line
    msp.add_line(
        (cx - w / 2 + 6, cy + h * 0.65),
        (cx + w / 2 - 6, cy + h * 0.65),
        dxfattribs={"layer": "虚线"},
    )
    text(msp, "油  箱", cx - 12, cy + h + 4, h=6)
    text(msp, "Hydraulic Tank", cx - 22, cy - 7, h=4)


def draw_variable_pump(msp, cx, cy, r=22):
    """变量液压泵 – circle + inward triangle + diagonal variable arrow."""
    msp.add_circle((cx, cy), r, dxfattribs=_layer("元件轮廓"))
    t = r * 0.62
    # triangle (filled outline – pointing right, pump output)
    msp.add_lwpolyline(
        [
            (cx - t * 0.55, cy - t * 0.72),
            (cx + t * 0.85, cy),
            (cx - t * 0.55, cy + t * 0.72),
            (cx - t * 0.55, cy - t * 0.72),
        ],
        dxfattribs=_layer("元件轮廓"),
    )
    # variable-displacement diagonal arrow
    msp.add_line(
        (cx - r * 0.82, cy - r * 0.82),
        (cx + r * 0.82, cy + r * 0.82),
        dxfattribs=_layer("元件轮廓"),
    )
    arrowhead(msp, (cx + r * 0.82, cy + r * 0.82), 45, size=5)
    text(msp, "变量液压泵", cx + r + 4, cy + 4, h=6)
    text(msp, "Variable Pump", cx + r + 4, cy - 7, h=4)


def draw_motor(msp, cx, cy, r=26, label_left=True):
    """双速液压马达 – circle + outward triangle + variable arrow."""
    msp.add_circle((cx, cy), r, dxfattribs=_layer("元件轮廓"))
    t = r * 0.60
    # triangle pointing left (motor output = shaft on left side)
    msp.add_lwpolyline(
        [
            (cx + t * 0.55, cy - t * 0.72),
            (cx - t * 0.85, cy),
            (cx + t * 0.55, cy + t * 0.72),
            (cx + t * 0.55, cy - t * 0.72),
        ],
        dxfattribs=_layer("元件轮廓"),
    )
    # variable diagonal arrow
    msp.add_line(
        (cx - r * 0.82, cy - r * 0.82),
        (cx + r * 0.82, cy + r * 0.82),
        dxfattribs=_layer("元件轮廓"),
    )
    arrowhead(msp, (cx + r * 0.82, cy + r * 0.82), 45, size=5)


def draw_relief_valve(msp, cx, cy, sz=16):
    """溢流阀 – square with diagonal arrow and spring."""
    rect(msp, cx, cy, sz, sz)
    # diagonal arrow inside
    msp.add_line(
        (cx - sz / 2 + 2, cy - sz / 2 + 2),
        (cx + sz / 2 - 2, cy + sz / 2 - 2),
        dxfattribs=_layer("元件轮廓"),
    )
    arrowhead(msp, (cx + sz / 2 - 2, cy + sz / 2 - 2), 45, size=3)
    # spring (zigzag arcs above)
    for i in range(3):
        y0 = cy + sz / 2 + i * 4
        msp.add_arc((cx, y0 + 2), 2, 0, 180, dxfattribs=_layer("元件轮廓"))
    # pilot drain line (dashed – pressure sensing)
    msp.add_line(
        (cx + sz / 2, cy),
        (cx + sz / 2 + 12, cy),
        dxfattribs={"layer": "虚线"},
    )


def draw_check_valve(msp, cx, cy, size=9, vertical=True):
    """单向阀 – triangle + blocking bar."""
    if vertical:
        # flow upward
        msp.add_lwpolyline(
            [
                (cx, cy - size),
                (cx - size * 0.65, cy + size * 0.55),
                (cx + size * 0.65, cy + size * 0.55),
                (cx, cy - size),
            ],
            dxfattribs=_layer("元件轮廓"),
        )
        msp.add_line(
            (cx - size * 0.75, cy + size * 0.55),
            (cx + size * 0.75, cy + size * 0.55),
            dxfattribs=_layer("元件轮廓"),
        )
    else:
        # flow rightward
        msp.add_lwpolyline(
            [
                (cx - size, cy),
                (cx + size * 0.55, cy - size * 0.65),
                (cx + size * 0.55, cy + size * 0.65),
                (cx - size, cy),
            ],
            dxfattribs=_layer("元件轮廓"),
        )
        msp.add_line(
            (cx + size * 0.55, cy - size * 0.75),
            (cx + size * 0.55, cy + size * 0.75),
            dxfattribs=_layer("元件轮廓"),
        )


def draw_filter(msp, cx, cy, sz=16):
    """过滤器 – diamond with cross-hatch lines."""
    msp.add_lwpolyline(
        [
            (cx, cy - sz / 2),
            (cx + sz / 2, cy),
            (cx, cy + sz / 2),
            (cx - sz / 2, cy),
            (cx, cy - sz / 2),
        ],
        dxfattribs=_layer("元件轮廓"),
    )
    # hatch lines inside
    for dy in [-sz * 0.18, 0, sz * 0.18]:
        half = sz / 2 * (1 - abs(dy) / (sz / 2)) * 0.75
        msp.add_line(
            (cx - half, cy + dy),
            (cx + half, cy + dy),
            dxfattribs=_layer("元件轮廓"),
        )


def draw_pressure_gauge(msp, cx, cy, r=7):
    """压力表 – circle with needle."""
    msp.add_circle((cx, cy), r, dxfattribs=_layer("元件轮廓"))
    msp.add_line(
        (cx, cy),
        (cx + r * 0.55, cy + r * 0.55),
        dxfattribs=_layer("元件轮廓"),
    )
    # connection nub at bottom
    vline(msp, cx, cy - r, cy - r - 6)


def draw_counterbalance_valve(msp, cx, cy, sz=20):
    """平衡阀 – square housing containing pilot check + relief."""
    rect(msp, cx, cy, sz, sz)
    # inner circle = pilot-operated check
    msp.add_circle((cx, cy), sz * 0.28, dxfattribs=_layer("元件轮廓"))
    # small spring marks at top
    for i in range(2):
        y0 = cy + sz / 2 - 6 + i * 3
        msp.add_arc((cx, y0), 1.5, 0, 180, dxfattribs=_layer("元件轮廓"))


def draw_solenoid_valve(msp, cx, cy, sz=14):
    """二速电磁阀 – rectangle with solenoid actuator symbol."""
    rect(msp, cx, cy, sz, sz * 0.55)
    # solenoid coil symbol (stacked rectangles) on right
    for i in range(2):
        rect(
            msp,
            cx + sz / 2 + 5 + i * 6,
            cy,
            5,
            sz * 0.5,
            layer="元件轮廓",
        )


def draw_3pos4way_valve(msp, cx, cy, bw=32, bh=30):
    """三位四通行走换向阀 (pilot-operated spring-centred)."""
    # Three valve position boxes
    for i in range(3):
        bx = cx - bw * 1.5 + i * bw
        msp.add_lwpolyline(
            [
                (bx, cy - bh / 2),
                (bx + bw, cy - bh / 2),
                (bx + bw, cy + bh / 2),
                (bx, cy + bh / 2),
                (bx, cy - bh / 2),
            ],
            dxfattribs=_layer("元件轮廓"),
        )

    # --- LEFT position: P→A, B→T (forward travel) ---
    lx = cx - bw * 1.5
    # P→A arrow (bottom-left to top-right)
    msp.add_line(
        (lx + 5, cy - bh / 2 + 5), (lx + bw - 5, cy + bh / 2 - 5),
        dxfattribs=_layer("元件轮廓"),
    )
    arrowhead(msp, (lx + bw - 5, cy + bh / 2 - 5), 50, size=4)
    # B→T arrow
    msp.add_line(
        (lx + bw - 5, cy - bh / 2 + 5), (lx + 5, cy + bh / 2 - 5),
        dxfattribs=_layer("元件轮廓"),
    )
    arrowhead(msp, (lx + 5, cy + bh / 2 - 5), 130, size=4)

    # --- CENTER position: all ports blocked (T-stop symbols) ---
    mx = cx - bw / 2
    # top blocked bar
    hline(msp, mx + 4, cy + bh / 2 - 5, mx + bw - 4, layer="元件轮廓")
    vline(msp, mx + 4, cy + bh / 2 - 5, cy, layer="元件轮廓")
    vline(msp, mx + bw - 4, cy + bh / 2 - 5, cy, layer="元件轮廓")
    # bottom blocked bar
    hline(msp, mx + 4, cy - bh / 2 + 5, mx + bw - 4, layer="元件轮廓")
    vline(msp, mx + 4, cy - bh / 2 + 5, cy, layer="元件轮廓")
    vline(msp, mx + bw - 4, cy - bh / 2 + 5, cy, layer="元件轮廓")

    # --- RIGHT position: P→B, A→T (reverse travel) ---
    rx = cx + bw / 2
    msp.add_line(
        (rx + bw - 5, cy - bh / 2 + 5), (rx + 5, cy + bh / 2 - 5),
        dxfattribs=_layer("元件轮廓"),
    )
    arrowhead(msp, (rx + 5, cy + bh / 2 - 5), 130, size=4)
    msp.add_line(
        (rx + 5, cy - bh / 2 + 5), (rx + bw - 5, cy + bh / 2 - 5),
        dxfattribs=_layer("元件轮廓"),
    )
    arrowhead(msp, (rx + bw - 5, cy + bh / 2 - 5), 50, size=4)

    # Pilot operators (dashed lines into valve ends)
    # Left pilot (forward)
    hline(msp, cx - bw * 1.5 - 28, cy, cx - bw * 1.5, layer="虚线")
    text(msp, "先导(前进)", cx - bw * 1.5 - 58, cy + 2, h=4.5)
    # Right pilot (reverse)
    hline(msp, cx + bw * 1.5, cy, cx + bw * 1.5 + 28, layer="虚线")
    text(msp, "先导(后退)", cx + bw * 1.5 + 30, cy + 2, h=4.5)

    # Spring return symbols on both ends (zigzag)
    for side in (-1, 1):
        bx_end = cx + side * bw * 1.5
        for i in range(3):
            xc = bx_end + side * (8 + i * 5)
            msp.add_arc((xc, cy), 2.5, 90, 270, dxfattribs=_layer("元件轮廓"))

    # Port labels P / T / A / B
    text(msp, "P", cx - 2, cy - bh / 2 - 10, h=6)
    text(msp, "T", cx - 2, cy + bh / 2 + 3, h=6)
    text(msp, "A", cx - bw * 1.5 - 9, cy - 2, h=6)
    text(msp, "B", cx + bw * 1.5 + 3, cy - 2, h=6)

    return bw * 3  # total valve width


# ---------------------------------------------------------------------------
# Title block
# ---------------------------------------------------------------------------

def draw_title_block(msp, W, H, margin=10):
    # Outer frame
    msp.add_lwpolyline(
        [(0, 0), (W, 0), (W, H), (0, H), (0, 0)],
        dxfattribs=_layer("标题栏"),
    )
    # Inner working frame (25mm left for binding)
    msp.add_lwpolyline(
        [
            (25, margin),
            (W - margin, margin),
            (W - margin, H - margin),
            (25, H - margin),
            (25, margin),
        ],
        dxfattribs=_layer("标题栏"),
    )
    # Title block box (bottom-right)
    tx, ty, tw, th = W - margin - 180, margin, 180, 55
    msp.add_lwpolyline(
        [
            (tx, ty),
            (tx + tw, ty),
            (tx + tw, ty + th),
            (tx, ty + th),
            (tx, ty),
        ],
        dxfattribs=_layer("标题栏"),
    )
    # Horizontal dividers inside title block
    msp.add_line((tx, ty + 38), (tx + tw, ty + 38), dxfattribs=_layer("标题栏"))
    msp.add_line((tx, ty + 22), (tx + tw, ty + 22), dxfattribs=_layer("标题栏"))
    msp.add_line((tx + 90, ty), (tx + 90, ty + 22), dxfattribs=_layer("标题栏"))

    text(msp, "EXB360 挖掘机行走液压回路图", tx + 4, ty + th - 11, h=8, layer="标题栏")
    text(msp, "Travel Hydraulic Circuit – EXB360 Excavator", tx + 4, ty + th - 22, h=5, layer="标题栏")
    text(msp, "图号: EXB360-HYD-TRV-001", tx + 4, ty + 27, h=5, layer="标题栏")
    text(msp, "比例: 1:1  单位: mm", tx + 4, ty + 13, h=5, layer="标题栏")
    text(msp, "图幅: A1", tx + 94, ty + 13, h=5, layer="标题栏")


def draw_legend(msp, lx, ly):
    """图例 legend box."""
    lw, lh = 115, 120
    rect(msp, lx + lw / 2, ly + lh / 2, lw, lh, layer="标题栏")
    text(msp, "图  例  Legend", lx + 18, ly + lh - 10, h=6, layer="标题栏")
    entries = [
        ("——————", "主压力油路 (High-pressure)"),
        ("- - - - - - -", "先导/泄油油路 (Pilot/Drain)"),
        ("○△ / ○", "变量泵 / 马达"),
        ("□ ×", "三位四通换向阀"),
        ("◇", "过滤器"),
        ("□ ↗", "溢流阀 / 平衡阀"),
        ("△|", "单向阀"),
    ]
    for i, (sym, desc) in enumerate(entries):
        text(msp, sym + "  " + desc, lx + 4, ly + lh - 22 - i * 14, h=4.5, layer="标题栏")


# ---------------------------------------------------------------------------
# Main circuit
# ---------------------------------------------------------------------------

def build_circuit(msp):
    # ── Sheet: A1 841 × 594 ──────────────────────────────────────────────
    W, H = 841, 594

    draw_title_block(msp, W, H)
    draw_legend(msp, 30, 80)

    # ── Vertical backbone X coordinates ─────────────────────────────────
    CX = 430          # centre spine (pump / valve)
    L_MX = 165        # left motor centre X
    R_MX = 695        # right motor centre X

    # ── Y levels (bottom → top) ──────────────────────────────────────────
    Y_TANK    = 65
    Y_FILTER  = 115
    Y_PUMP    = 175
    Y_VALVE   = 280
    Y_CB      = 370
    Y_MOTOR   = 455

    TANK_W, TANK_H = 80, 38
    PUMP_R   = 22
    MOTOR_R  = 28
    CB_SZ    = 20
    RV_SZ    = 16

    # ═══════════════════════════════════════════════════════════════════
    # 1. OIL TANK  油箱
    # ═══════════════════════════════════════════════════════════════════
    draw_tank(msp, CX, Y_TANK, w=TANK_W, h=TANK_H)
    tank_top = Y_TANK + TANK_H

    # ═══════════════════════════════════════════════════════════════════
    # 2. SUCTION FILTER  吸油过滤器
    # ═══════════════════════════════════════════════════════════════════
    F1X = CX - 22
    draw_filter(msp, F1X, Y_FILTER)
    text(msp, "吸油过滤器", F1X + 14, Y_FILTER - 4, h=5)
    # Tank → filter
    vline(msp, F1X, tank_top, Y_FILTER - 8)
    # filter → pump
    vline(msp, F1X, Y_FILTER + 8, Y_PUMP - PUMP_R)
    hline(msp, F1X, Y_PUMP - PUMP_R, CX - PUMP_R)

    # ═══════════════════════════════════════════════════════════════════
    # 3. VARIABLE PUMP  变量液压泵
    # ═══════════════════════════════════════════════════════════════════
    draw_variable_pump(msp, CX, Y_PUMP, r=PUMP_R)

    # Engine drive shaft (dashed, from left)
    hline(msp, CX - PUMP_R - 35, Y_PUMP, CX - PUMP_R, layer="虚线")
    text(msp, "发动机驱动轴", CX - PUMP_R - 80, Y_PUMP + 2, h=5)

    # Pump outlet line going up to main line Y_VALVE_IN
    Y_MAIN = Y_VALVE - 20          # horizontal main pressure rail
    vline(msp, CX, Y_PUMP + PUMP_R, Y_MAIN)

    # ── Main relief valve  主溢流阀 ──────────────────────────────────
    RV_X = CX + 55
    draw_relief_valve(msp, RV_X, Y_PUMP + PUMP_R + 18, sz=RV_SZ)
    text(msp, "主溢流阀", RV_X + RV_SZ / 2 + 4, Y_PUMP + PUMP_R + 20, h=5)
    text(msp, "35 MPa", RV_X + RV_SZ / 2 + 4, Y_PUMP + PUMP_R + 11, h=4)
    # tee off main line to relief valve
    hline(msp, CX, Y_PUMP + PUMP_R + 18, RV_X - RV_SZ / 2)
    # relief drain back to tank
    rv_drain_y = Y_PUMP + PUMP_R + 18
    hline(msp, RV_X + RV_SZ / 2 + 12, rv_drain_y, RV_X + RV_SZ / 2 + 30)
    vline(msp, RV_X + RV_SZ / 2 + 30, rv_drain_y, Y_TANK + TANK_H / 2)
    hline(msp, RV_X + RV_SZ / 2 + 30, Y_TANK + TANK_H / 2, CX + TANK_W / 2)

    # ── Pressure gauge  泵出口压力表 ────────────────────────────────
    PG_X = CX - 50
    draw_pressure_gauge(msp, PG_X, Y_MAIN + 10)
    text(msp, "压力表", PG_X - 4, Y_MAIN + 22, h=4)
    hline(msp, CX, Y_MAIN, PG_X)
    vline(msp, PG_X, Y_MAIN, Y_MAIN + 10 - 7)

    # ═══════════════════════════════════════════════════════════════════
    # 4. TRAVEL DIRECTIONAL CONTROL VALVE  行走换向阀
    # ═══════════════════════════════════════════════════════════════════
    VAL_BW, VAL_BH = 32, 30
    draw_3pos4way_valve(msp, CX, Y_VALVE, bw=VAL_BW, bh=VAL_BH)
    text(msp, "行走换向阀（三位四通先导式）", CX - 60, Y_VALVE - VAL_BH / 2 - 14, h=6)

    # P port – vertical from main line down to valve bottom
    vline(msp, CX, Y_MAIN, Y_VALVE - VAL_BH / 2)

    # T port – return to tank via return filter
    T_DRAIN_X = CX + 80
    vline(msp, CX, Y_VALVE + VAL_BH / 2, Y_VALVE + VAL_BH / 2 + 15)
    hline(msp, CX, Y_VALVE + VAL_BH / 2 + 15, T_DRAIN_X)
    # Return filter
    RF_Y = Y_FILTER
    draw_filter(msp, T_DRAIN_X, RF_Y)
    text(msp, "回油过滤器", T_DRAIN_X + 14, RF_Y - 4, h=5)
    vline(msp, T_DRAIN_X, Y_VALVE + VAL_BH / 2 + 15, RF_Y + 8)
    vline(msp, T_DRAIN_X, RF_Y - 8, tank_top)
    hline(msp, T_DRAIN_X, tank_top, CX + TANK_W / 2)

    # ── A port line (left side of valve → left motor) ────────────────
    A_PORT_X = CX - VAL_BW * 1.5    # left face of valve
    A_LINE_Y = Y_VALVE              # A port is at valve mid-height (left face)
    hline(msp, A_PORT_X, A_LINE_Y, A_PORT_X - 18)
    vline(msp, A_PORT_X - 18, A_LINE_Y, Y_CB - CB_SZ / 2 - 10)
    hline(msp, A_PORT_X - 18, Y_CB - CB_SZ / 2 - 10, L_MX + MOTOR_R + 25)
    vline(msp, L_MX + MOTOR_R + 25, Y_CB - CB_SZ / 2 - 10, Y_CB - CB_SZ / 2)

    # ── B port line (right side → right motor) ───────────────────────
    B_PORT_X = CX + VAL_BW * 1.5
    hline(msp, B_PORT_X, A_LINE_Y, B_PORT_X + 18)
    vline(msp, B_PORT_X + 18, A_LINE_Y, Y_CB - CB_SZ / 2 - 10)
    hline(msp, B_PORT_X + 18, Y_CB - CB_SZ / 2 - 10, R_MX - MOTOR_R - 25)
    vline(msp, R_MX - MOTOR_R - 25, Y_CB - CB_SZ / 2 - 10, Y_CB - CB_SZ / 2)

    # ═══════════════════════════════════════════════════════════════════
    # 5. LEFT COUNTERBALANCE VALVE  左平衡阀
    # ═══════════════════════════════════════════════════════════════════
    L_CB_X = L_MX + MOTOR_R + 25
    draw_counterbalance_valve(msp, L_CB_X, Y_CB, sz=CB_SZ)
    text(msp, "平衡阀", L_CB_X - CB_SZ / 2 - 32, Y_CB - 3, h=5)
    # CB → motor port
    vline(msp, L_CB_X, Y_CB + CB_SZ / 2, Y_MOTOR - MOTOR_R)
    hline(msp, L_CB_X, Y_MOTOR - MOTOR_R, L_MX)
    vline(msp, L_MX, Y_MOTOR - MOTOR_R, Y_MOTOR - MOTOR_R + 6)

    # Check valve on A branch (anti-cavitation)  左侧单向阀
    CV_L_Y = (Y_CB - CB_SZ / 2 - 10 + Y_CB - CB_SZ / 2) / 2
    draw_check_valve(msp, L_CB_X, CV_L_Y, size=8, vertical=True)
    text(msp, "单向阀", L_CB_X + 10, CV_L_Y - 3, h=4)

    # ═══════════════════════════════════════════════════════════════════
    # 6. RIGHT COUNTERBALANCE VALVE  右平衡阀
    # ═══════════════════════════════════════════════════════════════════
    R_CB_X = R_MX - MOTOR_R - 25
    draw_counterbalance_valve(msp, R_CB_X, Y_CB, sz=CB_SZ)
    text(msp, "平衡阀", R_CB_X + CB_SZ / 2 + 4, Y_CB - 3, h=5)
    # CB → motor port
    vline(msp, R_CB_X, Y_CB + CB_SZ / 2, Y_MOTOR - MOTOR_R)
    hline(msp, R_CB_X, Y_MOTOR - MOTOR_R, R_MX)
    vline(msp, R_MX, Y_MOTOR - MOTOR_R, Y_MOTOR - MOTOR_R + 6)

    CV_R_Y = CV_L_Y
    draw_check_valve(msp, R_CB_X, CV_R_Y, size=8, vertical=True)
    text(msp, "单向阀", R_CB_X + 10, CV_R_Y - 3, h=4)

    # ═══════════════════════════════════════════════════════════════════
    # 7. LEFT TRAVEL MOTOR  左行走马达
    # ═══════════════════════════════════════════════════════════════════
    draw_motor(msp, L_MX, Y_MOTOR, r=MOTOR_R)
    # Shaft output (left side)
    hline(msp, L_MX - MOTOR_R, Y_MOTOR, L_MX - MOTOR_R - 22)
    text(msp, "左行走马达（双速）", L_MX - 38, Y_MOTOR - MOTOR_R - 14, h=6)
    text(msp, "Left Travel Motor", L_MX - 30, Y_MOTOR - MOTOR_R - 25, h=4.5)

    # Motor B-port return line  马达B口回油
    hline(msp, L_MX + MOTOR_R, Y_MOTOR, L_MX + MOTOR_R + 15)
    vline(msp, L_MX + MOTOR_R + 15, Y_MOTOR, Y_VALVE)
    hline(msp, L_MX + MOTOR_R + 15, Y_VALVE, A_PORT_X - 18)  # joins A-line

    # Case drain  泄油口
    DRAIN_L_X = 40
    hline(msp, L_MX, Y_MOTOR + MOTOR_R, DRAIN_L_X)
    vline(msp, DRAIN_L_X, Y_MOTOR + MOTOR_R, tank_top + 5)
    hline(msp, DRAIN_L_X, tank_top + 5, CX - TANK_W / 2)
    text(msp, "泄油", DRAIN_L_X + 2, (Y_MOTOR + MOTOR_R + tank_top) / 2 + 5, h=4)

    # ── 2-speed solenoid  左行走二速电磁阀 ───────────────────────────
    SOL_L_X = L_MX - 20
    SOL_L_Y = Y_MOTOR + MOTOR_R + 38
    draw_solenoid_valve(msp, SOL_L_X, SOL_L_Y)
    text(msp, "二速电磁阀", SOL_L_X - 8, SOL_L_Y - 14, h=4.5)
    vline(msp, SOL_L_X, Y_MOTOR + MOTOR_R, SOL_L_Y - 7, layer="虚线")

    # ═══════════════════════════════════════════════════════════════════
    # 8. RIGHT TRAVEL MOTOR  右行走马达
    # ═══════════════════════════════════════════════════════════════════
    draw_motor(msp, R_MX, Y_MOTOR, r=MOTOR_R)
    # Shaft output (right side)
    hline(msp, R_MX + MOTOR_R, Y_MOTOR, R_MX + MOTOR_R + 22)
    text(msp, "右行走马达（双速）", R_MX - 38, Y_MOTOR - MOTOR_R - 14, h=6)
    text(msp, "Right Travel Motor", R_MX - 32, Y_MOTOR - MOTOR_R - 25, h=4.5)

    # Motor A-port return line  马达A口回油
    hline(msp, R_MX - MOTOR_R, Y_MOTOR, R_MX - MOTOR_R - 15)
    vline(msp, R_MX - MOTOR_R - 15, Y_MOTOR, Y_VALVE)
    hline(msp, R_MX - MOTOR_R - 15, Y_VALVE, B_PORT_X + 18)

    # Case drain
    DRAIN_R_X = W - 45
    hline(msp, R_MX, Y_MOTOR + MOTOR_R, DRAIN_R_X)
    vline(msp, DRAIN_R_X, Y_MOTOR + MOTOR_R, tank_top + 5)
    hline(msp, DRAIN_R_X, tank_top + 5, CX + TANK_W / 2)
    text(msp, "泄油", DRAIN_R_X - 14, (Y_MOTOR + MOTOR_R + tank_top) / 2 + 5, h=4)

    # ── 2-speed solenoid  右行走二速电磁阀 ───────────────────────────
    SOL_R_X = R_MX + 20
    SOL_R_Y = SOL_L_Y
    draw_solenoid_valve(msp, SOL_R_X, SOL_R_Y)
    text(msp, "二速电磁阀", SOL_R_X - 8, SOL_R_Y - 14, h=4.5)
    vline(msp, SOL_R_X, Y_MOTOR + MOTOR_R, SOL_R_Y - 7, layer="虚线")

    # ═══════════════════════════════════════════════════════════════════
    # 9. DRAWING TITLE  图纸标题
    # ═══════════════════════════════════════════════════════════════════
    text(msp, "EXB360 挖掘机行走液压回路图", 200, H - 22, h=14, layer="标题栏")
    text(msp, "EXB360 Excavator Travel Hydraulic Circuit Diagram", 200, H - 36, h=7, layer="标题栏")

    # Legend
    draw_legend(msp, 30, 80)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    doc = ezdxf.new(dxfversion="R2010")  # AC1024 – fully compatible with AutoCAD 2025

    # Document-level settings
    doc.header["$INSUNITS"] = 4      # millimetres
    doc.header["$MEASUREMENT"] = 1   # metric
    doc.header["$DIMSCALE"] = 1.0
    doc.header["$LTSCALE"] = 1.0

    # Layers
    layer_defs = [
        ("液压线路", 7,  "Continuous"),   # white – main hydraulic lines
        ("元件轮廓", 2,  "Continuous"),   # yellow – component outlines
        ("文字标注", 3,  "Continuous"),   # green  – annotation text
        ("标题栏",   1,  "Continuous"),   # red    – title block / border
        ("虚线",     8,  "DASHED"),       # grey   – pilot/drain lines (dashed)
        ("中心线",   6,  "CENTER"),       # magenta – centre lines
    ]
    for name, color, ltype in layer_defs:
        doc.layers.add(name, color=color)

    msp = doc.modelspace()
    build_circuit(msp)

    out = "/home/runner/work/cad/cad/EXB360_travel_hydraulic_circuit.dxf"
    doc.saveas(out)
    print(f"Saved: {out}")

    # Quick audit
    doc2 = ezdxf.readfile(out)
    print(f"Re-read OK – entity count: {len(list(doc2.modelspace()))}")


if __name__ == "__main__":
    main()
