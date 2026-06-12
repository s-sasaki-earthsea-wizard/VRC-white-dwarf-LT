"""冷えてしぼむ風船と「潰れない白色矮星」の謎のアニメーション。

熱で支えられる星の理屈をそのまま当てはめると、燃え尽きた星は風船の
ように冷えてしぼみ、重力でぺしゃんこに潰れてしまうはず。ところが
実際の白色矮星は潰れない――「？」の力が押し返している、という
謎の提示までを 1 カットで見せる。

yt_script.md の「3. 素朴な疑問 ―― 燃え尽きた星はなぜ潰れない？」に対応。

構成:
    ① 風船の中で分子が飛び回っている (温かい)
    ② 温度計が下がる → 分子がおとなしくなり、風船がしぼむ
    ③ 同じ理屈なら、燃え尽きた星は潰れて点になるはず → 「？」
    ④ でも実際の白色矮星は丸いまま。重力に対して未知の力「？」が押し返す

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/cooling_collapse.py CoolingCollapse   # 低画質プレビュー
    manim -pqh manim-scripts/cooling_collapse.py CoolingCollapse   # 高画質
"""

import numpy as np
from manim import *

# 配色 (balloon_pressure.py / hydrostatic_balance.py の色味に準拠)
BALLOON_FILL = "#F7C6B8"     # 風船のゴム膜 (薄いオレンジ)
BALLOON_STROKE = "#E0573C"   # 風船の輪郭
MOLECULE_COLOR = "#2F6FE0"   # 気体分子
STAR_COLOR = "#EF9F27"       # 燃え尽きる前の星 (オレンジ)
STAR_RIM = "#BA7517"
WD_CORE = "#EAF2FF"          # 白色矮星 (白〜淡青)
WD_RIM = "#9FB8D8"
GRAVITY_COLOR = "#2F80ED"    # 重力 (青)
MYSTERY_COLOR = "#C9A227"    # 未知の力「？」 (金)
THERMO_COLOR = "#D14B3A"     # 温度計の液柱 (赤)

