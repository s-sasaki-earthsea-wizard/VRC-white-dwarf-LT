"""チャンドラセカール限界の天秤のアニメーション。

白色矮星を支えられる質量には上限がある――「重力」と「電子縮退圧」を
天秤に載せ、星を重くしていくと天秤が圧力側から重力側へ傾いていき、
ある質量 (チャンドラセカール限界 ≈ 太陽1.4個ぶん) でぴたりと水平になる
ギリギリの釣り合いを見せる。

同時に、白色矮星の半径が質量の -1/3 乗に比例して縮む (R ∝ M^(-1/3)) ことを
星本体の大きさで可視化する。重くするほど星が小さくなる＝外へ膨らむ力が
重力に負けつつある、が目に見える。

yt_script.md の「7. チャンドラセカール限界」に対応するカット。

構成:
    ① 天秤の提示: 左に重力、右に電子縮退圧。軽いうちは圧力側が優勢
    ② 星を重くする → 天秤が重力側へ傾き、星自体は小さくなる (R ∝ M^(-1/3))
    ③ M = 1.4 太陽質量でぴたりと水平 = チャンドラセカール限界
    ④ 「太陽 約1.4個ぶん」の絵
    ⑤ 限界を超えると重力側に倒れ、星は潰れ続ける

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/chandrasekhar_balance.py ChandrasekharBalance   # 低画質プレビュー
    manim -pqh manim-scripts/chandrasekhar_balance.py ChandrasekharBalance   # 高画質
"""

import numpy as np
from manim import *

# 配色 (既存スクリプトの色味に準拠)
GRAVITY_COLOR = "#2F80ED"    # 重力 (青)
PRESSURE_COLOR = "#6FBF3A"   # 電子縮退圧 (緑)
BEAM_COLOR = "#8A8782"       # 天秤の竿
PIVOT_COLOR = "#5F5E5A"      # 支点
WD_CORE = "#EAF2FF"          # 白色矮星の中心色 (白〜淡青)
WD_RIM = "#9FB8D8"           # 白色矮星の縁
GHOST_COLOR = "#7A8794"      # 元の大きさを示す破線
SUN_COLOR = "#EF9F27"        # 太陽 (1.4個ぶんの絵)
SUN_RIM = "#BA7517"
LIMIT_COLOR = "#C9A227"      # 限界の強調 (金)

# 天秤のジオメトリ
PIVOT_POS = np.array([0.6, -1.15, 0.0])  # 支点の頂点位置
BEAM_HALF = 2.9                          # 竿の半長
STRING_LEN = 0.55                        # 皿を吊るすひもの長さ

# 白色矮星: R ∝ M^(-1/3) (M は太陽質量単位)
M_INIT = 0.4        # 初期質量
R_INIT = 1.15       # 初期質量での描画半径
M_LIMIT = 1.4       # チャンドラセカール限界

STAR_CENTER = np.array([-4.3, 1.7, 0.0])  # 星の表示位置


