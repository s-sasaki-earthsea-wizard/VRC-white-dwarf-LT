"""電子縮退圧の「強さ」と「弱点」のアニメーション (2シーン)。

シーン1 CompressionSpring (yt_script.md「5. 詰め込むほど強くなる圧力」):
    星を圧縮するほど中の電子が速く動き、圧力メーターが急カーブで
    跳ね上がる様子を見せる。続けて「押すほど強く押し返すバネ」の
    メタファーで縮退圧の心強さを描き、最後に弱点の存在を予告する。

シーン2 PressureCurves (yt_script.md「6. 光速の壁 ―― バネが弱くなる」):
    「重力に勝つために必要な圧力」の線に対して、
        ・光速を気にしない世界: P ∝ n^(5/3) の急カーブ → 必ず追いついて安定
        ・光速に近づいた世界:   P ∝ n^(4/3) の緩いカーブ → もう追いつけない
    を並べ、縮退圧というバネが頼りなくなる理由を見せる。

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/degeneracy_pressure_curve.py CompressionSpring  # シーン1
    manim -pql manim-scripts/degeneracy_pressure_curve.py PressureCurves     # シーン2
"""

import numpy as np
from manim import *

# 配色 (既存スクリプトの色味に準拠)
STAR_COLOR = "#EAF2FF"          # 白色矮星 (白〜淡青)
STAR_RIM = "#9FB8D8"
ELECTRON_COLOR = "#185FA5"      # 電子 (青)
COMPRESS_COLOR = "#2F80ED"      # 圧縮の矢印 (重力の青)
GAUGE_FRAME = "#8A8782"         # 圧力メーターの枠
PRESSURE_COLOR = "#6FBF3A"      # 圧力 (緑)
SPRING_COLOR = "#6FBF3A"        # バネ (緑)
WALL_COLOR = "#5F5E5A"          # バネの壁
AXIS_COLOR = "#5F5E5A"          # グラフの軸
NEED_COLOR = "#C9A227"          # 重力が要求する圧力 (金)
STEEP_COLOR = "#185FA5"         # 急カーブ P ∝ n^(5/3) (青)
SHALLOW_COLOR = "#C8643C"       # 緩いカーブ P ∝ n^(4/3) (テラコッタ)

# シーン1: 星と電子
STAR_CENTER = np.array([-2.6, 0.55, 0.0])
R_START = 1.9                   # 圧縮前の星の半径
R_MID = 1.5                     # 1段階目の圧縮
R_END = 1.15                    # 2段階目の圧縮
N_ELECTRONS = 12                # 星の中の電子の数

# 圧力メーター: P ∝ n^(5/3) ∝ R^(-5) を 0〜1 に規格化して表示する
GAUGE_POS = np.array([2.6, 0.55, 0.0])
GAUGE_H = 3.6                   # メーターの高さ
GAUGE_W = 0.55                  # メーターの幅


