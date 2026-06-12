"""パウリの排他原理と電子の「席取りゲーム」のアニメーション。

白色矮星を支える電子縮退圧の核心、「電子は席を譲らない」を可視化する。
位置×運動量で区切ったマス目(席)に電子を入れていくと、

    ・1マスには電子2個まで (スピンの向き違い) しか入れない
    ・満員のマスに来た3個目は、弾かれて別のマスへ
    ・おとなしい(低運動量の)席から埋まり、後から来た電子は「速い席」へ
    ・絶対零度まで冷やしても、詰め込まれた電子は止まらない

yt_script.md の「4-2. 性質その2：電子は『席を譲らない』」と、温度計が
絶対零度まで下がるカット、最後の「電子縮退圧」の種明かしまでに対応する。
slides-jp/assets/images/pauli_exclusion.svg / fermi_sea_filling.svg が下敷き。

構成:
    ① 運動量で区切った「席」のマス目が現れる
    ② 1マスに2個まで: 2個で満員、3個目は弾かれて隣へ
    ③ 下の段(おとなしい席)から順に電子が詰まっていく
    ④ 上の段の電子ほど激しく動く (席取りゲームの結果)
    ⑤ 温度計が絶対零度まで下がっても、電子は動き続ける
    ⑥ この運動が圧力を生む = 電子縮退圧

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/pauli_exclusion_seats.py PauliExclusionSeats   # 低画質プレビュー
    manim -pqh manim-scripts/pauli_exclusion_seats.py PauliExclusionSeats   # 高画質
"""

import numpy as np
from manim import *

# 配色 (既存スクリプトの色味に準拠)
GRID_COLOR = "#B4B2A9"       # マス目の格子線
FRAME_COLOR = "#534AB7"      # マス目全体の枠
SPIN_UP_COLOR = "#185FA5"    # スピン上向きの電子 (青)
SPIN_DOWN_COLOR = "#C8643C"  # スピン下向きの電子 (テラコッタ)
FULL_COLOR = "#C9A227"       # 「満員」の強調 (金)
PRESSURE_COLOR = "#6FBF3A"   # 電子縮退圧の矢印 (緑)
THERMO_COLOR = "#D14B3A"     # 温度計の液柱 (赤)

# マス目 (席) の配置
N_COLS = 4                   # 横方向のマス数 (位置の違い)
N_ROWS = 4                   # 縦方向のマス数 (運動量の段)
CELL_W = 1.15                # マス1個の幅
CELL_H = 0.95                # マス1個の高さ
GRID_CENTER = np.array([0.9, 0.55, 0.0])  # マス目全体の中心

SEAT_OFFSET = 0.27           # マス内の左右の席のずらし幅
ELECTRON_RADIUS = 0.105      # 電子マーカーの半径

# 揺れ (運動) の強さ: 上の段ほど激しく動く
JITTER_BASE = 0.04           # 最下段の揺れ振幅
JITTER_PER_ROW = 0.035       # 1段上がるごとに増える振幅
JITTER_RATE_BASE = 4.0       # 揺れの追従速度 (最下段)
JITTER_RATE_PER_ROW = 3.5    # 1段上がるごとに増える追従速度


def grid_origin() -> np.ndarray:
    """マス目全体の左下隅のシーン座標を返す。"""
    return GRID_CENTER - np.array(
        [N_COLS * CELL_W / 2, N_ROWS * CELL_H / 2, 0.0]
    )


def cell_center(col: int, row: int) -> np.ndarray:
    """マス (col, row) の中心座標を返す。row=0 が最下段 (低運動量)。"""
    return grid_origin() + np.array(
        [(col + 0.5) * CELL_W, (row + 0.5) * CELL_H, 0.0]
    )


def seat_pos(col: int, row: int, side: int) -> np.ndarray:
    """マス内の席の座標を返す。

    Args:
        col: マスの列番号。
        row: マスの段番号 (0 が最下段)。
        side: -1 で左の席、+1 で右の席。

    Returns:
        席のシーン座標。
    """
    return cell_center(col, row) + np.array([side * SEAT_OFFSET, 0.0, 0.0])


