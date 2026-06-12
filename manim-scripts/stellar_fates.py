"""燃え尽きた星のゆくえ (白色矮星 → 中性子星 → ブラックホール) のアニメーション。

燃え尽きた星の最終形態は元の星の重さで決まる。電子縮退圧で支えられる
白色矮星、それでも支えきれず中性子の縮退圧で支えられる中性子星、
もはや何も支えられないブラックホール、と「潰れない星」の物語が
次のステージへ続いていく分岐図を見せる。

yt_script.md の「8. 限界を超えたら何が起きる？」の後半に対応するカット。

構成:
    ① 白色矮星: 電子が支える (〜太陽の1.4倍まで)
    ② もっと重いと → 中性子星: 中性子が支える
    ③ さらに重いと → ブラックホール: もう何も支えられない
    ④ まとめ: 物語は次のステージへ

タイトルは動画編集側(FCP)で付与するため入れていない。キャプションは日英併記。

レンダリング例:
    manim -pql manim-scripts/stellar_fates.py StellarFates   # 低画質プレビュー
    manim -pqh manim-scripts/stellar_fates.py StellarFates   # 高画質
"""

import numpy as np
from manim import *

# 配色
WD_CORE = "#EAF2FF"        # 白色矮星 (白〜淡青)
WD_RIM = "#9FB8D8"
NS_CORE = "#7FE3D4"        # 中性子星 (青緑)
NS_RIM = "#2BA393"
BH_FILL = "#0B0B0E"        # ブラックホール本体 (ほぼ黒)
BH_RING = "#C9A227"        # 降着円盤・光の輪 (金)
ARROW_COLOR = "#8A8782"    # 分岐の矢印
TAG_COLOR = "#C8643C"      # 「もっと重いと」のタグ (テラコッタ)

# 3 つの最終形態の配置
WD_POS = np.array([-4.3, 0.8, 0.0])
NS_POS = np.array([0.0, 0.8, 0.0])
BH_POS = np.array([4.3, 0.8, 0.0])


def make_caption(jp: str, en: str) -> VGroup:
    """日本語＋英語の2段キャプションを作る。"""
    jp_text = Text(jp, font_size=30, color=WHITE, weight=BOLD)
    en_text = Text(en, font_size=22, color=GRAY_B)
    return VGroup(jp_text, en_text).arrange(DOWN, buff=0.12).to_edge(DOWN, buff=0.35)


def make_glow_ball(radius: float, color: str, rim_color: str,
                   center: np.ndarray) -> VGroup:
    """中心ほど明るいグローを重ねた星の球体を作る。"""
    group = VGroup()
    for scale, opacity in [(1.0, 0.12), (0.72, 0.20), (0.45, 0.35)]:
        layer = Circle(radius=radius * scale)
        layer.set_fill(color, opacity=opacity).set_stroke(width=0)
        layer.move_to(center)
        group.add(layer)
    rim = Circle(radius=radius).set_stroke(rim_color, width=1.5, opacity=0.9)
    rim.set_fill(opacity=0).move_to(center)
    group.add(rim)
    return group


def make_node_label(jp: str, en: str, sub_jp: str, sub_en: str,
                    color: str, anchor: np.ndarray, base_radius: float) -> VGroup:
    """最終形態の名前と「何が支えるか」の注釈ラベルを作る。

    Args:
        jp: 天体名 (日本語)。
        en: 天体名 (英語)。
        sub_jp: 支える力の注釈 (日本語)。
        sub_en: 支える力の注釈 (英語)。
        color: 天体名の色。
        anchor: 天体の中心座標。
        base_radius: 天体の描画半径 (ラベル位置の基準)。

    Returns:
        名前と注釈を縦に並べた VGroup。
    """
    name_jp = Text(jp, font_size=26, color=color, weight=BOLD)
    name_en = Text(en, font_size=18, color=GRAY_B)
    sub1 = Text(sub_jp, font_size=18, color=GRAY_B)
    sub2 = Text(sub_en, font_size=14, color=GRAY_C)
    group = VGroup(name_jp, name_en, sub1, sub2).arrange(DOWN, buff=0.08)
    group.next_to([anchor[0], anchor[1] - base_radius, 0], DOWN, buff=0.3)
    return group


