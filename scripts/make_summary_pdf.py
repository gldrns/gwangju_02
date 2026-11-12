"""터미널_식당.md, 터미널_카페.md, 광주_숙소.md를 종합하고
가게·숙소 대표 사진을 넣어 종합.pdf를 만든다.

사진은 research/images/ 폴더에 아래 이름으로 넣는다(jpg 또는 png).
  식당: r1, r2, r3   카페: c1, c2, c3   숙소: h1 ~ h5
  예) research/images/r1.jpg = 시골집
사진이 없으면 그 자리에 '사진 준비 중' 칸을 넣는다.

사용법: python scripts/make_summary_pdf.py [출력경로]
"""
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, Spacer, Table, TableStyle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_gwangju_pdf import LODGINGS, lodging_story  # noqa: E402
from make_terminal_pdf import (  # noqa: E402
    ACCENT, CAFES, GRID, LIGHT, RESTAURANTS, h1_style, make_footer, new_doc, p,
    subtitle_style, terminal_story, title_style,
)

IMAGE_DIR = os.environ.get("GUIDE_IMAGE_DIR", "research/images")
PHOTO_W, PHOTO_H = 45 * mm, 32 * mm

part_style = ParagraphStyle("part2", parent=title_style, fontSize=15, leading=20, spaceAfter=2)
name_style = ParagraphStyle("name", fontName="NanumBold", fontSize=11, leading=15, textColor=ACCENT)
ph_style = ParagraphStyle("ph", fontName="Nanum", fontSize=8, leading=11, alignment=TA_CENTER,
                          textColor=colors.grey)


def find_photo(key):
    for ext in ("jpg", "jpeg", "png", "webp"):
        path = os.path.join(IMAGE_DIR, f"{key}.{ext}")
        if os.path.exists(path):
            return path
    return None


def photo_cell(key):
    """사진이 있으면 비율을 지켜 넣고, 없으면 빈 칸을 넣는다."""
    path = find_photo(key)
    if path:
        iw, ih = ImageReader(path).getSize()
        scale = min(PHOTO_W / iw, PHOTO_H / ih)
        return Image(path, width=iw * scale, height=ih * scale)
    box = Table([[Paragraph("사진 준비 중", ph_style)]], colWidths=[PHOTO_W], rowHeights=[PHOTO_H])
    box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F2F2F2")),
        ("BOX", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return box


def card(key, rank, name, lines):
    """사진 + 설명으로 된 가게 카드 한 개."""
    info = [Paragraph(f"{rank}. {name}", name_style), Spacer(1, 3)]
    info += [p(line) for line in lines]
    t = Table([[photo_cell(key), info]], colWidths=[PHOTO_W + 4 * mm, 180 * mm - PHOTO_W - 4 * mm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOX", (0, 0), (-1, -1), 0.5, GRID),
        ("BACKGROUND", (1, 0), (1, 0), colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return KeepTogether([t, Spacer(1, 5)])


def bold(label, value):
    return f"<font name='NanumBold'>{label}</font> {value}"


def place_cards(prefix, rows, kind_label):
    out = []
    for r in rows:
        out.append(card(f"{prefix}{r[0]}", r[0], r[1], [
            bold(kind_label, r[2]),
            bold("다이닝코드 점수 / 평점:", r[3]),
            bold("터미널에서 직선거리:", r[4]),
            bold("주소 · 참고:", r[5]),
        ]))
    return out


def lodging_cards():
    out = []
    for r in LODGINGS:
        out.append(card(f"h{r[0]}", r[0], r[1], [
            bold("구글 평점 (리뷰 수):", r[2]),
            bold("야구장에서 거리:", r[3]),
            bold("참고:", r[4]),
        ]))
    return out


def build(out_path):
    label = "광주 종합 가이드 (터미널 식당·카페 · 야구장 근처 숙소)"
    s = [Paragraph("광주 종합 가이드", title_style),
         Paragraph("광주종합버스터미널 주변 식당·카페 + 광주-기아 챔피언스 필드 근처 숙소", subtitle_style),
         Spacer(1, 10)]

    # 1부: 터미널 (사진 카드 → 기존 요약·대안·기준·주의)
    t = terminal_story(header_style=part_style)
    t[0] = Paragraph("1부. 광주종합버스터미널(유스퀘어) 주변 식당·카페", part_style)
    s.extend(t[:4])  # 1부 제목, 부제, 여백, 정보 표
    s.append(Paragraph("사진으로 보기 — 식당", h1_style))
    s.extend(place_cards("r", RESTAURANTS, "메뉴:"))
    s.append(Paragraph("사진으로 보기 — 카페", h1_style))
    s.extend(place_cards("c", CAFES, "종류:"))
    s.append(PageBreak())
    s.extend(t[4:])  # 한눈에 보기 표, 상세 표, 상황별 대안, 선정 기준, 주의할 점

    # 2부: 숙소
    s.append(PageBreak())
    lod = lodging_story()
    s.extend(lod[:4])  # 2부 제목, 부제, 여백, 정보 표
    s.append(Paragraph("사진으로 보기 — 숙소", h1_style))
    s.extend(lodging_cards())
    s.extend(lod[4:])

    footer = make_footer(label)
    new_doc(out_path, label).build(s, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "research/종합.pdf")
