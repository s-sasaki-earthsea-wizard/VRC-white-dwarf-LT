"""位相空間でみる不確定性原理のアニメーション。

電子は「ここにいる」と一点に決められない――位置 x と運動量 p の位相空間で、
電子は鋭い一点ではなく面積 h のマスとして「広がり」を持つ。本質は次の2点:

    ・「このマスのどこか」までは *面的に* わかる
    ・しかし「どこにいるか」を *点で* 指定することはできない

slides-jp/assets/images/phase_space_cell.svg を下敷きにした映像で、
yt_script.md の「4-1. 性質その1：電子は『ぼやけている』」に対応する。

構成:
    ① 位相空間の軸 (位置 x / 運動量 p) が現れる
    ② 電子を鋭い一点に置こうとすると、点が定まらずぼやけて広がる
    ③ ぼやけが1つのマス (面積 = h) に落ち着く。「このマスのどこか」は面的に分かる
    ④ 位置 Δx をしぼると運動量 Δp が広がる (マスが伸縮)。面積は常に h
    ⑤ 位相空間全体が h のマスで敷き詰められる

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/uncertainty_principle.py UncertaintyPrinciple   # 低画質プレビュー
    manim -pqh manim-scripts/uncertainty_principle.py UncertaintyPrinciple   # 高画質
"""

import numpy as np
from manim import *

# 配色 (参考 SVG phase_space_cell.svg に準拠)
AXIS_COLOR = "#5F5E5A"      # 位相空間の軸
GRID_COLOR = "#B4B2A9"      # マス目の格子線
CELL_FILL = "#CECBF6"       # 強調マスの塗り (藤色)
CELL_STROKE = "#534AB7"     # 強調マスの輪郭
ELECTRON_COLOR = "#185FA5"  # 電子
BLUR_COLOR = "#7E76D6"      # ぼやけ (電子と強調マスの中間色)

# 位相空間の描画範囲 (Axes のシーン座標)
X_RANGE = [0.0, 7.0, 1.0]   # 位置 x
P_RANGE = [0.0, 5.0, 1.0]   # 運動量 p

# マス1個の大きさ (位相空間の単位)。面積 CELL_DX * CELL_DP = h を表す
CELL_DX = 1.0   # 位置方向の幅 Δx
CELL_DP = 1.0   # 運動量方向の高さ Δp

# 強調マスの左下隅 (位相空間座標)
CELL_X0 = 3.0
CELL_P0 = 2.0


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


def make_blur_cloud(center: np.ndarray, half_w: float, half_h: float,
                    n_layers: int = 5) -> VGroup:
    """中心まわりに広がる「ぼやけた雲」を同心の半透明楕円で作る。

    Args:
        center: 雲の中心 (シーン座標)。
        half_w: 最外層の横半径。
        half_h: 最外層の縦半径。
        n_layers: 重ねる楕円の枚数 (多いほど滑らかなグラデーション)。

    Returns:
        外ほど薄く内ほど濃い楕円を重ねた VGroup。
    """
    cloud = VGroup()
    for i in range(n_layers):
        t = (i + 1) / n_layers  # 1 が最外層
        ellipse = Ellipse(width=2 * half_w * t, height=2 * half_h * t)
        ellipse.move_to(center)
        ellipse.set_stroke(width=0)
        ellipse.set_fill(BLUR_COLOR, opacity=0.16 * (1.0 - t) + 0.06)
        cloud.add(ellipse)
    return cloud


