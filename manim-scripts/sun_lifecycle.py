"""太陽の一生 (主系列 → 赤色巨星 → 白色矮星) のアニメーション。

太陽が燃料の水素を使い切り、赤色巨星に膨らみ、外層を放出して
白色矮星が残るまでを 1 カットで見せる。残った芯を地球と並べて
「太陽なみの重さが地球サイズに詰まっている」ことまでつなぐ。

yt_script.md の「1. 太陽の一生と『白色矮星』」に対応するカット。

構成:
    ① いまの太陽: 表面で核融合の光がちらつく
    ② 50億年の時計が早送りで進む
    ③ 膨らんで赤色巨星に (最後の輝き)
    ④ 外側のガスが剥がれ、中心に白い芯だけが残る
    ⑤ 芯にズームイン: 白色矮星と地球はほぼ同じ大きさ
    ⑥ 天秤: 太陽1個ぶんの重さ = この小さな星

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/sun_lifecycle.py SunLifecycle   # 低画質プレビュー
    manim -pqh manim-scripts/sun_lifecycle.py SunLifecycle   # 高画質
"""

import numpy as np
from manim import *

# 配色
SUN_COLOR = "#EF9F27"      # いまの太陽 (オレンジ)
SUN_RIM = "#BA7517"
GIANT_COLOR = "#D14B3A"    # 赤色巨星 (赤)
GIANT_RIM = "#8F2C1E"
EJECTA_COLOR = "#E58A6F"   # 放出されるガス (薄い赤)
WD_CORE = "#EAF2FF"        # 白色矮星 (白〜淡青)
WD_RIM = "#9FB8D8"
EARTH_COLOR = "#2F6FE0"    # 地球 (青)
EARTH_LAND = "#6FBF3A"     # 地球の陸 (緑)
CLOCK_COLOR = "#C9A227"    # 時計 (金)
BEAM_COLOR = "#8A8782"     # 天秤の竿

SUN_RADIUS = 1.3           # いまの太陽の描画半径
GIANT_SCALE = 2.3          # 赤色巨星への拡大率
WD_RADIUS_SMALL = 0.14     # 芯として残る白色矮星の半径
WD_RADIUS_ZOOM = 0.85      # ズーム後の白色矮星の半径