def pressure_frac(radius: float) -> float:
    """半径から圧力メーターの目盛り (0〜1) を計算する。

    P ∝ R^(-5) を、R_START で 0・R_END で 1 になるように規格化する。

    Args:
        radius: 現在の星の半径。

    Returns:
        メーターの埋まり具合 (0〜1)。
    """
    p = (R_START / radius) ** 5
    p_max = (R_START / R_END) ** 5
    return (p - 1.0) / (p_max - 1.0)


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。"""
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


class CompressionSpring(Scene):
    """圧縮 → 圧力急上昇 → 強いバネ、を見せるシーン。"""

    def construct(self):
        self.caption = None
        self.radius = ValueTracker(R_START)

        # --- 星本体 (半径トラッカーに追従) ---
        star = always_redraw(self._make_star)
        self.show_caption("白色矮星を、重力でさらに圧縮してみる",
                          "Let gravity squeeze the white dwarf further")
        self.play(FadeIn(star), run_time=1.0)

        # 中の電子 (圧縮されるほど速く揺れる)
        self._setup_electrons()
        self.add(self.electrons)
        self.electrons.add_updater(self._jitter)

        # 圧縮の矢印 (星の外から内向き、半径に追従)
        arrows = always_redraw(self._make_compress_arrows)
        self.add(arrows)

        # 圧力メーター
        gauge = self._make_gauge()
        self.play(FadeIn(gauge), run_time=0.8)
        self.wait(0.6)

        # --- 圧縮1段階目 ---
        self.show_caption("詰め込むほど、奥の席の電子は速くなる",
                          "Squeezing makes the deep-seat electrons faster")
        self.play(self.radius.animate.set_value(R_MID), run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(0.6)

        # --- 圧縮2段階目: メーターが急カーブで跳ね上がる ---
        self.show_caption("圧力は急カーブで跳ね上がる",
                          "The pressure shoots up steeply")
        self.play(self.radius.animate.set_value(R_END), run_time=2.2,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.0)

        self.electrons.remove_updater(self._jitter)
        self.remove(arrows)
        # always_redraw の更新を止めてからフェードアウトする
        star.clear_updaters()
        for sub in gauge:
            sub.clear_updaters()
        self.play(FadeOut(star), FadeOut(self.electrons), FadeOut(gauge),
                  run_time=0.8)

        # --- バネのメタファー ---
        self._spring_metaphor()

    # ------------------------------------------------------------------
    # 星まわりの部品
    # ------------------------------------------------------------------
    def _make_star(self) -> VGroup:
        """半径トラッカーに追従する星本体を作る (always_redraw 用)。"""
        r = self.radius.get_value()
        group = VGroup()
        for scale, opacity in [(1.0, 0.10), (0.7, 0.16), (0.4, 0.28)]:
            layer = Circle(radius=r * scale)
            layer.set_fill(STAR_COLOR, opacity=opacity).set_stroke(width=0)
            layer.move_to(STAR_CENTER)
            group.add(layer)
        rim = Circle(radius=r).set_stroke(STAR_RIM, width=2)
        rim.set_fill(opacity=0).move_to(STAR_CENTER)
        group.add(rim)
        return group

    def _make_compress_arrows(self) -> VGroup:
        """星の外から内向きに押す圧縮の矢印を作る (always_redraw 用)。"""
        r = self.radius.get_value()
        arrows = VGroup()
        for ang in np.linspace(0, TAU, 8, endpoint=False):
            d = np.array([np.cos(ang), np.sin(ang), 0.0])
            arrows.add(Arrow(
                start=STAR_CENTER + d * (r + 0.75),
                end=STAR_CENTER + d * (r + 0.15),
                buff=0, color=COMPRESS_COLOR, stroke_width=5,
                tip_length=0.18,
                max_stroke_width_to_length_ratio=25,
                max_tip_length_to_length_ratio=0.5,
            ))
        return arrows

    def _setup_electrons(self):
        """星の中に電子を配置し、揺れの初期状態を作る。"""
        rng = np.random.default_rng(7)
        self._rng = rng
        self.electrons = VGroup()
        self._frac = []   # 中心からの相対距離 (圧縮時も保たれる)
        self._pos = []
        for _ in range(N_ELECTRONS):
            ang = rng.uniform(0, TAU)
            frac = 0.85 * np.sqrt(rng.uniform())
            d = np.array([np.cos(ang), np.sin(ang), 0.0])
            self._frac.append(d * frac)
            pos = STAR_CENTER + d * frac * R_START
            self._pos.append(pos.copy())
            dot = Dot(radius=0.08, color=ELECTRON_COLOR).set_stroke(WHITE, width=1)
            dot.move_to(pos)
            self.electrons.add(dot)

    def _jitter(self, group: VGroup, dt: float):
        """電子を揺らす。圧縮されるほど振幅と速さが増す。"""
        r = self.radius.get_value()
        boost = (R_START / r) ** 2.5  # 圧縮による「速さ」の増幅
        amp = 0.05 * boost
        rate = 3.0 * boost
        for i, dot in enumerate(group):
            home = STAR_CENTER + self._frac[i] * r
            target = home + np.array([
                self._rng.uniform(-1, 1) * amp,
                self._rng.uniform(-1, 1) * amp,
                0.0,
            ])
            self._pos[i] += (target - self._pos[i]) * min(dt * rate, 1.0)
            dot.move_to(self._pos[i])

    def _make_gauge(self) -> VGroup:
        """半径トラッカーに連動する圧力メーターを作る。"""
        frame = RoundedRectangle(width=GAUGE_W, height=GAUGE_H,
                                 corner_radius=0.12)
        frame.set_stroke(GAUGE_FRAME, width=2.5).set_fill(BLACK, opacity=0.3)
        frame.move_to(GAUGE_POS)

        def fill_bar():
            frac = np.clip(pressure_frac(self.radius.get_value()), 0.0, 1.0)
            h = max(frac * (GAUGE_H - 0.16), 0.03)
            bar = Rectangle(width=GAUGE_W - 0.18, height=h)
            bar.set_stroke(width=0).set_fill(PRESSURE_COLOR, opacity=0.95)
            bottom = GAUGE_POS - np.array([0.0, (GAUGE_H - 0.16) / 2, 0.0])
            bar.move_to(bottom + np.array([0.0, h / 2, 0.0]))
            return bar

        bar = always_redraw(fill_bar)
        jp = Text("圧力", font_size=22, color=PRESSURE_COLOR, weight=BOLD)
        en = Text("pressure", font_size=16, color=GRAY_B)
        label = VGroup(jp, en).arrange(DOWN, buff=0.06)
        label.next_to(frame, UP, buff=0.2)
        return VGroup(bar, frame, label)

    # ------------------------------------------------------------------
    # バネのメタファー
    # ------------------------------------------------------------------
    def _spring_metaphor(self):
        """押すほど強く押し返すバネのカットを見せる。"""
        self.show_caption("押すほど強く押し返す、超強力なバネ",
                          "A spring that pushes back harder the more you press")

        wall_x = -4.6
        wall = Line([wall_x, -0.9, 0], [wall_x, 1.9, 0],
                    stroke_width=8, color=WALL_COLOR)
        self.block_x = ValueTracker(0.6)

        def spring():
            return self._make_spring(
                np.array([wall_x, 0.5, 0.0]),
                np.array([self.block_x.get_value() - 0.45, 0.5, 0.0]),
            )

        def block():
            b = Square(side_length=0.9)
            b.set_fill(COMPRESS_COLOR, opacity=0.35)
            b.set_stroke(COMPRESS_COLOR, width=2.5)
            b.move_to([self.block_x.get_value(), 0.5, 0])
            return b

        spring_mob = always_redraw(spring)
        block_mob = always_redraw(block)
        self.play(Create(wall), FadeIn(spring_mob), FadeIn(block_mob),
                  run_time=1.0)
        self.wait(0.3)

        # 押し込む → 強く跳ね返される、を2回 (2回目はより深く・より強く)
        for push, rebound in [(-1.3, 1.0), (-2.4, 1.6)]:
            self.play(self.block_x.animate.set_value(push), run_time=0.9,
                      rate_func=rate_functions.ease_in_sine)
            self.play(self.block_x.animate.set_value(rebound), run_time=0.55,
                      rate_func=rate_functions.ease_out_quad)
            self.wait(0.25)

        # 弱点の予告
        self.show_caption("…ところが、このバネには弱点がある",
                          "…but this spring has a weakness")
        self.wait(2.0)

    def _make_spring(self, start: np.ndarray, end: np.ndarray,
                     n_coils: int = 8) -> VMobject:
        """壁とブロックの間のジグザグばねを作る。"""
        length = end[0] - start[0]
        points = [start]
        for i in range(n_coils):
            t = (i + 0.5) / n_coils
            y = 0.5 + (0.28 if i % 2 == 0 else -0.28)
            points.append(np.array([start[0] + length * t, y, 0.0]))
        points.append(end)
        spring = VMobject(stroke_color=SPRING_COLOR, stroke_width=4)
        spring.set_points_as_corners(points)
        return spring

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption


class PressureCurves(Scene):
    """急カーブ(5/3乗)と緩いカーブ(4/3乗)を重力の要求と比べるシーン。"""

    # 描画範囲とカーブの係数 (見やすさ優先で選んだ無次元の値)
    X_MAX = 6.5
    Y_MAX = 8.0
    NEED_COEF = 0.62    # 重力が要求する圧力 ∝ x^(4/3)
    STEEP_COEF = 0.45   # 急カーブ ∝ x^(5/3)
    SHALLOW_COEF = 0.45  # 緩いカーブ ∝ x^(4/3)

    def construct(self):
        self.caption = None

        # --- 座標軸 ---
        axes = Axes(
            x_range=[0, self.X_MAX, 1],
            y_range=[0, self.Y_MAX, 2],
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

        x_label = Text("ぎゅうぎゅう度（密度）", font_size=22, color=GRAY_C)
        x_label.next_to(axes.x_axis.get_end(), DOWN, buff=0.18)
        x_label.shift(LEFT * 0.8)
        y_label = Text("圧力", font_size=22, color=GRAY_C)
        y_label.next_to(axes.y_axis.get_end(), RIGHT, buff=0.18)
        self.play(Create(axes), run_time=1.2)
        self.play(FadeIn(x_label), FadeIn(y_label), run_time=0.7)

        # --- 重力が要求する圧力 (これを上回れば星は安定) ---
        self.show_caption("重力に勝つには、この線より強い圧力が要る",
                          "To beat gravity, pressure must exceed this line")
        need = axes.plot(lambda x: self.NEED_COEF * x ** (4 / 3),
                         x_range=[0, 6.3], color=NEED_COLOR, stroke_width=4)
        need_dashed = DashedVMobject(need, num_dashes=40)
        need_label = Text("重力の要求 / what gravity demands",
                          font_size=20, color=NEED_COLOR, weight=BOLD)
        # 曲線と重ならない左上の空き地に置く (色でカーブと対応づける)
        need_label.move_to(axes.c2p(2.1, 6.4))
        self.play(Create(need_dashed), run_time=1.4)
        self.play(FadeIn(need_label), run_time=0.6)
        self.wait(0.5)

        # --- 急カーブ: 光速を気にしない世界 ---
        self.show_caption("光速を気にしない世界：圧力は急カーブで増える",
                          "Without the light-speed wall, pressure rises steeply")
        steep = axes.plot(lambda x: self.STEEP_COEF * x ** (5 / 3),
                          x_range=[0, 5.6], color=STEEP_COLOR, stroke_width=5)
        steep_label = Text("急カーブ / steep", font_size=20,
                           color=STEEP_COLOR, weight=BOLD)
        steep_label.next_to(axes.c2p(5.6, self.STEEP_COEF * 5.6 ** (5 / 3)),
                            LEFT, buff=0.25)
        self.play(Create(steep), run_time=1.6)
        self.play(FadeIn(steep_label), run_time=0.6)

        # 交点 = 釣り合い (安定) の強調
        x_cross = (self.NEED_COEF / self.STEEP_COEF) ** 3
        y_cross = self.NEED_COEF * x_cross ** (4 / 3)
        cross_dot = Dot(axes.c2p(x_cross, y_cross), radius=0.09,
                        color=PRESSURE_COLOR).set_stroke(WHITE, width=1.5)
        cross_label = Text("ここで釣り合う＝安定", font_size=20,
                           color=PRESSURE_COLOR, weight=BOLD)
        cross_label.next_to(cross_dot, UL, buff=0.15)
        self.show_caption("急カーブなら必ず重力に追いつき、星は安定する",
                          "The steep curve always catches up — the star is stable")
        self.play(GrowFromCenter(cross_dot), FadeIn(cross_label), run_time=0.9)
        self.wait(1.2)

        # --- 緩いカーブ: 光速に近づいた世界 ---
        self.show_caption("光速の壁にぶつかると、カーブは緩くなる",
                          "Near the light-speed wall, the curve flattens")
        shallow = axes.plot(lambda x: self.SHALLOW_COEF * x ** (4 / 3),
                            x_range=[0, 6.3], color=SHALLOW_COLOR,
                            stroke_width=5)
        shallow_label = Text("緩いカーブ / flattened", font_size=20,
                             color=SHALLOW_COLOR, weight=BOLD)
        shallow_label.next_to(axes.c2p(6.3, self.SHALLOW_COEF * 6.3 ** (4 / 3)),
                              DOWN, buff=0.3)
        self.play(
            FadeOut(cross_dot), FadeOut(cross_label),
            steep.animate.set_stroke(opacity=0.3),
            steep_label.animate.set_opacity(0.3),
            run_time=0.8,
        )
        self.play(Create(shallow), run_time=1.6)
        self.play(FadeIn(shallow_label), run_time=0.6)
        self.wait(0.4)

        # --- どこまで行っても重力の要求に届かない ---
        self.show_caption("もうどこまで行っても、重力に追いつけない",
                          "Now it can never catch up with gravity")
        x_gap = 4.4
        gap = DoubleArrow(
            axes.c2p(x_gap, self.SHALLOW_COEF * x_gap ** (4 / 3)),
            axes.c2p(x_gap, self.NEED_COEF * x_gap ** (4 / 3)),
            color=NEED_COLOR, stroke_width=3, buff=0.0, tip_length=0.16,
        )
        gap_note = Text("届かない", font_size=20, color=NEED_COLOR, weight=BOLD)
        gap_note.next_to(gap, LEFT, buff=0.15)
        self.play(GrowFromCenter(gap), FadeIn(gap_note), run_time=0.9)
        self.play(Indicate(gap, color=NEED_COLOR, scale_factor=1.15),
                  run_time=0.9)
        self.wait(2.0)

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