class StellarFates(Scene):
    """白色矮星 → 中性子星 → ブラックホールの分岐図を見せるシーン。"""

    def construct(self):
        self.caption = None

        self.show_caption("燃え尽きた星のゆくえは、重さで決まる",
                          "A dead star's fate is decided by its mass")
        self.wait(0.4)

        # --- ① 白色矮星 ---
        wd = make_glow_ball(0.75, WD_CORE, WD_RIM, WD_POS)
        wd_label = make_node_label(
            "白色矮星", "white dwarf",
            "電子が支える", "held up by electrons",
            WD_RIM, WD_POS, 0.75,
        )
        wd_mass = Text("〜太陽の1.4倍まで / up to 1.4 Suns",
                       font_size=16, color=GRAY_B)
        wd_mass.next_to([WD_POS[0], WD_POS[1] + 0.75, 0], UP, buff=0.25)
        self.show_caption("ここまで見てきた白色矮星は、電子が支えている",
                          "The white dwarf we met is held up by electrons")
        self.play(FadeIn(wd, scale=0.8), FadeIn(wd_label), FadeIn(wd_mass),
                  run_time=1.2)
        self.wait(0.8)

        # --- ② もっと重いと → 中性子星 ---
        arrow1, tag1 = self._make_branch_arrow(
            WD_POS, NS_POS, 0.95, 0.6,
            "もっと重いと", "if heavier",
        )
        self.show_caption("電子でも支えきれないと、中性子が支える星になる",
                          "When electrons give way, neutrons take over")
        self.play(GrowArrow(arrow1), FadeIn(tag1), run_time=0.9)

        ns = make_glow_ball(0.45, NS_CORE, NS_RIM, NS_POS)
        ns_label = make_node_label(
            "中性子星", "neutron star",
            "中性子が支える", "held up by neutrons",
            NS_RIM, NS_POS, 0.45,
        )
        self.play(FadeIn(ns, scale=0.6), FadeIn(ns_label), run_time=1.0)
        # 中性子星はさらに小さい: 圧縮の強さを一瞬の収縮で示す
        self.play(Indicate(ns, color=NS_CORE, scale_factor=1.12), run_time=0.8)
        self.wait(0.8)

        # --- ③ さらに重いと → ブラックホール ---
        arrow2, tag2 = self._make_branch_arrow(
            NS_POS, BH_POS, 0.65, 0.85,
            "さらに重いと", "heavier still",
        )
        self.show_caption("それでも重ければ、もう何も止められない",
                          "Heavier still, and nothing can stop gravity")
        self.play(GrowArrow(arrow2), FadeIn(tag2), run_time=0.9)

        bh = self._make_black_hole()
        bh_label = make_node_label(
            "ブラックホール", "black hole",
            "すべてを飲み込む", "nothing can hold it up",
            BH_RING, BH_POS, 0.7,
        )
        self.play(FadeIn(bh, scale=0.7), FadeIn(bh_label), run_time=1.2)
        self.play(Rotate(bh[-1], angle=PI / 3, about_point=BH_POS), run_time=1.2)
        self.wait(0.8)

        # --- ④ まとめ ---
        self.show_caption("『潰れない星』の物語は、次のステージへ",
                          "The story of stars that refuse to collapse goes on")
        self.play(
            Indicate(wd, color=WD_CORE, scale_factor=1.06),
            Indicate(ns, color=NS_CORE, scale_factor=1.06),
            Indicate(bh, color=BH_RING, scale_factor=1.06),
            run_time=1.4,
        )
        self.wait(2.0)

    # ------------------------------------------------------------------
    # 部品づくり
    # ------------------------------------------------------------------
    def _make_branch_arrow(self, from_pos: np.ndarray, to_pos: np.ndarray,
                           from_r: float, to_r: float,
                           tag_jp: str, tag_en: str) -> tuple[Arrow, VGroup]:
        """天体間をつなぐ矢印と「もっと重いと」のタグを作る。

        Args:
            from_pos: 矢印の出発側の天体の中心。
            to_pos: 矢印の到着側の天体の中心。
            from_r: 出発側の天体の半径 (矢印の始点を縁から出すため)。
            to_r: 到着側の天体の半径。
            tag_jp: 矢印の上に添える日本語タグ。
            tag_en: 矢印の上に添える英語タグ。

        Returns:
            (矢印, タグの VGroup) のタプル。
        """
        start = from_pos + RIGHT * (from_r + 0.25)
        end = to_pos + LEFT * (to_r + 0.25)
        arrow = Arrow(start=start, end=end, buff=0, color=ARROW_COLOR,
                      stroke_width=4, tip_length=0.22)
        tag_jp_text = Text(tag_jp, font_size=20, color=TAG_COLOR, weight=BOLD)
        tag_en_text = Text(tag_en, font_size=15, color=GRAY_B)
        tag = VGroup(tag_jp_text, tag_en_text).arrange(DOWN, buff=0.05)
        tag.next_to(arrow, UP, buff=0.15)
        return arrow, tag

    def _make_black_hole(self) -> VGroup:
        """事象の地平面と光の輪・降着円盤風の楕円を持つブラックホールを作る。"""
        group = VGroup()

        # 周囲のかすかなグロー
        for scale, opacity in [(1.35, 0.10), (1.15, 0.16)]:
            glow = Circle(radius=0.55 * scale)
            glow.set_fill(BH_RING, opacity=opacity).set_stroke(width=0)
            glow.move_to(BH_POS)
            group.add(glow)

        # 光の輪 (photon ring)
        ring = Circle(radius=0.58).set_stroke(BH_RING, width=3, opacity=0.95)
        ring.set_fill(opacity=0).move_to(BH_POS)
        group.add(ring)

        # 本体 (ほぼ真っ黒)
        hole = Circle(radius=0.5)
        hole.set_fill(BH_FILL, opacity=1.0).set_stroke("#2A2A33", width=1.5)
        hole.move_to(BH_POS)
        group.add(hole)

        # 降着円盤風の楕円 (回転させて動きを出す)
        disk = Ellipse(width=2.1, height=0.5)
        disk.set_stroke(BH_RING, width=2.5, opacity=0.8).set_fill(opacity=0)
        disk.rotate(-0.35).move_to(BH_POS)
        group.add(disk)

        return group

    def show_caption(self, jp: str, en: str):
        """下部キャプション(日英併記)を差し替える。"""
        new_caption = make_caption(jp, en)
        if self.caption is None:
            self.play(FadeIn(new_caption), run_time=0.5)
        else:
            self.play(FadeOut(self.caption), FadeIn(new_caption), run_time=0.5)
        self.caption = new_caption