CENTER = np.array([0.0, 0.55, 0.0])  # 風船・星の中心
R_WARM = 1.7                 # 温かい風船の半径
R_COLD = 1.05                # 冷えた風船の半径
N_MOLECULES = 10             # 分子の数


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。"""
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


def make_glow_ball(radius: float, color: str, rim_color: str,
                   center: np.ndarray) -> VGroup:
    """中心ほど明るいグローを重ねた星の球体を作る。"""
    group = VGroup()
    for scale, opacity in [(1.0, 0.12), (0.72, 0.18), (0.45, 0.30)]:
        layer = Circle(radius=radius * scale)
        layer.set_fill(color, opacity=opacity).set_stroke(width=0)
        layer.move_to(center)
        group.add(layer)
    rim = Circle(radius=radius).set_stroke(rim_color, width=2, opacity=0.9)
    rim.set_fill(opacity=0).move_to(center)
    group.add(rim)
    return group


class CoolingCollapse(Scene):
    """風船の冷却 → 星の崩壊 (のはず) → 潰れない白色矮星、を見せるシーン。"""

    def construct(self):
        self.caption = None
        self.radius = ValueTracker(R_WARM)   # 風船の半径
        self.speed = ValueTracker(1.0)       # 分子の運動の激しさ

        # --- ① 温かい風船と飛び回る分子 ---
        balloon = always_redraw(self._make_balloon)
        self.show_caption("温かい風船：分子が飛び回って支えている",
                          "A warm balloon: flying molecules hold it up")
        self.play(FadeIn(balloon, scale=0.9), run_time=1.0)

        self._setup_molecules()
        self.add(self.molecules)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in self.molecules],
                              lag_ratio=0.06), run_time=0.9)
        self.molecules.add_updater(self._step)
        self.wait(1.6)

        # --- ② 冷やす → 分子がおとなしくなり、しぼむ ---
        self.show_caption("冷えると分子はおとなしくなり、しぼんでいく",
                          "Cooling calms the molecules — the balloon deflates")
        thermo, temp = self._make_thermometer()
        self.play(FadeIn(thermo, shift=RIGHT * 0.3), run_time=0.7)
        self.play(
            temp.animate.set_value(-40.0),
            self.speed.animate.set_value(0.22),
            self.radius.animate.set_value(R_COLD),
            run_time=3.0,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(1.0)

        # --- ③ 星なら潰れて点になるはず → 「？」 ---
        self.show_caption("燃え尽きた星も、同じように潰れてしまうはず…？",
                          "Shouldn't a burnt-out star collapse the same way?")
        self.molecules.remove_updater(self._step)
        # always_redraw の更新を止めてからフェードアウトする
        balloon.clear_updaters()
        for sub in thermo:
            sub.clear_updaters()
        star = make_glow_ball(R_COLD, STAR_COLOR, STAR_RIM, CENTER)
        self.play(
            FadeOut(self.molecules),
            FadeOut(thermo),
            FadeOut(balloon),
            FadeIn(star),
            run_time=1.2,
        )

        gravity_arrows = self._make_radial_arrows(
            R_COLD + 0.85, R_COLD + 0.25, GRAVITY_COLOR)
        self.play(LaggedStart(*[GrowArrow(a) for a in gravity_arrows],
                              lag_ratio=0.06), run_time=1.0)

        # 重力に負けて点まで潰れる
        collapsed = make_glow_ball(0.07, STAR_COLOR, STAR_RIM, CENTER)
        self.play(
            Transform(star, collapsed),
            *[a.animate.shift((CENTER - a.get_end()) * 0.55)
              for a in gravity_arrows],
            run_time=1.8,
            rate_func=rate_functions.ease_in_quad,
        )
        question = Text("？", font_size=110, color=MYSTERY_COLOR, weight=BOLD)
        question.move_to(CENTER + UP * 0.1)
        self.play(FadeIn(question, scale=1.4), FadeOut(gravity_arrows),
                  run_time=0.9)
        self.wait(1.6)

        # --- ④ でも白色矮星は潰れない: 「？」の力が押し返す ---
        self.show_caption("ところが白色矮星は、潰れずに丸いまま",
                          "Yet the real white dwarf stays round")
        wd = make_glow_ball(1.15, WD_CORE, WD_RIM, CENTER)
        self.play(FadeOut(question), FadeOut(star), FadeIn(wd, scale=0.6),
                  run_time=1.2)

        gravity_arrows2 = self._make_radial_arrows(
            1.15 + 0.95, 1.15 + 0.35, GRAVITY_COLOR)
        self.play(LaggedStart(*[GrowArrow(a) for a in gravity_arrows2],
                              lag_ratio=0.06), run_time=1.0)
        self.wait(0.4)

        self.show_caption("熱ではない『何か』が、重力を押し返している",
                          "Something other than heat is pushing gravity back")
        mystery_arrows = self._make_radial_arrows(
            1.15 + 0.35, 1.15 + 0.95, MYSTERY_COLOR, angle_offset=PI / 8)
        q_marks = VGroup()
        for arrow in mystery_arrows:
            q = Text("？", font_size=26, color=MYSTERY_COLOR, weight=BOLD)
            q.move_to(arrow.get_end() + (arrow.get_end() - arrow.get_start()) * 0.4)
            q_marks.add(q)
        self.play(
            LaggedStart(*[GrowArrow(a) for a in mystery_arrows], lag_ratio=0.06),
            run_time=1.1,
        )
        self.play(FadeIn(q_marks), run_time=0.7)
        self.play(Indicate(wd, color=MYSTERY_COLOR, scale_factor=1.04),
                  run_time=1.0)
        self.wait(2.0)

    # ------------------------------------------------------------------
    # 風船と分子
    # ------------------------------------------------------------------
    def _make_balloon(self) -> VGroup:
        """半径トラッカーに追従する風船を作る (always_redraw 用)。"""
        r = self.radius.get_value()
        body = Circle(radius=r)
        body.set_fill(BALLOON_FILL, opacity=0.85)
        body.set_stroke(BALLOON_STROKE, width=3)
        body.stretch(1.06, dim=1)
        body.move_to(CENTER)

        knot_y = CENTER[1] - r * 1.06
        knot = Triangle().scale(0.12)
        knot.set_fill(BALLOON_STROKE, opacity=1.0).set_stroke(width=0)
        knot.move_to([CENTER[0], knot_y, 0.0])
        return VGroup(body, knot)

    def _setup_molecules(self):
        """風船内の分子の初期位置と速度を設定する。"""
        rng = np.random.default_rng(13)
        self._rng = rng
        self.molecules = VGroup()
        self._pos = []
        self._vel = []
        for _ in range(N_MOLECULES):
            ang = rng.uniform(0, TAU)
            rad = (R_WARM - 0.3) * np.sqrt(rng.uniform())
            pos = CENTER + np.array([np.cos(ang) * rad, np.sin(ang) * rad, 0.0])
            self._pos.append(pos.copy())
            vang = rng.uniform(0, TAU)
            self._vel.append(
                np.array([np.cos(vang), np.sin(vang), 0.0])
                * 1.8 * rng.uniform(0.8, 1.2)
            )
            dot = Dot(radius=0.085, color=MOLECULE_COLOR).set_stroke(WHITE, width=1)
            dot.move_to(pos)
            self.molecules.add(dot)

    def _step(self, mob: VGroup, dt: float):
        """分子の等速運動と風船の壁での反射を処理する。"""
        dt = min(dt, 1.0 / 30.0)
        r_wall = self.radius.get_value() - 0.12
        speed = self.speed.get_value()
        for i, dot in enumerate(mob):
            pos = self._pos[i] + self._vel[i] * speed * dt
            offset = pos - CENTER
            dist = np.linalg.norm(offset)
            if dist > r_wall and dist > 1e-6:
                normal = offset / dist
                vn = float(np.dot(self._vel[i], normal))
                if vn > 0:
                    self._vel[i] = self._vel[i] - 2 * vn * normal
                pos = CENTER + normal * r_wall
            self._pos[i] = pos
            dot.move_to(pos)

    def _make_thermometer(self) -> tuple[VGroup, ValueTracker]:
        """画面左に置く温度計と温度トラッカーを作る。"""
        temp = ValueTracker(30.0)
        x0 = -5.4
        tube_h = 2.2
        tube = RoundedRectangle(width=0.32, height=tube_h, corner_radius=0.14)
        tube.set_stroke(GRAY_B, width=2).set_fill(BLACK, opacity=0.3)
        tube.move_to([x0, 0.85, 0])
        bulb = Circle(radius=0.24).set_stroke(GRAY_B, width=2)
        bulb.set_fill(THERMO_COLOR, opacity=1.0)
        bulb.move_to([x0, 0.85 - tube_h / 2 - 0.1, 0])

        def liquid():
            # 30℃ で満タン、-50℃ でほぼ空の液柱
            frac = np.clip((temp.get_value() + 50.0) / 80.0, 0.02, 1.0)
            h = max(frac * (tube_h - 0.2), 0.06)
            rect = Rectangle(width=0.16, height=h)
            rect.set_stroke(width=0).set_fill(THERMO_COLOR, opacity=1.0)
            rect.move_to([x0, bulb.get_center()[1] + h / 2, 0])
            return rect

        column = always_redraw(liquid)
        label = Text("冷やす / cooling", font_size=18, color=GRAY_B)
        label.next_to(bulb, DOWN, buff=0.2)
        return VGroup(column, tube, bulb, label), temp

    # ------------------------------------------------------------------
    # 矢印
    # ------------------------------------------------------------------
    def _make_radial_arrows(self, r_from: float, r_to: float, color: str,
                            angle_offset: float = 0.0) -> VGroup:
        """中心に対して放射状の力の矢印を 8 本作る。

        向きは r_from と r_to の大小で決まる (r_from > r_to なら内向き)。

        Args:
            r_from: 矢印の始点の中心からの距離。
            r_to: 矢印の終点の中心からの距離。
            color: 矢印の色。
            angle_offset: 配置角のずらし (内向き矢印と交互に並べる用)。

        Returns:
            8 本の矢印をまとめた VGroup。
        """
        arrows = VGroup()
        for ang in np.linspace(0, TAU, 8, endpoint=False) + angle_offset:
            d = np.array([np.cos(ang), np.sin(ang), 0.0])
            arrows.add(Arrow(
                start=CENTER + d * r_from,
                end=CENTER + d * r_to,
                buff=0, color=color, stroke_width=5,
                tip_length=0.18,
                max_stroke_width_to_length_ratio=25,
                max_tip_length_to_length_ratio=0.5,
            ))
        return arrows

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
