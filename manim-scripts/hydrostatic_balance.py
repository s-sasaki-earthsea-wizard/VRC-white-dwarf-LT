"""静水圧平衡 (hydrostatic equilibrium) のアニメーション。

星がなぜ自分の重力で潰れずに丸い形を保てるのか――その理由である
「内向きの重力」と「外向きの圧力」のつり合いを可視化する。

slides-jp/assets/images/white_dwarf_hydrostatic_balance.svg を下敷きに、
オレンジ系の星本体・青=重力・緑=圧力という配色を踏襲している。

構成:
    ① 星本体を提示
    ② 内向きの重力が現れ、星がわずかに縮もうとする
    ③ 外向きの圧力が押し返し、星が元のサイズに戻る
    ④ 代表シェル dm に注目し、重力と圧力のつり合い (=静水圧平衡) を見せる

タイトルと方程式は動画編集側で付与するため、ここでは入れていない。
キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/hydrostatic_balance.py HydrostaticEquilibrium   # 低画質プレビュー
    manim -pqh manim-scripts/hydrostatic_balance.py HydrostaticEquilibrium   # 高画質
"""

import numpy as np
from manim import *

# SVG を踏襲した配色
STAR_CORE = "#EF9F27"     # 星本体のオレンジ
STAR_STROKE = "#BA7517"   # 星の輪郭・破線シェル
GRAVITY_COLOR = "#2F80ED"  # 重力 (内向き) の青
PRESSURE_COLOR = "#6FBF3A"  # 圧力 (外向き) の緑
SHELL_FILL = "#F0997B"     # 代表シェル dm の塗り
SHELL_STROKE = "#993C1D"   # 代表シェル dm の輪郭

STAR_RADIUS = 2.3          # 星本体の半径
SHELL_R = 1.5              # 代表シェルを置く半径 r


def make_star() -> VGroup:
    """中心ほど明るいオレンジの星本体を作る。

    Returns:
        グロー層・輪郭・破線シェル・中心マーカーをまとめた VGroup。
    """
    group = VGroup()

    # 中心へ向かうほど濃くなるグロー (同心円を重ねて表現)
    for rad, op in [(STAR_RADIUS, 0.12), (1.7, 0.14), (1.1, 0.18), (0.55, 0.26)]:
        layer = Circle(radius=rad).set_fill(STAR_CORE, opacity=op).set_stroke(width=0)
        group.add(layer)

    # 星の輪郭
    rim = Circle(radius=STAR_RADIUS).set_stroke(STAR_STROKE, width=1.5, opacity=0.85)
    rim.set_fill(opacity=0)
    group.add(rim)

    # 内部の破線シェル (半径の目安)
    for rad in (SHELL_R, 0.85):
        shell = DashedVMobject(
            Circle(radius=rad).set_stroke(STAR_STROKE, width=1, opacity=0.5),
            num_dashes=44,
        )
        group.add(shell)

    # 中心マーカーと r=0 ラベル
    center = Dot(ORIGIN, radius=0.045, color=STAR_STROKE)
    center_label = Text("r = 0", font_size=18, color=GRAY_B)
    center_label.next_to(center, RIGHT, buff=0.1)
    group.add(center, center_label)

    return group


