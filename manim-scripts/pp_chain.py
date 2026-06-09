"""陽子-陽子連鎖反応 (pp-chain) のアニメーション。

太陽の中心で起こる「水素 → ヘリウム」の核融合プロセスを可視化する。
反応式の羅列ではなく、陽子 (p) と中性子 (n) のマーカーが実際に動いて
融合し、陽電子 (e⁺)・ニュートリノ (ν)・ガンマ線 (γ) が飛び出す様子を見せる。

最終段 ³He + ³He → ⁴He + 2¹H は ³He が 2 個必要なため、
上下 2 本の反応経路を並行に進め、最後に中央で合流させる構成とした。
正味の収支「6 ¹H → ⁴He + 2 ¹H」が画面内で閉じて見えるようにしている。

レンダリング例:
    manim -pql manim-scripts/pp_chain.py ProtonProtonChain   # 低画質プレビュー
    manim -pqh manim-scripts/pp_chain.py ProtonProtonChain   # 高画質
"""

from manim import *

# 粒子ごとの色定義
PROTON_COLOR = RED_D       # 陽子
NEUTRON_COLOR = GRAY_B     # 中性子
POSITRON_COLOR = ORANGE    # 陽電子 e⁺
NEUTRINO_COLOR = TEAL_B    # ニュートリノ ν
GAMMA_COLOR = YELLOW_B     # ガンマ線 γ

NUCLEON_RADIUS = 0.18


def make_nucleon(kind: str) -> VGroup:
    """陽子または中性子 1 個を表すマーカーを作る。

    Args:
        kind: "p"(陽子) または "n"(中性子)。

    Returns:
        円と記号をまとめた VGroup。
    """
    color = PROTON_COLOR if kind == "p" else NEUTRON_COLOR
    body = Circle(radius=NUCLEON_RADIUS, stroke_color=WHITE, stroke_width=1.5)
    body.set_fill(color, opacity=1.0)
    label = Text(kind, font_size=18, color=WHITE, weight=BOLD).move_to(body)
    return VGroup(body, label)


def make_nucleus(kinds: list[str]) -> VGroup:
    """核子の組み合わせから原子核クラスタを作る。

    Args:
        kinds: 核子種のリスト。例: ["p", "n"] は重水素 ²H。

    Returns:
        核子をまとまりよく配置した VGroup。
    """
    offsets = {
        1: [ORIGIN],
        2: [LEFT * 0.19, RIGHT * 0.19],
        3: [UP * 0.21, DOWN * 0.19 + LEFT * 0.21, DOWN * 0.19 + RIGHT * 0.21],
        4: [UL * 0.21, UR * 0.21, DL * 0.21, DR * 0.21],
    }[len(kinds)]
    group = VGroup()
    for kind, off in zip(kinds, offsets):
        group.add(make_nucleon(kind).move_to(off))
    return group


def make_label(text: str, color=WHITE) -> Text:
    """原子核や放出粒子に添える短いラベルを作る。"""
    return Text(text, font_size=22, color=color, weight=BOLD)


def make_caption(jp: str, en: str) -> VGroup:
    """画面下部の日英併記テロップ (上段=日本語, 下段=英語) を作る。

    Args:
        jp: 日本語の説明文 (上段・白)。
        en: 英語の説明文 (下段・グレー)。

    Returns:
        2 行を縦に並べ、画面下端に配置した VGroup。
    """
    jp_line = Text(jp, font_size=22, color=WHITE, weight=BOLD)
    en_line = Text(en, font_size=18, color=GRAY_B)
    group = VGroup(jp_line, en_line).arrange(DOWN, buff=0.12)
    group.to_edge(DOWN, buff=0.35)
    return group


class Branch:
    """1 本の反応経路 (¹H+¹H+¹H → ³He) が持つ mobject 群を管理する。

    Attributes:
        oy: この経路の基準 y 座標。
        sign: 放出粒子を飛ばす向き (+1 で上, -1 で下)。
    """

    def __init__(self, oy: float, sign: int):
        self.oy = oy
        self.sign = sign
        # 初期状態: 陽子 3 個を左側に配置
        self.p1 = make_nucleon("p").move_to([-6.3, oy, 0])
        self.p2 = make_nucleon("p").move_to([-5.1, oy, 0])
        self.p3 = make_nucleon("p").move_to([-6.9, oy + sign * 0.95, 0])
        self.deuteron = None   # ²H
        self.helium3 = None     # ³He
        self.nucleus_label = None

    @property
    def fuse_a(self):
        """第 1 段 (p+p) の融合点。"""
        return [-5.2, self.oy, 0]

    @property
    def fuse_b(self):
        """第 2 段 (²H+p) の融合点。"""
        return [-3.4, self.oy, 0]


