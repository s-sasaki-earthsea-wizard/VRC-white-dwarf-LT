"""運動量と速度の関係でみる「光速の壁」のアニメーション。

電子をぎゅうぎゅうに詰め込むほど運動量 p は大きくなる。古典(ニュートン)の
世界では速度は v = p/m でどこまでも上がり、光速 c をやすやすと超えてしまう。
だが相対論では、運動量をいくら増やしても速度は c に漸近して頭打ちになる。

    ・低い運動量では、古典も相対論もほぼ同じ(直線に重なる)
    ・運動量を上げると、相対論の曲線は c の壁に近づいて伸び悩む

この「速くしたいのに、もう速くできない」が、奥の席の電子の運動量を上げても
縮退圧が思ったほど跳ね上がらなくなる――バネが頼りなくなる――理由そのもの。
yt_script.md の「6. 光速の壁 ―― バネが弱くなる」に対応する。

規格化単位として mc = 1, c = 1 を採り、横軸は p/mc、縦軸は v/c で描く:

    古典    : v = p          (原点を通る直線。p = 1 で c に達し、さらに突き抜ける)
    相対論  : v = p / √(1 + p²)   (p → ∞ で c に漸近)

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/momentum_velocity.py MomentumVelocity   # 低画質プレビュー
    manim -pqh manim-scripts/momentum_velocity.py MomentumVelocity   # 高画質
"""

import numpy as np
from manim import *

# 配色 (既存スクリプトの色味に準拠)
AXIS_COLOR = "#5F5E5A"          # 座標軸
GRID_COLOR = "#B4B2A9"          # 補助線
CLASSICAL_COLOR = "#C8643C"     # 古典 v = p/m (素朴な予想・テラコッタ)
RELATIVISTIC_COLOR = "#185FA5"  # 相対論 v = p/√(1+p²) (正しい振る舞い・青)
LIGHT_COLOR = "#C9A227"         # 光速 c の壁 (金)

# 描画範囲 (規格化単位 mc = 1, c = 1)
P_RANGE = [0.0, 4.0, 1.0]       # 運動量 p / mc
V_RANGE = [0.0, 1.35, 0.5]      # 速度 v / c

# 古典の直線を描く運動量の上限。v = p なので p = 1.3 で縦軸の上端に達し、
# c の壁(v = 1)を突き抜けて画面外へ抜ける様子を見せる
P_CLASSICAL_MAX = 1.3

# 相対論の曲線を強調する高運動量側の位置 (壁ぎわで伸び悩む点)
P_HIGHLIGHT = 2.0


def v_classical(p: float) -> float:
    """古典(ニュートン)の速度 v = p (規格化単位 mc = 1, c = 1)。"""
    return p