def wd_radius(mass: float) -> float:
    """質量 (太陽質量単位) に対する白色矮星の描画半径を返す。

    R ∝ M^(-1/3) を初期値 (M_INIT, R_INIT) で規格化したもの。

    Args:
        mass: 星の質量 [太陽質量]。

    Returns:
        シーン座標系での描画半径。
    """
    return R_INIT * (M_INIT / mass) ** (1.0 / 3.0)


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。"""
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


def make_white_dwarf(radius: float, center: np.ndarray) -> VGroup:
    """白〜淡青のグローを重ねた白色矮星を作る。"""
    group = VGroup()
    for scale, opacity in [(1.0, 0.10), (0.78, 0.16), (0.55, 0.30), (0.32, 0.55)]:
        layer = Circle(radius=radius * scale)
        layer.set_fill(WD_CORE, opacity=opacity).set_stroke(width=0)
        layer.move_to(center)
        group.add(layer)
    rim = Circle(radius=radius).set_stroke(WD_RIM, width=1.5, opacity=0.9)
    rim.set_fill(opacity=0).move_to(center)
    group.add(rim)
    return group


class ChandrasekharBalance(Scene):
    """重力 vs 電子縮退圧の天秤で質量の上限を見せるシーン。"""

    def construct(self):
        self.caption = None

        # 天秤の傾き (rad)。正で右(圧力側)が上がる = 重力側に傾く
        self.tilt = ValueTracker(-0.30)
        # 星の質量 [太陽質量]
        self.mass = ValueTracker(M_INIT)

        # --- ① 天秤と星の提示 ---
        balance = always_redraw(self._make_balance)
        star = always_redraw(
            lambda: make_white_dwarf(wd_radius(self.mass.get_value()), STAR_CENTER)
        )
        ghost = DashedVMobject(
            Circle(radius=R_INIT).move_to(STAR_CENTER), num_dashes=48
        ).set_stroke(GHOST_COLOR, width=1.5, opacity=0.8)
        mass_readout = self._make_mass_readout()

        self.show_caption("重力 と 電子縮退圧 の天秤",
                          "A balance: gravity vs electron degeneracy pressure")
        self.play(FadeIn(balance), run_time=1.2)
        self.play(FadeIn(star, scale=0.9), FadeIn(mass_readout), run_time=1.0)
        self.wait(0.6)

        # --- ② 重くする → 天秤は重力側へ、星は小さく ---
        self.show_caption("重くするほど、天秤は重力側へ",
                          "The heavier the star, the more gravity gains")
        self.play(
            FadeIn(ghost),
            self.mass.animate.set_value(1.0),
            self.tilt.animate.set_value(-0.16),
            run_time=2.4,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.4)

        self.show_caption("しかも、重い白色矮星ほど小さくなる",
                          "A heavier white dwarf is smaller — R ∝ M^(-1/3)")
        radius_note = Text("R ∝ M^(-1/3)", font_size=24, color=GHOST_COLOR,
                           weight=BOLD)
        radius_note.next_to(STAR_CENTER + DOWN * R_INIT, DOWN, buff=0.55)
        self.play(FadeIn(radius_note, shift=UP * 0.1), run_time=0.6)
        self.play(
            self.mass.animate.set_value(1.3),
            self.tilt.animate.set_value(-0.06),
            run_time=2.2,
            rate_func=rate_functions.ease_in_out_sine,
        )
        # 破線 (元の大きさ) と今の星の差を見せる
        self.play(Indicate(ghost, color=GHOST_COLOR, scale_factor=1.03),
                  run_time=0.9)
        self.wait(0.5)

        # --- ③ ぴたりと水平 = チャンドラセカール限界 ---
        self.show_caption("ギリギリの釣り合い ― チャンドラセカール限界",
                          "The knife-edge balance — the Chandrasekhar limit")
        self.play(
            self.mass.animate.set_value(M_LIMIT),
            self.tilt.animate.set_value(0.0),
            run_time=2.0,
            rate_func=rate_functions.ease_out_sine,
        )
        limit_line = DashedLine(
            PIVOT_POS + UP * 0.95 + LEFT * (BEAM_HALF + 0.4),
            PIVOT_POS + UP * 0.95 + RIGHT * (BEAM_HALF + 0.4),
            color=LIMIT_COLOR, stroke_width=2, dash_length=0.12,
        )
        self.play(Create(limit_line), run_time=0.8)
        self.wait(0.8)

        # --- ④ 太陽 約1.4個ぶん ---
        suns = self._make_sun_graphic()
        self.show_caption("その重さ、太陽 約1.4個ぶん",
                          "That mass is about 1.4 Suns")
        self.play(FadeIn(suns, shift=LEFT * 0.3), run_time=1.0)
        self.wait(1.6)

        # --- ⑤ 限界を超えると潰れ続ける ---
        self.show_caption("限界を超えると、もう支えられない",
                          "Beyond the limit, nothing holds it up")
        self.play(
            self.mass.animate.set_value(1.5),
            self.tilt.animate.set_value(0.30),
            run_time=1.6,
            rate_func=rate_functions.ease_in_sine,
        )
        # 星が一気に縮んでいく (潰れ続ける)。
        # always_redraw の更新を止めてから Transform する
        star.clear_updaters()
        collapse_target = make_white_dwarf(0.12, STAR_CENTER)
        self.play(Transform(star, collapse_target), run_time=1.4,
                  rate_func=rate_functions.ease_in_quad)
        self.wait(2.0)

    # ------------------------------------------------------------------
    # 部品づくり
    # ------------------------------------------------------------------
    def _make_balance(self) -> VGroup:
        """傾きトラッカーに追従する天秤一式を作る (always_redraw 用)。"""
        tilt = self.tilt.get_value()
        top = PIVOT_POS + UP * 0.95  # 竿の回転中心 (支点の頂上)

        group = VGroup()

        # 支点 (三角形) と土台
        pivot = Triangle().scale(0.55)
        pivot.set_fill(PIVOT_COLOR, opacity=1.0).set_stroke(width=0)
        pivot.move_to(PIVOT_POS + UP * 0.35)
        base = Rectangle(width=1.6, height=0.12)
        base.set_fill(PIVOT_COLOR, opacity=1.0).set_stroke(width=0)
        base.move_to(PIVOT_POS + DOWN * 0.18)
        group.add(pivot, base)

        # 竿: 傾き tilt で回転
        direction = np.array([np.cos(tilt), np.sin(tilt), 0.0])
        end_l = top - direction * BEAM_HALF
        end_r = top + direction * BEAM_HALF
        beam = Line(end_l, end_r, stroke_width=6, color=BEAM_COLOR)
        group.add(beam)

        # 左右の皿 (ひもは常に鉛直に垂れる)
        group.add(self._make_pan(end_l, GRAVITY_COLOR, "重力", "gravity"))
        group.add(self._make_pan(end_r, PRESSURE_COLOR, "電子縮退圧",
                                 "degeneracy pressure"))
        return group

    def _make_pan(self, hang_point: np.ndarray, color: str,
                  jp: str, en: str) -> VGroup:
        """竿の端から吊るす皿と中身のブロックを作る。

        Args:
            hang_point: 竿の端点 (吊り元)。
            color: ブロックとラベルの色。
            jp: ブロックの日本語ラベル。
            en: ブロックの英語ラベル。

        Returns:
            ひも・皿・ブロック・ラベルをまとめた VGroup。
        """
        pan_top = hang_point + DOWN * STRING_LEN
        string = Line(hang_point, pan_top, stroke_width=2, color=BEAM_COLOR)

        plate = Line(pan_top + LEFT * 0.65, pan_top + RIGHT * 0.65,
                     stroke_width=5, color=BEAM_COLOR)

        block = RoundedRectangle(width=1.45, height=0.6, corner_radius=0.08)
        block.set_fill(color, opacity=0.25).set_stroke(color, width=2)
        block.move_to(pan_top + UP * 0.32)

        jp_text = Text(jp, font_size=15, color=color, weight=BOLD)
        en_text = Text(en, font_size=10, color=color)
        label = VGroup(jp_text, en_text).arrange(DOWN, buff=0.05)
        label.move_to(block)

        return VGroup(string, plate, block, label)

    def _make_mass_readout(self) -> VGroup:
        """星の質量の読み出し表示 (M = x.xx 太陽質量) を作る。"""
        prefix = Text("M = ", font_size=26, color=WHITE)
        number = DecimalNumber(M_INIT, num_decimal_places=2, font_size=30,
                               color=WHITE)
        unit = Text(" 太陽質量 / solar masses", font_size=20, color=GRAY_B)
        group = VGroup(prefix, number, unit).arrange(RIGHT, buff=0.08)
        group.next_to(STAR_CENTER + UP * R_INIT, UP, buff=0.35)

        number.add_updater(lambda m: m.set_value(self.mass.get_value()))
        # 限界に達したら数字を金色で強調
        number.add_updater(
            lambda m: m.set_color(
                LIMIT_COLOR if self.mass.get_value() >= M_LIMIT - 0.005 else WHITE
            )
        )
        return group

    def _make_sun_graphic(self) -> VGroup:
        """「太陽 約1.4個ぶん」の絵 (太陽1個 + 0.4個ぶんの欠け) を作る。"""
        def sun_circle(radius: float) -> Circle:
            c = Circle(radius=radius)
            c.set_fill(SUN_COLOR, opacity=0.95).set_stroke(SUN_RIM, width=2)
            return c

        full_sun = sun_circle(0.5)

        # 0.4個ぶん: 円の左側 4 割だけを残した欠けた太陽
        partial_circle = sun_circle(0.5)
        clip = Rectangle(width=0.4, height=1.2)
        clip.move_to(partial_circle.get_left() + RIGHT * 0.2)
        partial = Intersection(partial_circle, clip)
        partial.set_fill(SUN_COLOR, opacity=0.95).set_stroke(SUN_RIM, width=2)

        text = Text("× 約1.4", font_size=26, color=SUN_COLOR, weight=BOLD)

        group = VGroup(full_sun, partial, text).arrange(RIGHT, buff=0.25)
        group.to_corner(UR, buff=0.5)
        return group

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