class ProtonProtonChain(Scene):
    """陽子-陽子連鎖反応を 2 経路並行で見せるシーン。"""

    def construct(self):
        # タイトルは後工程 (FCP) で挿入するため、ここでは描かない。
        # 画面下の日英併記テロップ
        caption = make_caption(
            "太陽の中心: 水素が核融合してヘリウムになる",
            "In the Sun's core: hydrogen fuses into helium",
        )
        self.play(FadeIn(caption))

        # --- 2 本の反応経路を用意 (上・下) ---
        branches = [Branch(oy=1.9, sign=+1), Branch(oy=-1.9, sign=-1)]
        intro = []
        for b in branches:
            intro += [FadeIn(b.p1), FadeIn(b.p2), FadeIn(b.p3)]
        self.play(*intro, run_time=0.8)
        self.wait(0.4)

        # --- 第 1 段: ¹H + ¹H → ²H + e⁺ + ν (両経路同時) ---
        self._update_caption(
            caption,
            "① 2つの陽子が融合 → 重水素 + 陽電子 + ニュートリノ",
            "Two protons fuse → deuterium + e⁺ + ν",
        )
        self._step_pp_to_deuteron(branches)

        # --- 第 2 段: ²H + ¹H → ³He + γ (両経路同時) ---
        self._update_caption(
            caption,
            "② 重水素 + 陽子 → ³He + ガンマ線",
            "Deuterium + proton → ³He + γ",
        )
        self._step_deuteron_to_he3(branches)

        # --- 第 3 段: ³He + ³He → ⁴He + 2¹H (中央で合流) ---
        self._update_caption(
            caption,
            "③ 2つの³Heが合流 → ⁴He + 陽子2個",
            "Two ³He merge → ⁴He + two protons",
        )
        self._step_merge_to_he4(branches)

        self._update_caption(
            caption,
            "正味: 6個の陽子 → ⁴He + 陽子2個 (+ 光と熱)",
            "Net: 6 protons → ⁴He + 2 protons (+ light & heat)",
        )
        self.wait(2.0)

    # ------------------------------------------------------------------
    # 各反応ステップ
    # ------------------------------------------------------------------
    def _step_pp_to_deuteron(self, branches: list[Branch]):
        """¹H + ¹H → ²H + e⁺ + ν を両経路同時に再生する。"""
        # 2 つの陽子を融合点へ寄せる
        approach = []
        for b in branches:
            approach += [
                b.p1.animate.move_to(b.fuse_a),
                b.p2.animate.move_to(b.fuse_a),
            ]
        self.play(*approach, run_time=1.0)

        # 融合: 陽子2個 → 重水素、陽電子とニュートリノを放出
        flashes, fades, appears, emits = [], [], [], []
        for b in branches:
            b.deuteron = make_nucleus(["p", "n"]).move_to(b.fuse_a)
            b.nucleus_label = make_label("²H").next_to(b.deuteron, DOWN, buff=0.18)

            flashes.append(Flash(b.fuse_a, color=POSITRON_COLOR, flash_radius=0.6))
            fades += [FadeOut(b.p1), FadeOut(b.p2)]
            appears += [FadeIn(b.deuteron, scale=0.4), FadeIn(b.nucleus_label)]

            # e⁺ と ν を経路の外向き (sign 方向) へ飛ばす
            positron = self._emitted("e⁺", POSITRON_COLOR, b.fuse_a)
            neutrino = self._emitted("ν", NEUTRINO_COLOR, b.fuse_a)
            target_e = [b.fuse_a[0] - 0.8, b.fuse_a[1] + b.sign * 1.7, 0]
            target_v = [b.fuse_a[0] + 0.4, b.fuse_a[1] + b.sign * 1.9, 0]
            emits.append(self._fly_out(positron, target_e))
            emits.append(self._fly_out(neutrino, target_v))

        self.play(*flashes, *fades, *appears, run_time=0.8)
        self.play(*emits, run_time=1.1)
        self.wait(0.3)

    def _step_deuteron_to_he3(self, branches: list[Branch]):
        """²H + ¹H → ³He + γ を両経路同時に再生する。"""
        # 重水素とラベルを融合点 B へ、待機していた陽子も合流させる
        approach = []
        for b in branches:
            approach += [
                b.deuteron.animate.move_to(b.fuse_b),
                b.nucleus_label.animate.next_to([b.fuse_b[0], b.fuse_b[1], 0], DOWN, buff=0.18),
                b.p3.animate.move_to(b.fuse_b),
            ]
        self.play(*approach, run_time=1.1)

        # 融合: 重水素 + 陽子 → ³He、ガンマ線を放出
        flashes, fades, appears, emits = [], [], [], []
        for b in branches:
            b.helium3 = make_nucleus(["p", "p", "n"]).move_to(b.fuse_b)
            new_label = make_label("³He").next_to(b.helium3, DOWN, buff=0.18)

            flashes.append(Flash(b.fuse_b, color=GAMMA_COLOR, flash_radius=0.7))
            fades += [FadeOut(b.deuteron), FadeOut(b.p3)]
            appears += [
                FadeIn(b.helium3, scale=0.4),
                Transform(b.nucleus_label, new_label),
            ]

            gamma = self._emitted("γ", GAMMA_COLOR, b.fuse_b)
            target_g = [b.fuse_b[0] + 0.2, b.fuse_b[1] + b.sign * 1.9, 0]
            emits.append(self._fly_out(gamma, target_g))

        self.play(*flashes, *fades, *appears, run_time=0.8)
        self.play(*emits, run_time=1.0)
        self.wait(0.3)

    def _step_merge_to_he4(self, branches: list[Branch]):
        """³He + ³He → ⁴He + 2¹H を中央で合流させて再生する。"""
        top, bot = branches
        # 2 つの ³He を中央付近へ寄せる
        self.play(
            top.helium3.animate.move_to([0.2, 0.5, 0]),
            top.nucleus_label.animate.next_to([0.2, 0.5, 0], UP, buff=0.18),
            bot.helium3.animate.move_to([0.2, -0.5, 0]),
            bot.nucleus_label.animate.next_to([0.2, -0.5, 0], DOWN, buff=0.18),
            run_time=1.2,
        )

        # 合流: ³He 2 個 → ⁴He、余った陽子 2 個を放出
        center = [0.2, 0.0, 0]
        helium4 = make_nucleus(["p", "p", "n", "n"]).move_to(center).scale(1.15)
        he4_label = make_label("⁴He", color=YELLOW_A).next_to(helium4, DOWN, buff=0.2)

        free_p1 = make_nucleon("p").move_to(center)
        free_p2 = make_nucleon("p").move_to(center)

        self.play(
            Flash(center, color=YELLOW_A, flash_radius=1.0, num_lines=20),
            FadeOut(top.helium3),
            FadeOut(bot.helium3),
            FadeOut(top.nucleus_label),
            FadeOut(bot.nucleus_label),
            FadeIn(helium4, scale=0.4),
            FadeIn(he4_label),
            run_time=0.9,
        )

        # 余剰陽子 2 個が右へ飛び出す (次の反応の燃料に戻る)
        p1_label = make_label("¹H", PROTON_COLOR)
        p2_label = make_label("¹H", PROTON_COLOR)
        p1_label.add_updater(lambda m: m.next_to(free_p1, UP, buff=0.1))
        p2_label.add_updater(lambda m: m.next_to(free_p2, UP, buff=0.1))
        self.add(free_p1, free_p2, p1_label, p2_label)
        self.play(
            free_p1.animate.move_to([4.0, 1.4, 0]),
            free_p2.animate.move_to([4.0, -1.4, 0]),
            run_time=1.3,
        )
        p1_label.clear_updaters()
        p2_label.clear_updaters()

        # ⁴He を少し強調
        self.play(Indicate(VGroup(helium4, he4_label), color=YELLOW_A, scale_factor=1.2))

    # ------------------------------------------------------------------
    # 補助メソッド
    # ------------------------------------------------------------------
    def _emitted(self, text: str, color, pos) -> VGroup:
        """放出粒子 (e⁺ / ν / γ) の小さなマーカーを作る。"""
        dot = Dot(radius=0.09, color=color)
        label = Text(text, font_size=20, color=color, weight=BOLD).next_to(dot, RIGHT, buff=0.05)
        return VGroup(dot, label).move_to(pos)

    def _fly_out(self, mobject: VGroup, target) -> AnimationGroup:
        """放出粒子をフェードインしながら飛ばし、最後に消すアニメーション。"""
        return Succession(
            AnimationGroup(
                FadeIn(mobject, scale=0.5),
                mobject.animate.move_to(target),
                lag_ratio=0.0,
            ),
            FadeOut(mobject, run_time=0.3),
        )

    def _update_caption(self, caption: VGroup, jp: str, en: str):
        """下部の日英併記テロップを差し替える。"""
        new_caption = make_caption(jp, en)
        self.play(Transform(caption, new_caption), run_time=0.5)