def v_relativistic(p: float) -> float:
    """相対論の速度 v = p / √(1 + p²) (規格化単位 mc = 1, c = 1)。

    p = γ m v を v について解いて c で規格化したもの。p → ∞ で 1(= c)に漸近する。
    """
    return p / np.sqrt(1.0 + p * p)


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。

    Args:
        jp: 上段に表示する日本語テロップ。
        en: 下段に表示する英語テロップ。

    Returns:
        日英を縦に並べて画面下部に配置した VGroup。
    """
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


class MomentumVelocity(Scene):
    """運動量を上げても速度が c で頭打ちになる「光速の壁」を見せるシーン。"""

    def construct(self):
        self.caption = None

        # --- 座標軸 (横: 運動量 p / 縦: 速度 v) ---
        axes = Axes(
            x_range=P_RANGE,
            y_range=V_RANGE,
            x_length=8.6,
            y_length=5.0,
            axis_config={
                "color": AXIS_COLOR,
                "stroke_width": 2,
                "include_ticks": False,
                "tip_width": 0.18,
                "tip_height": 0.18,
            },
        )
        axes.to_edge(UP, buff=0.7).shift(DOWN * 0.1)
        self.axes = axes

        x_label = Text("運動量 p", font_size=24, color=GRAY_C)
        x_label.next_to(axes.x_axis.get_end(), DOWN, buff=0.18)
        y_label = Text("速度 v", font_size=24, color=GRAY_C)
        y_label.next_to(axes.y_axis.get_end(), RIGHT, buff=0.18)

        self.play(Create(axes), run_time=1.2)
        self.play(FadeIn(x_label, shift=DOWN * 0.1), FadeIn(y_label, shift=RIGHT * 0.1),
                  run_time=0.8)

        # --- 光速 c の壁 (v = 1 の水平な点線) ---
        self.show_caption("どんなものも光速 c を超えられない",
                          "Nothing can exceed the speed of light c")
        c_line = DashedLine(
            axes.c2p(P_RANGE[0], 1.0),
            axes.c2p(P_RANGE[1], 1.0),
            color=LIGHT_COLOR,
            stroke_width=3,
            dash_length=0.14,
        )
        # 右上は相対論ラベルと混み合うので、光速 c の注記は左寄りの壁の上に置く
        c_label = Text("光速 c", font_size=24, color=LIGHT_COLOR, weight=BOLD)
        c_label.next_to(axes.c2p(0.55, 1.0), UP, buff=0.1)
        self.play(Create(c_line), FadeIn(c_label), run_time=1.0)
        self.wait(0.4)

        # --- 古典の直線 v = p/m (cを突き抜けて画面外へ) ---
        self.show_caption("古典：詰め込むほど、どこまでも速くなる",
                          "Classical: pack more, go ever faster")
        classical = axes.plot(
            v_classical,
            x_range=[0.0, P_CLASSICAL_MAX],
            color=CLASSICAL_COLOR,
            stroke_width=5,
        )
        classical_label = Text("v = p / m", font_size=24, color=CLASSICAL_COLOR,
                               weight=BOLD)
        classical_label.next_to(classical.get_end(), UR, buff=0.08)
        self.play(Create(classical), run_time=1.3)
        self.play(FadeIn(classical_label, shift=UP * 0.1), run_time=0.6)
        # cの壁を「軽々超えてしまう」ことを示す
        self.show_caption("古典のままだと、光速 c すら超えてしまう",
                          "Taken literally, it would even exceed c")
        self.play(Indicate(classical_label, color=CLASSICAL_COLOR, scale_factor=1.15),
                  run_time=1.0)
        self.wait(0.5)

        # --- 相対論の曲線 v = p/√(1+p²) (cに漸近) ---
        self.show_caption("相対論：速度は光速 c に漸近して頭打ち",
                          "Relativity: speed saturates, approaching c")
        relativistic = axes.plot(
            v_relativistic,
            x_range=[0.0, P_RANGE[1]],
            color=RELATIVISTIC_COLOR,
            stroke_width=5,
        )
        # 曲線の下側の空きスペース(右下)に置き、c の壁の注記と重ねない
        rel_label = Text("相対論 / relativity", font_size=22,
                         color=RELATIVISTIC_COLOR, weight=BOLD)
        rel_label.next_to(axes.c2p(2.6, v_relativistic(2.6)), DOWN, buff=0.35)
        self.play(Create(relativistic), run_time=1.6)
        self.play(FadeIn(rel_label, shift=UP * 0.1), run_time=0.6)
        self.wait(0.3)

        # 低運動量では古典と一致することを示す (原点付近を強調)
        self.show_caption("ゆっくりなら、古典とほとんど同じ",
                          "At low speed, it matches the classical line")
        low_p_zone = SurroundingRectangle(
            VGroup(
                Dot(axes.c2p(0, 0)),
                Dot(axes.c2p(0.5, v_relativistic(0.5))),
            ),
            color=GRAY_B,
            stroke_width=2,
            buff=0.12,
        )
        self.play(Create(low_p_zone), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(low_p_zone), run_time=0.5)

        # --- 高運動量側を強調：詰め込んでも、もう速くならない ---
        self.show_caption("詰め込んでも、もう速くならない ― 光速の壁",
                          "Packing more no longer helps — the speed-of-light wall")
        # 壁ぎわの点と、そこから c までの「届かない隙間」を見せる
        p_hi = P_HIGHLIGHT
        wall_dot = Dot(axes.c2p(p_hi, v_relativistic(p_hi)),
                       radius=0.07, color=RELATIVISTIC_COLOR)
        wall_dot.set_stroke(WHITE, width=1)
        gap = DoubleArrow(
            axes.c2p(p_hi, v_relativistic(p_hi)),
            axes.c2p(p_hi, 1.0),
            color=LIGHT_COLOR,
            stroke_width=3,
            buff=0.0,
            tip_length=0.16,
        )
        gap_note = Text("c には届かない", font_size=20, color=LIGHT_COLOR, weight=BOLD)
        gap_note.next_to(gap, RIGHT, buff=0.18)
        self.play(GrowFromCenter(wall_dot), run_time=0.5)
        self.play(GrowArrow(gap), FadeIn(gap_note, shift=RIGHT * 0.1), run_time=0.9)
        self.wait(0.6)

        # 高運動量側で曲線が水平に寝ていく(速度が伸び悩む)ことを強調する
        flat_tail = axes.plot(
            v_relativistic,
            x_range=[2.4, P_RANGE[1]],
            color=RELATIVISTIC_COLOR,
            stroke_width=8,
        )
        self.play(Create(flat_tail), run_time=0.7)
        self.play(Indicate(flat_tail, color=LIGHT_COLOR, scale_factor=1.0),
                  run_time=1.0)
        self.wait(1.6)

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
