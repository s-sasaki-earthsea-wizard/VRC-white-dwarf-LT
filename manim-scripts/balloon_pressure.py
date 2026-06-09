"""風船と気体分子の運動による圧力のアニメーション。

普通の星が潰れない理由である「熱からの圧力」を、身近な風船で説明するための
イメージ映像。気体の圧力が「分子の運動」から生まれること――つまり分子が
激しく飛び回って壁を叩くほど圧力が高まり、風船が膨らむ様子を可視化する。

slides-jp/yt_script.md の「2. そもそも、星はなぜ潰れないのか」の
> 熱いと分子が激しく飛び回って、壁をどんどん叩く。これが圧力。
に対応するカット。

構成:
    ① 風船の中で気体分子が飛び回り、壁で跳ね返る
    ② 壁への衝突点に閃光を出し「壁を叩く力＝圧力」を見せる
    ③ 運動を激しくする(加熱)と衝突が増え、風船が膨らむ

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/balloon_pressure.py BalloonPressure   # 低画質プレビュー
    manim -pqh manim-scripts/balloon_pressure.py BalloonPressure   # 高画質
"""

import numpy as np
from manim import *

# 配色 (warm 系の風船 × 寒色の分子でコントラストを付ける)
BALLOON_FILL = "#F7C6B8"    # 風船のゴム膜 (薄いオレンジ)
BALLOON_STROKE = "#E0573C"  # 風船の輪郭
MOLECULE_COLOR = "#2F6FE0"  # 気体分子
IMPACT_COLOR = "#FFC233"    # 壁を叩いた瞬間の閃光 (= 圧力)

BALLOON_CENTER = UP * 0.45  # 風船の中心 (下部キャプションの余白を確保)
RADIUS_CALM = 1.55          # 初期 (おとなしい) 状態の半径
RADIUS_HOT = 2.35           # 加熱して膨らんだ状態の半径

MOL_RADIUS = 0.085          # 分子マーカーの半径
N_MOLECULES = 14            # 分子の個数
BASE_SPEED = 1.9            # 速さ係数 1.0 のときの基準速度 [units/sec]

FLASH_LIFE = 0.32           # 衝突閃光の寿命 [sec]
MAX_FLASHES = 20            # 同時に出す閃光の上限 (描画負荷の抑制)


def make_balloon(radius_tracker: ValueTracker) -> VMobject:
    """半径トラッカーに追従して膨らむ風船を作る (always_redraw 用)。

    Args:
        radius_tracker: 風船の半径 [units] を保持する ValueTracker。

    Returns:
        ゴム膜・結び目・ひもをまとめた VGroup。
    """
    r = radius_tracker.get_value()
    center = BALLOON_CENTER

    # ゴム膜本体 (上をわずかに尖らせるため縦に少し伸ばす)
    body = Circle(radius=r)
    body.set_fill(BALLOON_FILL, opacity=0.85)
    body.set_stroke(BALLOON_STROKE, width=3)
    body.stretch(1.06, dim=1)  # 縦長にして風船らしいシルエットに
    body.move_to(center)

    # ハイライト (左上の光沢)
    gloss = Arc(radius=r * 0.62, start_angle=PI * 0.55, angle=PI * 0.45)
    gloss.set_stroke(WHITE, width=3, opacity=0.5)
    gloss.move_to(center + np.array([-r * 0.22, r * 0.28, 0.0]))

    # 結び目 (風船の口)
    knot_y = center[1] - r * 1.06
    knot = Triangle().scale(0.12)
    knot.set_fill(BALLOON_STROKE, opacity=1.0).set_stroke(width=0)
    knot.move_to(np.array([center[0], knot_y, 0.0]))

    # ひも
    string = Line(
        np.array([center[0], knot_y - 0.05, 0.0]),
        np.array([center[0] + 0.18, knot_y - 0.7, 0.0]),
        stroke_width=2,
        color=BALLOON_STROKE,
    )

    return VGroup(body, gloss, knot, string)