class UncertaintyPrinciple(Scene):
    """位相空間で「点に決められない／マスのどこかは分かる」を見せるシーン。"""

    def construct(self):
        self.caption = None

        # --- 位相空間の軸 (横: 位置 x / 縦: 運動量 p) ---
        axes = Axes(
            x_range=X_RANGE,
            y_range=P_RANGE,
            x_length=8.4,
            y_length=5.0,
            axis_config={
                "color": AXIS_COLOR,
                "stroke_width": 2,
                "include_ticks": False,
                "tip_width": 0.18,
                "tip_height": 0.18,
            },
        )
        axes.to_edge(UP, buff=0.7).shift(DOWN * 0.15)
        self.axes = axes

        x_label = Text("位置 x", font_size=24, color=GRAY_C)
        x_label.next_to(axes.x_axis.get_end(), DOWN, buff=0.18)
        p_label = Text("運動量 p", font_size=24, color=GRAY_C)
        p_label.next_to(axes.y_axis.get_end(), RIGHT, buff=0.18)

        self.play(Create(axes), run_time=1.2)
        self.play(FadeIn(x_label, shift=UP * 0.1), FadeIn(p_label, shift=RIGHT * 0.1),
                  run_time=0.8)

        # 強調マスの中心 (このシーンを通じて電子・ぼやけの基準点になる)
        cell_center = axes.c2p(CELL_X0 + CELL_DX / 2, CELL_P0 + CELL_DP / 2)

        # --- ② 一点に置こうとすると、ぼやけて広がる ---
        self.show_caption("電子は一点には決められない",
                          "An electron can't be pinned to a point")

        # まず鋭い一点として電子を置く
        electron = Dot(cell_center, radius=0.06, color=ELECTRON_COLOR)
        electron.set_stroke(WHITE, width=1)
        crosshair = self._make_crosshair(cell_center, size=0.32)
        self.play(GrowFromCenter(electron), Create(crosshair), run_time=0.7)
        self.wait(0.4)

        # 点が定まらず、もやっと広がる (十字は役に立たず消える)
        cell_dx_scene = axes.c2p(CELL_DX, 0)[0] - axes.c2p(0, 0)[0]
        cell_dp_scene = axes.c2p(0, CELL_DP)[1] - axes.c2p(0, 0)[1]
        blur = make_blur_cloud(cell_center, cell_dx_scene * 0.46, cell_dp_scene * 0.46)
        self.show_caption("位置も運動量も、つねに少しぼやける",
                          "Position and momentum are always a little blurred")
        self.play(
            FadeOut(crosshair),
            FadeIn(blur),
            electron.animate.set_opacity(0.35).scale(0.8),
            run_time=1.2,
        )
        # ぼやけをゆらして「点に定まらない」感じを出す
        self.play(blur.animate.scale(1.12), rate_func=there_and_back,
                  run_time=1.4)
        self.wait(0.3)

        # --- ③ ぼやけが1つのマス (面積 h) に落ち着く ---
        cell = self._make_cell(CELL_X0, CELL_P0, CELL_DX, CELL_DP)
        self.show_caption("分かるのは「このマスのどこか」だけ（面積 ≈ h）",
                          "We only know it's somewhere in this cell (area ≈ h)")
        self.play(
            FadeOut(blur),
            FadeOut(electron),
            FadeIn(cell["fill"]),
            Create(cell["frame"]),
            run_time=1.0,
        )

        # マス内をチラチラ動く電子: 点では指定できないことを示す
        self.fuzzy_pos = cell_center.copy()
        fuzzy = Dot(cell_center, radius=0.07, color=ELECTRON_COLOR)
        fuzzy.set_stroke(WHITE, width=1)
        self._rng = np.random.default_rng(3)
        self._cell_center = cell_center
        self._cell_half = np.array([cell_dx_scene * 0.5, cell_dp_scene * 0.5, 0.0])
        fuzzy.add_updater(self._jitter)
        self.add(fuzzy)

        # h^3 等の注記 (参考 SVG の Δx·Δp ≈ h)
        relation = self._make_relation(cell["frame"])
        self.play(FadeIn(relation, shift=RIGHT * 0.2), run_time=0.8)
        self.wait(2.2)
        fuzzy.remove_updater(self._jitter)
        self.play(FadeOut(fuzzy), run_time=0.4)

        # --- ④ 位置をしぼると運動量が広がる (面積は h のまま) ---
        self.show_caption("位置をしぼると運動量が広がる ― 面積は h のまま",
                          "Sharpen Δx and Δp spreads — the area stays h")
        self._morph_cell(cell, relation, factor=0.4)   # Δx を 0.4 倍, Δp を 2.5 倍
        self.wait(0.6)
        self._morph_cell(cell, relation, factor=1.0 / 0.4)  # 元に戻す (逆方向も等価)
        self.wait(0.6)

        # --- ⑤ 位相空間全体を h のマスで敷き詰める ---
        self.show_caption("位相空間は h のマスで埋め尽くされる",
                          "Phase space is tiled by cells of area h")
        grid = self._make_full_grid()
        self.play(FadeOut(relation), run_time=0.4)
        self.play(Create(grid), run_time=1.6, lag_ratio=0.04)
        # 強調マスを最前面に保ち、敷き詰めの中の「1マス」として際立たせる
        self.play(
            cell["fill"].animate.set_fill(CELL_FILL, opacity=0.9),
            Indicate(cell["frame"], color=CELL_STROKE, scale_factor=1.0),
            run_time=1.0,
        )
        self.wait(1.8)

    # ------------------------------------------------------------------
    # 部品づくり
    # ------------------------------------------------------------------
    def _make_crosshair(self, center: np.ndarray, size: float) -> VGroup:
        """「一点に決めようとする」十字カーソルを作る。"""
        h = Line(center + LEFT * size, center + RIGHT * size,
                 stroke_width=1.5, color=GRAY_B)
        v = Line(center + DOWN * size, center + UP * size,
                 stroke_width=1.5, color=GRAY_B)
        return VGroup(h, v)

    def _make_cell(self, x0: float, p0: float, dx: float, dp: float) -> dict:
        """位相空間座標で指定した1マス (塗り + 枠) を作る。

        Args:
            x0: マス左下の位置 x。
            p0: マス左下の運動量 p。
            dx: 位置方向の幅 Δx。
            dp: 運動量方向の高さ Δp。

        Returns:
            "fill" (Polygon) と "frame" (Rectangle) を持つ辞書。
        """
        corners = [
            self.axes.c2p(x0, p0),
            self.axes.c2p(x0 + dx, p0),
            self.axes.c2p(x0 + dx, p0 + dp),
            self.axes.c2p(x0, p0 + dp),
        ]
        fill = Polygon(*corners, stroke_width=0)
        fill.set_fill(CELL_FILL, opacity=0.55)

        width = corners[1][0] - corners[0][0]
        height = corners[2][1] - corners[1][1]
        frame = Rectangle(width=width, height=height)
        frame.set_stroke(CELL_STROKE, width=2.5)
        frame.set_fill(opacity=0)
        frame.move_to(fill.get_center())
        return {"fill": fill, "frame": frame, "dx": dx, "dp": dp,
                "x0": x0, "p0": p0}

    def _make_relation(self, frame: Mobject) -> VGroup:
        """マスの脇に Δx・Δp ≈ h の注記を作る。"""
        formula = Text("Δx · Δp ≈ h", font_size=26, color=CELL_STROKE, weight=BOLD)
        note = Text("セル面積 = h / cell area = h", font_size=18, color=GRAY_C)
        group = VGroup(formula, note).arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        group.next_to(frame, RIGHT, buff=0.5)
        return group

    def _make_full_grid(self) -> VGroup:
        """位相空間全体を CELL_DX × CELL_DP のマスで敷き詰める格子線を作る。"""
        grid = VGroup()
        x_min, x_max = X_RANGE[0], X_RANGE[1]
        p_min, p_max = P_RANGE[0], P_RANGE[1]

        x = x_min
        while x <= x_max + 1e-6:
            line = Line(self.axes.c2p(x, p_min), self.axes.c2p(x, p_max),
                        stroke_width=0.8, color=GRID_COLOR)
            grid.add(line)
            x += CELL_DX

        p = p_min
        while p <= p_max + 1e-6:
            line = Line(self.axes.c2p(x_min, p), self.axes.c2p(x_max, p),
                        stroke_width=0.8, color=GRID_COLOR)
            grid.add(line)
            p += CELL_DP
        return grid

    # ------------------------------------------------------------------
    # アニメーション処理
    # ------------------------------------------------------------------
    def _jitter(self, mob: Mobject, dt: float):
        """マス内で電子をランダムに揺らし、点に定まらない様子を出す。"""
        # 目標位置へ少しずつ寄せながら、毎フレーム新しい目標を引き直す
        target = self._cell_center + (self._rng.uniform(-0.7, 0.7, 3)
                                      * self._cell_half)
        target[2] = 0.0
        self.fuzzy_pos += (target - self.fuzzy_pos) * min(dt * 6.0, 1.0)
        mob.move_to(self.fuzzy_pos)

    def _morph_cell(self, cell: dict, relation: Mobject, factor: float):
        """マスの Δx を factor 倍, Δp を 1/factor 倍にして面積 h を保つ。

        Args:
            cell: _make_cell が返したマス辞書 (この場で更新される)。
            relation: マスに追従させる Δx・Δp ≈ h の注記。
            factor: Δx に掛ける倍率 (<1 で位置をしぼる)。
        """
        new_dx = cell["dx"] * factor
        new_dp = cell["dp"] / factor
        # 面積中心を保ったまま左下隅を計算し直す
        cx = cell["x0"] + cell["dx"] / 2
        cp = cell["p0"] + cell["dp"] / 2
        new_x0 = cx - new_dx / 2
        new_p0 = cp - new_dp / 2

        new_cell = self._make_cell(new_x0, new_p0, new_dx, new_dp)
        new_relation = self._make_relation(new_cell["frame"])
        self.play(
            Transform(cell["fill"], new_cell["fill"]),
            Transform(cell["frame"], new_cell["frame"]),
            Transform(relation, new_relation),
            run_time=1.2,
            rate_func=rate_functions.ease_in_out_sine,
        )
        # 辞書の論理状態も更新 (次の morph の基準になる)
        cell.update({"dx": new_dx, "dp": new_dp, "x0": new_x0, "p0": new_p0})

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