def make_force_arrow(start, end, color) -> Arrow:
    """短くても太く見える力の矢印を作る。"""
    return Arrow(
        start=start,
        end=end,
        buff=0,
        color=color,
        stroke_width=5,
        tip_length=0.2,
        max_stroke_width_to_length_ratio=25,
        max_tip_length_to_length_ratio=0.5,
    )


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。"""
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


class HydrostaticEquilibrium(Scene):
    """重力と圧力のつり合い (静水圧平衡) を見せるシーン。"""

    def construct(self):
        self.caption = None

        # --- ① 星本体を提示 ---
        star = make_star().move_to(UP * 0.25)
        self.play(FadeIn(star, scale=0.9), run_time=1.2)
        self.wait(0.4)

        center = star.get_center()

        # 8 方向の単位ベクトルを用意 (重力・圧力の矢印を放射状に配置)
        dirs = [
            np.array([np.cos(a), np.sin(a), 0.0])
            for a in np.linspace(0, TAU, 8, endpoint=False)
        ]
        # 圧力は重力の間 (22.5°ずらし) に置いて交互に並べる
        dirs_offset = [
            np.array([np.cos(a), np.sin(a), 0.0])
            for a in np.linspace(0, TAU, 8, endpoint=False) + PI / 8
        ]

        # --- ② 内向きの重力 ---
        gravity_arrows = VGroup(*[
            make_force_arrow(center + d * 3.0, center + d * 2.45, GRAVITY_COLOR)
            for d in dirs
        ])
        self.show_caption("重力：内側へ縮もうとする", "Gravity pulls matter inward")
        self.play(
            LaggedStart(*[GrowArrow(a) for a in gravity_arrows], lag_ratio=0.06),
            run_time=1.1,
        )
        # 重力に押されて星がわずかに縮む
        self.play(star.animate.scale(0.92), run_time=0.7)
        self.wait(0.3)

        # --- ③ 外向きの圧力が押し返す ---
        pressure_arrows = VGroup(*[
            make_force_arrow(center + d * 2.45, center + d * 3.0, PRESSURE_COLOR)
            for d in dirs_offset
        ])
        self.show_caption("圧力：外向きに押し返す", "Pressure pushes back outward")
        self.play(
            LaggedStart(*[GrowArrow(a) for a in pressure_arrows], lag_ratio=0.06),
            run_time=1.1,
        )
        # 圧力に押し返されて元のサイズへ戻る
        self.play(star.animate.scale(1 / 0.92), run_time=0.7)
        self.wait(0.5)

        # --- ④ 代表シェル dm に注目し、つり合いを見せる ---
        self.show_caption("つり合い ＝ 静水圧平衡", "Force balance — hydrostatic equilibrium")
        self.play(
            FadeOut(gravity_arrows),
            FadeOut(pressure_arrows),
            run_time=0.7,
        )
        self._focus_on_shell(star, center)

        self.wait(2.0)

    # ------------------------------------------------------------------
    # 補助メソッド
    # ------------------------------------------------------------------
    def _focus_on_shell(self, star: VGroup, center: np.ndarray):
        """半径 r 上の代表シェル dm で重力と圧力の局所的なつり合いを見せる。"""
        shell_pos = center + RIGHT * SHELL_R

        # 半径 r を示す破線と r ラベル
        r_line = DashedLine(center, shell_pos, color=GRAY_B, stroke_width=1.5)
        r_label = Text("r", font_size=22, color=GRAY_B)
        r_label.next_to(r_line, UP, buff=0.08)

        # 代表シェル dm
        dm_rect = RoundedRectangle(
            width=0.5, height=0.3, corner_radius=0.05,
            fill_color=SHELL_FILL, fill_opacity=1.0,
            stroke_color=SHELL_STROKE, stroke_width=1.5,
        ).move_to(shell_pos)
        dm_label = Text("dm", font_size=18, color="#4A1B0C").move_to(dm_rect)
        dm_group = VGroup(dm_rect, dm_label)

        self.play(
            Create(r_line), FadeIn(r_label),
            FadeIn(dm_group, scale=0.5),
            run_time=1.0,
        )

        # シェルに働く力: 重力(内向き=中心向き)と圧力(外向き)
        grav = make_force_arrow(
            shell_pos + UP * 0.4 + RIGHT * 0.45,
            shell_pos + UP * 0.4 + LEFT * 0.45,
            GRAVITY_COLOR,
        )
        grav_label = Text("重力 / gravity", font_size=18, color=GRAVITY_COLOR)
        grav_label.next_to(grav, UP, buff=0.08)

        pres = make_force_arrow(
            shell_pos + DOWN * 0.4 + LEFT * 0.45,
            shell_pos + DOWN * 0.4 + RIGHT * 0.45,
            PRESSURE_COLOR,
        )
        pres_label = Text("圧力 / pressure", font_size=18, color=PRESSURE_COLOR)
        pres_label.next_to(pres, DOWN, buff=0.08)

        self.play(
            GrowArrow(grav), FadeIn(grav_label),
            GrowArrow(pres), FadeIn(pres_label),
            run_time=1.0,
        )
        self.wait(0.3)

        # 綱引き: 重力に少し引かれ、圧力に押し返され、最後はつり合って止まる
        self.play(
            Indicate(grav, scale_factor=1.3, color=GRAVITY_COLOR),
            dm_group.animate.shift(LEFT * 0.12),
            run_time=0.6,
        )
        self.play(
            Indicate(pres, scale_factor=1.3, color=PRESSURE_COLOR),
            dm_group.animate.shift(RIGHT * 0.12),
            run_time=0.6,
        )
        # つり合い: 両方を同時に強調し、シェルは動かない
        self.play(
            Indicate(grav, scale_factor=1.2, color=GRAVITY_COLOR),
            Indicate(pres, scale_factor=1.2, color=PRESSURE_COLOR),
            run_time=0.9,
        )

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