def make_glow_ball(radius: float, color: str, rim_color: str,
                   center: np.ndarray = ORIGIN) -> VGroup:
    """中心ほど明るいグローを重ねた星の球体を作る。

    Args:
        radius: 最外層の半径。
        color: 本体の色。
        rim_color: 輪郭の色。
        center: 配置する中心座標。

    Returns:
        グロー層と輪郭をまとめた VGroup。
    """
    group = VGroup()
    for scale, opacity in [(1.0, 0.14), (0.75, 0.20), (0.5, 0.30), (0.28, 0.50)]:
        layer = Circle(radius=radius * scale)
        layer.set_fill(color, opacity=opacity).set_stroke(width=0)
        layer.move_to(center)
        group.add(layer)
    rim = Circle(radius=radius).set_stroke(rim_color, width=1.5, opacity=0.85)
    rim.set_fill(opacity=0).move_to(center)
    group.add(rim)
    return group


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。"""
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


class SunLifecycle(Scene):
    """太陽 → 赤色巨星 → 白色矮星 → 地球とのサイズ・質量比較のシーン。"""

    def construct(self):
        self.caption = None

        # --- ① いまの太陽 ---
        sun = make_glow_ball(SUN_RADIUS, SUN_COLOR, SUN_RIM, UP * 0.4)
        self.show_caption("太陽はいま、核融合で燃えている",
                          "The Sun burns by nuclear fusion today")
        self.play(FadeIn(sun, scale=0.9), run_time=1.2)
        # 表面のちらちらした核融合の光
        rng = np.random.default_rng(5)
        for _ in range(3):
            ang = rng.uniform(0, TAU)
            point = sun.get_center() + np.array(
                [np.cos(ang), np.sin(ang), 0.0]
            ) * SUN_RADIUS * 0.8
            self.play(Flash(point, color=YELLOW_A, flash_radius=0.35,
                            num_lines=8), run_time=0.45)
        self.wait(0.3)

        # --- ② 50億年の早送り ---
        self.show_caption("燃料の水素は、あと50億年で尽きる",
                          "Its hydrogen fuel runs out in about 5 billion years")
        clock, years = self._make_clock()
        self.play(FadeIn(clock), run_time=0.6)
        hand = clock[1]
        self.play(
            Rotate(hand, angle=-6 * TAU, about_point=clock[0].get_center()),
            years.animate.set_value(50),
            run_time=2.6,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(0.5)

        # --- ③ 赤色巨星へ ---
        self.show_caption("膨らんで赤色巨星に ― 燃え尽きる前の最後の輝き",
                          "It swells into a red giant — the final blaze")
        giant = make_glow_ball(SUN_RADIUS * GIANT_SCALE, GIANT_COLOR, GIANT_RIM,
                               sun.get_center())
        self.play(Transform(sun, giant), run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)

        # --- ④ 外層の放出 → 芯だけが残る ---
        self.show_caption("外側のガスを手放し、中心の芯だけが残る",
                          "The outer layers drift away, leaving only the core")
        center = sun.get_center()
        shells = VGroup(*[
            Circle(radius=SUN_RADIUS * GIANT_SCALE * s)
            .set_stroke(EJECTA_COLOR, width=3, opacity=0.7)
            .set_fill(opacity=0)
            .move_to(center)
            for s in (0.95, 0.75, 0.55)
        ])
        core = make_glow_ball(WD_RADIUS_SMALL, WD_CORE, WD_RIM, center)
        # カウンタの更新を止めてからフェードアウトする
        years.mobject_group[0].clear_updaters()
        self.add(shells)
        self.play(
            FadeOut(sun, run_time=2.0),
            FadeOut(clock), FadeOut(years.mobject_group),
            *[shell.animate(run_time=2.2).scale(2.6).set_stroke(opacity=0)
              for shell in shells],
            FadeIn(core, run_time=1.6),
        )
        self.remove(shells)
        self.wait(0.4)

        # --- ⑤ ズームイン: 白色矮星 vs 地球 ---
        self.show_caption("これが白色矮星 ― 燃え尽きた星",
                          "This is a white dwarf — the burnt-out star")
        zoomed = make_glow_ball(WD_RADIUS_ZOOM, WD_CORE, WD_RIM,
                                LEFT * 2.0 + UP * 0.5)
        self.play(Transform(core, zoomed), run_time=1.6,
                  rate_func=rate_functions.ease_in_out_sine)
        wd_label = self._make_label("白色矮星", "white dwarf", WD_RIM)
        wd_label.next_to(core, DOWN, buff=0.35)
        self.play(FadeIn(wd_label, shift=UP * 0.1), run_time=0.6)
        self.wait(0.4)

        earth = self._make_earth(WD_RADIUS_ZOOM, RIGHT * 2.0 + UP * 0.5)
        earth_label = self._make_label("地球", "Earth", EARTH_COLOR)
        earth_label.next_to(earth, DOWN, buff=0.35)
        self.show_caption("大きさは、地球とほぼ同じ",
                          "It is about the same size as Earth")
        self.play(FadeIn(earth, scale=0.8), FadeIn(earth_label), run_time=1.0)
        self.wait(1.2)

        # --- ⑥ 天秤: 太陽1個ぶんの重さ = この小さな星 ---
        self.show_caption("太陽なみの重さが、地球サイズに詰まっている",
                          "A Sun's worth of mass packed into an Earth-sized ball")
        self.play(FadeOut(earth), FadeOut(earth_label), FadeOut(wd_label),
                  run_time=0.7)
        self._show_mass_balance(core)
        self.wait(2.0)

    # ------------------------------------------------------------------
    # 部品づくり
    # ------------------------------------------------------------------
    def _make_clock(self) -> tuple[VGroup, ValueTracker]:
        """早送り用の時計と「○○億年後」のカウンタを作る。

        Returns:
            (時計の VGroup, 年数のトラッカー) のタプル。
            トラッカーには .mobject_group としてカウンタ表示を持たせる。
        """
        face = Circle(radius=0.55).set_stroke(CLOCK_COLOR, width=3)
        face.set_fill(BLACK, opacity=0.4)
        face.to_corner(UR, buff=0.6).shift(LEFT * 0.4)
        hand = Line(face.get_center(),
                    face.get_center() + UP * 0.42,
                    stroke_width=4, color=CLOCK_COLOR)
        clock = VGroup(face, hand)

        years = ValueTracker(0)
        number = Integer(0, font_size=30, color=CLOCK_COLOR)
        number.add_updater(lambda m: m.set_value(years.get_value()))
        unit = Text("億年後 / ×100 Myr later", font_size=18, color=GRAY_B)
        counter = VGroup(number, unit).arrange(RIGHT, buff=0.12)
        counter.next_to(face, DOWN, buff=0.2)
        number.add_updater(lambda m: m.next_to(unit, LEFT, buff=0.12))
        self.add(counter)
        years.mobject_group = counter  # 後でまとめてフェードアウトするための参照
        return clock, years

    def _make_earth(self, radius: float, center: np.ndarray) -> VGroup:
        """青い海と簡単な陸を持つ地球を作る。"""
        sea = Circle(radius=radius)
        sea.set_fill(EARTH_COLOR, opacity=0.9).set_stroke("#1D4DA8", width=2)
        sea.move_to(center)
        land1 = Ellipse(width=radius * 0.9, height=radius * 0.55)
        land1.set_fill(EARTH_LAND, opacity=0.9).set_stroke(width=0)
        land1.move_to(center + np.array([-radius * 0.25, radius * 0.3, 0.0]))
        land1.rotate(0.5)
        land2 = Ellipse(width=radius * 0.6, height=radius * 0.4)
        land2.set_fill(EARTH_LAND, opacity=0.9).set_stroke(width=0)
        land2.move_to(center + np.array([radius * 0.35, -radius * 0.35, 0.0]))
        land2.rotate(-0.4)
        return VGroup(sea, land1, land2)

    def _make_label(self, jp: str, en: str, color: str) -> VGroup:
        """天体名の日英ラベルを作る。"""
        jp_text = Text(jp, font_size=24, color=color, weight=BOLD)
        en_text = Text(en, font_size=18, color=GRAY_B)
        return VGroup(jp_text, en_text).arrange(DOWN, buff=0.08)

    def _show_mass_balance(self, core: VGroup):
        """太陽1個ぶんの重さと白色矮星が釣り合う天秤を見せる。"""
        pivot_pos = np.array([0.0, -1.5, 0.0])
        top = pivot_pos + UP * 0.8

        pivot = Triangle().scale(0.45)
        pivot.set_fill(BEAM_COLOR, opacity=1.0).set_stroke(width=0)
        pivot.move_to(pivot_pos + UP * 0.3)
        beam = Line(top + LEFT * 2.6, top + RIGHT * 2.6,
                    stroke_width=5, color=BEAM_COLOR)
        plate_l = Line(top + LEFT * 2.6 + DOWN * 0.45 + LEFT * 0.5,
                       top + LEFT * 2.6 + DOWN * 0.45 + RIGHT * 0.5,
                       stroke_width=4, color=BEAM_COLOR)
        plate_r = Line(top + RIGHT * 2.6 + DOWN * 0.45 + LEFT * 0.5,
                       top + RIGHT * 2.6 + DOWN * 0.45 + RIGHT * 0.5,
                       stroke_width=4, color=BEAM_COLOR)
        string_l = Line(top + LEFT * 2.6, plate_l.get_center(),
                        stroke_width=2, color=BEAM_COLOR)
        string_r = Line(top + RIGHT * 2.6, plate_r.get_center(),
                        stroke_width=2, color=BEAM_COLOR)
        balance = VGroup(pivot, beam, string_l, string_r, plate_l, plate_r)

        # 左の皿: 太陽1個ぶんの重さ (白色矮星より大きく見せる)
        mini_sun = make_glow_ball(0.7, SUN_COLOR, SUN_RIM,
                                  plate_l.get_center() + UP * 0.75)
        sun_label = Text("太陽1個ぶんの重さ / one Sun's mass",
                         font_size=16, color=SUN_COLOR)
        sun_label.next_to(plate_l, DOWN, buff=0.15)

        self.play(FadeIn(balance), run_time=0.9)
        self.play(FadeIn(mini_sun, scale=0.7), FadeIn(sun_label), run_time=0.8)

        # 右の皿: 白色矮星を載せる (太陽より小さいのに同じ重さ)
        self.play(
            core.animate.scale(0.45).move_to(plate_r.get_center() + UP * 0.45),
            run_time=1.2,
            rate_func=rate_functions.ease_in_out_sine,
        )
        wd_label = Text("白色矮星 / white dwarf", font_size=16, color=WD_RIM)
        wd_label.next_to(plate_r, DOWN, buff=0.15)
        self.play(FadeIn(wd_label), run_time=0.5)

        # 釣り合っていることを強調 (竿は水平のまま)
        self.play(Indicate(beam, color=YELLOW_A, scale_factor=1.03),
                  run_time=0.9)

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
