"""Ia型超新星と「宇宙の明るさのものさし」のアニメーション。

白色矮星が隣の星からガスを吸い込んで重くなり、チャンドラセカール限界
(約1.4太陽質量) を超えた瞬間に大爆発を起こす――Ia型超新星。
限界の重さで爆発するため明るさがほぼ一定になり、宇宙の距離を測る
「標準光源」として使えることまでを見せる。

yt_script.md の「8. 限界を超えたら何が起きる？」の前半に対応するカット。

構成:
    ① 白色矮星と隣の星 (連星)。ガスの流れが白色矮星に降り積もる
    ② 質量カウンタが 1.4 太陽質量へ向けて上がっていく
    ③ 限界を超えた瞬間 ― 大爆発 (Ia型超新星)
    ④ 遠くの銀河に同じ明るさの爆発が点々と灯る = 明るさのものさし

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/type_ia_supernova.py TypeIaSupernova   # 低画質プレビュー
    manim -pqh manim-scripts/type_ia_supernova.py TypeIaSupernova   # 高画質
"""

import numpy as np
from manim import *

# 配色
COMPANION_COLOR = "#D14B3A"   # 隣の星 (赤いガスを供給する側)
COMPANION_RIM = "#8F2C1E"
WD_CORE = "#EAF2FF"           # 白色矮星 (白〜淡青)
WD_RIM = "#9FB8D8"
STREAM_COLOR = "#E58A6F"      # 降着するガスの流れ
LIMIT_COLOR = "#C9A227"       # 限界の強調 (金)
EXPLODE_COLOR = "#FFD66B"     # 爆発の光
GALAXY_COLOR = "#8A8782"      # 遠くの銀河
CANDLE_COLOR = "#FFD66B"      # 標準光源の爆発 (すべて同じ色・同じ大きさ)

COMPANION_CENTER = np.array([-3.9, 0.7, 0.0])
COMPANION_RADIUS = 1.45
WD_CENTER = np.array([3.0, -0.1, 0.0])
WD_RADIUS = 0.5