def make_electron(side: int) -> Dot:
    """スピンの向き (席の左右) に応じた色の電子マーカーを作る。"""
    color = SPIN_UP_COLOR if side < 0 else SPIN_DOWN_COLOR
    return Dot(radius=ELECTRON_RADIUS, color=color).set_stroke(WHITE, width=1)


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。"""
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


class PauliExclusionSeats(Scene):
    """電子の席取りゲームから電子縮退圧までを見せるシーン。"""

    def construct(self):
        self.caption = None
        self.electrons = VGroup()  # 着席済みの電子
        self.homes = []            # 各電子の席 (定位置)
        self.rows_of = []          # 各電子の段番号 (揺れの強さに使う)
        self.add(self.electrons)   # 着席した電子はこのグループへ移し替える

        # --- ① マス目 (席) を描く ---
        grid, frame = self._make_grid()
        momentum_axis = self._make_momentum_axis()
        self.show_caption("電子の席は、マス目で区切られている",
                          "Electron seats form a grid of cells")
        self.play(Create(frame), Create(grid), run_time=1.4)
        self.play(FadeIn(momentum_axis, shift=UP * 0.2), run_time=0.8)

        # スピンの凡例 (色違い = スピンの向き違い)
        legend = self._make_legend()
        self.play(FadeIn(legend), run_time=0.6)
        self.wait(0.4)

        # --- ② 1マス2個まで。3個目は弾かれる ---
        self._part_two_per_cell()

        # --- ③④ 下の席から順に埋まり、あふれた電子は速い席へ ---
        self._part_seat_filling()

        # 全員着席 → 揺れ (運動) を開始。上の段ほど激しい
        self._start_jitter()
        self._part_fast_seats()

        # --- ⑤ 絶対零度でも止まらない ---
        self._part_absolute_zero()

        # --- ⑥ 電子縮退圧 ---
        self._part_degeneracy_pressure(frame)

        self.electrons.remove_updater(self._jitter)
        self.wait(0.5)

    # ------------------------------------------------------------------
    # 部品づくり
    # ------------------------------------------------------------------
    def _make_grid(self) -> tuple[VGroup, Rectangle]:
        """マス目の格子線と外枠を作る。"""
        origin = grid_origin()
        grid = VGroup()
        for i in range(1, N_COLS):
            x = origin[0] + i * CELL_W
            grid.add(Line([x, origin[1], 0], [x, origin[1] + N_ROWS * CELL_H, 0],
                          stroke_width=1.2, color=GRID_COLOR))
        for j in range(1, N_ROWS):
            y = origin[1] + j * CELL_H
            grid.add(Line([origin[0], y, 0], [origin[0] + N_COLS * CELL_W, y, 0],
                          stroke_width=1.2, color=GRID_COLOR))

        frame = Rectangle(width=N_COLS * CELL_W, height=N_ROWS * CELL_H)
        frame.set_stroke(FRAME_COLOR, width=2.5).set_fill(opacity=0)
        frame.move_to(GRID_CENTER)
        return grid, frame

    def _make_momentum_axis(self) -> VGroup:
        """マス目の左に置く「運動量 (速さ)」の上向き矢印を作る。"""
        origin = grid_origin()
        x = origin[0] - 0.55
        arrow = Arrow(
            start=[x, origin[1], 0],
            end=[x, origin[1] + N_ROWS * CELL_H, 0],
            buff=0, color=GRAY_C, stroke_width=3,
            tip_length=0.2, max_tip_length_to_length_ratio=0.2,
        )
        label = Text("速い席\nfast", font_size=18, color=GRAY_C, line_spacing=0.8)
        label.next_to(arrow.get_end(), LEFT, buff=0.15)
        label2 = Text("おとなしい席\ncalm", font_size=18, color=GRAY_C,
                      line_spacing=0.8)
        label2.next_to(arrow.get_start(), LEFT, buff=0.15)
        return VGroup(arrow, label, label2)

    def _make_legend(self) -> VGroup:
        """スピンの向き = 色の凡例を作る。"""
        up_dot = make_electron(-1)
        down_dot = make_electron(+1)
        text = Text("色の違い＝スピンの向き / spin", font_size=18, color=GRAY_B)
        legend = VGroup(up_dot, down_dot, text).arrange(RIGHT, buff=0.18)
        legend.to_corner(UR, buff=0.4)
        return legend

    # ------------------------------------------------------------------
    # 各パート
    # ------------------------------------------------------------------
    def _part_two_per_cell(self):
        """1マス2個まで・3個目は隣へ、を最下段の左端マスで見せる。"""
        self.show_caption("1つのマスに入れる電子は、2個まで",
                          "Each cell holds at most two electrons")

        entry = grid_origin() + np.array([-2.2, 0.5 * CELL_H, 0.0])

        # 1個目・2個目: すんなり着席
        for side in (-1, +1):
            e = make_electron(side).move_to(entry)
            self.play(FadeIn(e, scale=0.5), run_time=0.3)
            self.play(e.animate.move_to(seat_pos(0, 0, side)), run_time=0.7)
            self._register(e, row=0)

        # 「満員」の強調
        full_rect = Rectangle(width=CELL_W, height=CELL_H)
        full_rect.set_stroke(FULL_COLOR, width=3).set_fill(opacity=0)
        full_rect.move_to(cell_center(0, 0))
        full_label = Text("満員 / full", font_size=20, color=FULL_COLOR, weight=BOLD)
        full_label.next_to(full_rect, UP, buff=0.1)
        self.play(Create(full_rect), FadeIn(full_label), run_time=0.6)
        self.wait(0.4)

        # 3個目: 入ろうとして弾かれ、隣のマスへ
        self.show_caption("3個目は弾かれて、隣のマスへ",
                          "A third one is rejected — it must take another cell")
        e3 = make_electron(-1).move_to(entry)
        self.play(FadeIn(e3, scale=0.5), run_time=0.3)
        self.play(e3.animate.move_to(cell_center(0, 0) + LEFT * 0.15), run_time=0.6)
        self.play(
            Flash(cell_center(0, 0), color=FULL_COLOR, flash_radius=0.5),
            e3.animate(path_arc=-PI / 2).move_to(seat_pos(1, 0, -1)),
            run_time=0.8,
        )
        self._register(e3, row=0)
        self.play(FadeOut(full_rect), FadeOut(full_label), run_time=0.5)
        self.wait(0.3)

    def _part_seat_filling(self):
        """残りの席を下の段から順に埋めていく。"""
        self.show_caption("おとなしい席から、順に埋まっていく",
                          "Calm low-momentum seats fill up first")
        self._fill_rows([0, 1])

        self.show_caption("後から来た電子は『速い席』しか残っていない",
                          "Latecomers are forced into the fast seats")
        self._fill_rows([2, 3])
        self.wait(0.3)

    def _fill_rows(self, rows: list[int]):
        """指定した段の空席をすべて埋める。"""
        for row in rows:
            anims = []
            newcomers = []
            for col in range(N_COLS):
                for side in (-1, +1):
                    target = seat_pos(col, row, side)
                    # すでに着席済みの席はスキップ (パート②の3個)
                    if any(np.allclose(target, h) for h in self.homes):
                        continue
                    start = grid_origin() + np.array(
                        [-2.2, (row + 0.5) * CELL_H, 0.0]
                    )
                    e = make_electron(side).move_to(start)
                    newcomers.append((e, target, row))
                    anims.append(Succession(
                        FadeIn(e, scale=0.5, run_time=0.2),
                        e.animate(run_time=0.7).move_to(target),
                    ))
            self.play(LaggedStart(*anims, lag_ratio=0.12), run_time=1.8)
            for e, target, r in newcomers:
                e.move_to(target)
                self._register(e, row=r)

    def _part_fast_seats(self):
        """上の段の電子ほど激しく動いていることを強調する。"""
        self.show_caption("詰め込むほど、速く動く電子が必ず現れる",
                          "Packing them in creates fast-moving electrons")
        top_zone = Rectangle(width=N_COLS * CELL_W + 0.2, height=CELL_H + 0.2)
        top_zone.set_stroke(FULL_COLOR, width=2.5).set_fill(opacity=0)
        top_zone.move_to(cell_center(0, N_ROWS - 1)
                         + RIGHT * (N_COLS - 1) * CELL_W / 2)
        self.play(Create(top_zone), run_time=0.8)
        self.wait(2.2)
        self.play(FadeOut(top_zone), run_time=0.5)

    def _part_absolute_zero(self):
        """温度計を絶対零度まで下げても電子が止まらないことを見せる。"""
        self.show_caption("絶対零度まで冷やしても、電子は止まらない",
                          "Even at absolute zero, they keep moving")

        thermo, temp = self._make_thermometer()
        self.play(FadeIn(thermo, shift=RIGHT * 0.3), run_time=0.8)
        self.play(temp.animate.set_value(-273.0), run_time=3.0,
                  rate_func=rate_functions.ease_in_out_sine)
        self.wait(1.8)
        self.thermo = thermo

    def _make_thermometer(self) -> tuple[VGroup, ValueTracker]:
        """左端に置く温度計と、温度のトラッカーを作る。"""
        temp = ValueTracker(20.0)
        x0 = -5.9
        tube_h = 2.4
        tube = RoundedRectangle(width=0.34, height=tube_h, corner_radius=0.15)
        tube.set_stroke(GRAY_B, width=2).set_fill(BLACK, opacity=0.3)
        tube.move_to([x0, 0.9, 0])
        bulb = Circle(radius=0.26).set_stroke(GRAY_B, width=2)
        bulb.set_fill(THERMO_COLOR, opacity=1.0)
        bulb.move_to([x0, 0.9 - tube_h / 2 - 0.12, 0])

        def liquid():
            # 20℃ で満タン、-273℃ でほぼ空になる液柱
            frac = (temp.get_value() + 273.0) / 293.0
            h = max(frac * (tube_h - 0.2), 0.06)
            rect = Rectangle(width=0.18, height=h)
            rect.set_stroke(width=0).set_fill(THERMO_COLOR, opacity=1.0)
            bottom_y = bulb.get_center()[1]
            rect.move_to([x0, bottom_y + h / 2, 0])
            return rect

        column = always_redraw(liquid)

        value = Integer(20)
        value.add_updater(lambda m: m.set_value(temp.get_value()))
        unit = Text("°C", font_size=22, color=WHITE)
        readout = VGroup(value, unit).arrange(RIGHT, buff=0.08)
        readout.next_to(tube, UP, buff=0.25)
        value.add_updater(lambda m: m.next_to(unit, LEFT, buff=0.08))

        label = Text("温度 / temp.", font_size=18, color=GRAY_B)
        label.next_to(bulb, DOWN, buff=0.2)

        return VGroup(column, tube, bulb, readout, label), temp

    def _part_degeneracy_pressure(self, frame: Rectangle):
        """電子の運動が外向きの圧力を生むことを見せる。"""
        self.show_caption("この運動が圧力を生む ― 電子縮退圧",
                          "This motion creates pressure — electron degeneracy pressure")

        center = frame.get_center()
        half_w = frame.width / 2
        half_h = frame.height / 2
        arrows = VGroup()
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            d = np.array([dx, dy, 0.0], dtype=float)
            d /= np.linalg.norm(d)
            start = center + np.array([dx * half_w, dy * half_h, 0.0]) * 0.98
            end = start + d * 0.65
            arrows.add(Arrow(start=start, end=end, buff=0,
                             color=PRESSURE_COLOR, stroke_width=5,
                             tip_length=0.18,
                             max_stroke_width_to_length_ratio=25,
                             max_tip_length_to_length_ratio=0.5))
        self.play(LaggedStart(*[GrowArrow(a) for a in arrows], lag_ratio=0.06),
                  run_time=1.2)
        self.play(Indicate(frame, color=PRESSURE_COLOR, scale_factor=1.02),
                  run_time=1.0)
        self.wait(1.8)

    # ------------------------------------------------------------------
    # 揺れ (運動) の処理
    # ------------------------------------------------------------------
    def _register(self, electron: Dot, row: int):
        """着席した電子を揺れ対象として登録する。"""
        self.remove(electron)  # トップレベルから外し、グループ経由で描画する
        self.electrons.add(electron)
        self.homes.append(electron.get_center().copy())
        self.rows_of.append(row)

    def _start_jitter(self):
        """全電子の揺れを開始する。上の段ほど速く・大きく揺れる。"""
        self._rng = np.random.default_rng(11)
        self._jitter_pos = [d.get_center().copy() for d in self.electrons]
        self.electrons.add_updater(self._jitter)

    def _jitter(self, group: VGroup, dt: float):
        """毎フレーム、各電子を席のまわりでランダムに揺らす。

        Args:
            group: 着席済みの電子をまとめた VGroup。
            dt: 前フレームからの経過時間 [sec]。
        """
        for i, dot in enumerate(group):
            row = self.rows_of[i]
            amp = JITTER_BASE + JITTER_PER_ROW * row
            rate = JITTER_RATE_BASE + JITTER_RATE_PER_ROW * row
            target = self.homes[i] + np.array([
                self._rng.uniform(-1, 1) * amp * 2.0,
                self._rng.uniform(-1, 1) * amp * 1.6,
                0.0,
            ])
            self._jitter_pos[i] += (target - self._jitter_pos[i]) * min(dt * rate, 1.0)
            dot.move_to(self._jitter_pos[i])

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