def make_molecule() -> Dot:
    """気体分子 1 個のマーカーを作る。"""
    return Dot(radius=MOL_RADIUS, color=MOLECULE_COLOR).set_stroke(WHITE, width=1)


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。"""
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


class BalloonPressure(Scene):
    """気体分子の運動 → 圧力 → 風船が膨らむ、を見せるシーン。"""

    def construct(self):
        self.caption = None

        # 風船の半径と「運動の激しさ(温度)」を駆動するトラッカー
        self.radius = ValueTracker(RADIUS_CALM)
        self.speed = ValueTracker(1.0)

        # --- 風船 (半径トラッカーに追従) ---
        balloon = always_redraw(lambda: make_balloon(self.radius))
        self.play(FadeIn(balloon, scale=0.85), run_time=1.0)

        # --- 分子の初期配置と速度 ---
        rng = np.random.default_rng(7)
        self.positions = []
        self.velocities = []
        mols = VGroup()
        for _ in range(N_MOLECULES):
            # 壁の内側に面積一様でばらつかせて配置する
            ang = rng.uniform(0, TAU)
            rad = (RADIUS_CALM - 0.3) * np.sqrt(rng.uniform())
            pos = BALLOON_CENTER + np.array([np.cos(ang) * rad, np.sin(ang) * rad, 0.0])
            self.positions.append(pos)

            # 向きはランダム、速さは基準の 0.8〜1.2 倍でばらつかせる
            vang = rng.uniform(0, TAU)
            vmag = BASE_SPEED * rng.uniform(0.8, 1.2)
            self.velocities.append(np.array([np.cos(vang), np.sin(vang), 0.0]) * vmag)

            dot = make_molecule().move_to(pos)
            mols.add(dot)

        self.flashes = VGroup()  # 衝突閃光を入れておくグループ
        self.add(self.flashes)

        self.show_caption("気体分子が飛び回っている", "Gas molecules fly around inside")
        self.play(LaggedStart(*[GrowFromCenter(d) for d in mols], lag_ratio=0.05), run_time=1.0)

        # 物理更新の updater を取り付け、分子を動かし始める
        # (VGroup 自体をシーンに登録しないとグループ更新子が呼ばれない)
        self.add(mols)
        mols.add_updater(self._step)
        self.wait(2.4)

        # --- ② 壁を叩く力 = 圧力 ---
        self.show_caption("壁を叩く力が圧力になる", "Molecules striking the wall create pressure")
        self.wait(2.6)

        # --- ③ 激しく動くほど圧力が強まり、膨らむ ---
        self.show_caption(
            "激しく動くほど圧力が強まり、膨らむ",
            "Faster motion → higher pressure → the balloon expands",
        )
        # 「加熱」: 運動を速くしつつ風船を膨らませる (updater が両トラッカーを毎フレーム参照)
        self.play(
            self.speed.animate.set_value(3.7),
            self.radius.animate.set_value(RADIUS_HOT),
            run_time=3.0,
            rate_func=rate_functions.ease_in_out_sine,
        )
        self.wait(2.6)

        mols.remove_updater(self._step)
        self.wait(0.5)

    # ------------------------------------------------------------------
    # 物理更新
    # ------------------------------------------------------------------
    def _step(self, mob: VGroup, dt: float):
        """毎フレーム呼ばれ、分子の等速運動と円壁での反射を処理する。

        Args:
            mob: 分子マーカーをまとめた VGroup (各 Dot が 1 分子に対応)。
            dt: 前フレームからの経過時間 [sec]。
        """
        dt = min(dt, 1.0 / 30.0)  # 大きなフレーム飛びでのすり抜けを防ぐ
        center = BALLOON_CENTER
        r_wall = self.radius.get_value() - MOL_RADIUS
        speed = self.speed.get_value()

        for i, dot in enumerate(mob):
            pos = self.positions[i] + self.velocities[i] * speed * dt

            # 中心からの距離で壁との衝突を判定
            offset = pos - center
            dist = np.linalg.norm(offset)
            if dist > r_wall and dist > 1e-6:
                normal = offset / dist
                vn = float(np.dot(self.velocities[i], normal))
                if vn > 0:  # 外向きに進んでいるときだけ反射
                    self.velocities[i] = self.velocities[i] - 2 * vn * normal
                pos = center + normal * r_wall  # 壁の内側へ押し戻す
                # 閃光は壁のわずか内側に出し、はみ出して見えないようにする
                self._spawn_flash(center + normal * (r_wall - 0.06))

            self.positions[i] = pos
            dot.move_to(pos)

        self._age_flashes(dt)

    def _spawn_flash(self, point: np.ndarray):
        """衝突点に圧力を表す閃光を発生させる。"""
        if len(self.flashes) >= MAX_FLASHES:
            return
        flash = Dot(point, radius=0.1, color=IMPACT_COLOR)
        flash.set_stroke(WHITE, width=1, opacity=0.8)
        flash.age = 0.0
        self.flashes.add(flash)

    def _age_flashes(self, dt: float):
        """閃光を寿命に応じて拡大・減衰させ、寿命切れを除去する。"""
        for flash in list(self.flashes):
            flash.age += dt
            progress = flash.age / FLASH_LIFE
            if progress >= 1.0:
                self.flashes.remove(flash)
            else:
                flash.set_opacity((1.0 - progress) * 0.9)
                flash.scale(1.0 + dt * 1.2)

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