M_START = 1.20                # 降着開始時の質量 [太陽質量]
M_LIMIT = 1.4                 # チャンドラセカール限界


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。"""
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


def make_glow_ball(radius: float, color: str, rim_color: str,
                   center: np.ndarray) -> VGroup:
    """中心ほど明るいグローを重ねた星の球体を作る。"""
    group = VGroup()
    for scale, opacity in [(1.0, 0.12), (0.72, 0.18), (0.45, 0.32)]:
        layer = Circle(radius=radius * scale)
        layer.set_fill(color, opacity=opacity).set_stroke(width=0)
        layer.move_to(center)
        group.add(layer)
    rim = Circle(radius=radius).set_stroke(rim_color, width=1.5, opacity=0.9)
    rim.set_fill(opacity=0).move_to(center)
    group.add(rim)
    return group


class TypeIaSupernova(Scene):
    """降着 → 限界超え → 爆発 → 標準光源、を見せるシーン。"""

    def construct(self):
        self.caption = None
        self.mass = ValueTracker(M_START)

        # --- ① 連星の提示 ---
        companion = make_glow_ball(COMPANION_RADIUS, COMPANION_COLOR,
                                   COMPANION_RIM, COMPANION_CENTER)
        wd = make_glow_ball(WD_RADIUS, WD_CORE, WD_RIM, WD_CENTER)
        companion_label = Text("となりの星 / companion", font_size=20,
                               color=COMPANION_COLOR)
        companion_label.next_to(COMPANION_CENTER + DOWN * COMPANION_RADIUS,
                                DOWN, buff=0.25)
        wd_label = Text("白色矮星 / white dwarf", font_size=20, color=WD_RIM)
        wd_label.next_to(WD_CENTER + DOWN * WD_RADIUS, DOWN, buff=0.25)

        self.show_caption("白色矮星が、となりの星からガスを吸い込む",
                          "The white dwarf siphons gas from its companion")
        self.play(FadeIn(companion, scale=0.9), FadeIn(wd, scale=0.9),
                  FadeIn(companion_label), FadeIn(wd_label), run_time=1.4)

        # 質量カウンタ
        readout = self._make_mass_readout()
        self.play(FadeIn(readout), run_time=0.6)

        # --- ② 降着でだんだん重くなる ---
        stream_path = self._make_stream_path()
        stream_curve = stream_path.copy()
        stream_curve.set_stroke(STREAM_COLOR, width=2, opacity=0.45)
        self.play(Create(stream_curve), run_time=0.8)

        self.show_caption("吸い込むほど重くなり、限界に近づいていく",
                          "Each gulp adds mass, edging it toward the limit")
        # ガス粒の流れと質量の上昇を同時に進める
        flow1 = self._make_flow_animation(stream_path, n_dots=10)
        self.play(
            AnimationGroup(flow1, self.mass.animate.set_value(1.32)),
            run_time=2.6,
        )
        flow2 = self._make_flow_animation(stream_path, n_dots=10)
        self.play(
            AnimationGroup(flow2, self.mass.animate.set_value(1.399)),
            run_time=2.6,
        )
        self.wait(0.4)

        # --- ③ 限界を超えた瞬間 ― 大爆発 ---
        self.show_caption("チャンドラセカール限界を超えた瞬間――",
                          "The instant it crosses the Chandrasekhar limit—")
        self.play(self.mass.animate.set_value(1.401), run_time=0.5)
        self.play(Indicate(readout, color=LIMIT_COLOR, scale_factor=1.15),
                  run_time=0.7)

        rings = VGroup(*[
            Circle(radius=0.1).set_stroke(EXPLODE_COLOR, width=6 - 1.5 * k)
            .set_fill(opacity=0).move_to(WD_CENTER)
            for k in range(3)
        ])
        whiteout = Rectangle(width=15, height=9)
        whiteout.set_fill(WHITE, opacity=0).set_stroke(width=0)
        self.add(rings, whiteout)
        self.play(
            Flash(WD_CENTER, color=EXPLODE_COLOR, flash_radius=1.4,
                  num_lines=24, line_length=0.6),
            *[ring.animate.scale(s).set_stroke(opacity=0)
              for ring, s in zip(rings, (32, 22, 13))],
            whiteout.animate.set_fill(opacity=0.92),
            run_time=1.5,
            rate_func=rate_functions.ease_in_sine,
        )

        # 白飛びからの暗転: 連星系は消え、爆発の名前を出す
        self.show_caption("これが Ia型超新星",
                          "A Type Ia supernova")
        # 質量カウンタの更新を止めてからフェードアウトする
        readout[1].clear_updaters()
        self.play(
            whiteout.animate.set_fill(opacity=0),
            FadeOut(companion), FadeOut(wd),
            FadeOut(companion_label), FadeOut(wd_label),
            FadeOut(stream_curve), FadeOut(readout), FadeOut(rings),
            run_time=1.6,
        )
        self.wait(0.6)

        # --- ④ 標準光源: 遠くの銀河に同じ明るさの爆発が灯る ---
        self._standard_candles()

    # ------------------------------------------------------------------
    # 部品づくり
    # ------------------------------------------------------------------
    def _make_mass_readout(self) -> VGroup:
        """白色矮星の質量カウンタを作る。限界に達すると金色になる。"""
        prefix = Text("M = ", font_size=24, color=WHITE)
        number = DecimalNumber(M_START, num_decimal_places=2, font_size=28,
                               color=WHITE)
        unit = Text(" 太陽質量 / solar masses", font_size=18, color=GRAY_B)
        group = VGroup(prefix, number, unit).arrange(RIGHT, buff=0.08)
        group.next_to(WD_CENTER + UP * WD_RADIUS, UP, buff=0.4)

        number.add_updater(lambda m: m.set_value(self.mass.get_value()))
        number.add_updater(
            lambda m: m.set_color(
                LIMIT_COLOR if self.mass.get_value() >= M_LIMIT - 0.002 else WHITE
            )
        )
        return group

    def _make_stream_path(self) -> VMobject:
        """隣の星の縁から白色矮星へ落ちるガスの経路を作る。"""
        start = COMPANION_CENTER + np.array([COMPANION_RADIUS * 0.92,
                                             -COMPANION_RADIUS * 0.25, 0.0])
        end = WD_CENTER + np.array([-WD_RADIUS * 0.9, WD_RADIUS * 0.3, 0.0])
        ctrl1 = start + np.array([1.6, -1.1, 0.0])
        ctrl2 = end + np.array([-1.8, -0.9, 0.0])
        return CubicBezier(start, ctrl1, ctrl2, end)

    def _make_flow_animation(self, path: VMobject, n_dots: int) -> AnimationGroup:
        """経路に沿ってガス粒が流れるアニメーションを作る。

        Args:
            path: ガス粒が沿う経路。
            n_dots: 流すガス粒の数。

        Returns:
            ガス粒の MoveAlongPath をずらしながらまとめた AnimationGroup。
        """
        anims = []
        for _ in range(n_dots):
            dot = Dot(radius=0.06, color=STREAM_COLOR)
            dot.set_stroke(width=0)
            dot.move_to(path.get_start())
            anims.append(Succession(
                FadeIn(dot, run_time=0.1),
                MoveAlongPath(dot, path, run_time=1.4,
                              rate_func=rate_functions.ease_in_sine),
                FadeOut(dot, run_time=0.15),
            ))
        return AnimationGroup(*anims, lag_ratio=0.12)

    def _standard_candles(self):
        """遠くの銀河に同じ明るさの爆発が灯るカットを見せる。"""
        self.show_caption("限界の重さで爆発するから、明るさはいつもほぼ同じ",
                          "Exploding at the same limit, they shine alike")

        # 散らばる銀河 (小さな楕円)
        rng = np.random.default_rng(21)
        galaxies = VGroup()
        positions = [(-4.8, 1.9), (-2.3, 0.4), (-0.4, 2.2), (1.8, 1.0),
                     (4.4, 2.0), (3.4, -0.6), (-3.6, -0.8), (0.9, -0.9)]
        for x, y in positions:
            g = Ellipse(width=rng.uniform(0.5, 0.9),
                        height=rng.uniform(0.18, 0.32))
            g.set_stroke(GALAXY_COLOR, width=1.5, opacity=0.8)
            g.set_fill(GALAXY_COLOR, opacity=0.25)
            g.rotate(rng.uniform(0, PI))
            g.move_to([x, y, 0])
            galaxies.add(g)
        self.play(LaggedStart(*[FadeIn(g, scale=0.7) for g in galaxies],
                              lag_ratio=0.08), run_time=1.4)

        # 同じ明るさ (同じ大きさ・同じ色) の爆発が順に灯る
        candle_spots = [galaxies[1], galaxies[4], galaxies[6], galaxies[3]]
        candles = VGroup()
        for g in candle_spots:
            spot = g.get_center() + np.array([0.12, 0.06, 0.0])
            candle = Dot(radius=0.14, color=CANDLE_COLOR)
            candle.set_stroke(WHITE, width=1.5)
            candles.add(candle.move_to(spot))
            self.play(
                Flash(spot, color=CANDLE_COLOR, flash_radius=0.45, num_lines=10),
                GrowFromCenter(candle),
                run_time=0.7,
            )
        self.wait(0.4)

        self.show_caption("宇宙の距離を測る『明るさのものさし』になる",
                          "They become standard candles to measure the cosmos")
        self.play(
            *[Indicate(c, color=CANDLE_COLOR, scale_factor=1.4)
              for c in candles],
            run_time=1.2,
        )
        self.wait(2.0)

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
