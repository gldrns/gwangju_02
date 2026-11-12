"""터미널 식당·카페(research/터미널_식당.md, 터미널_카페.md)와
야구장 근처 숙소(research/광주_숙소.md)를 합쳐 광주터미널및숙소.pdf를 만든다.

사용법: python scripts/make_gwangju_pdf.py [출력경로]
"""
import os
import sys

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, Spacer, Table, TableStyle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_terminal_pdf import (  # noqa: E402
    ACCENT, GRID, LIGHT, bullets, h1_style, h2_style, head_style, info_table, make_footer,
    new_doc, p, subtitle_style, terminal_story, title_style,
)
from reportlab.lib.styles import ParagraphStyle  # noqa: E402

part_style = ParagraphStyle("part", parent=title_style, fontSize=15, leading=20, spaceAfter=2)

# ---- 숙소 데이터 (research/광주_숙소.md 정리) ----
LODGINGS = [
    ("1", "에이치원호텔", "4.4 (84)", "약 620m",
     "수영장, 무료 주차. 네이버 블로그에 \"챔필 도보 10~15분\", \"원정 직관 숙소\" 후기 여러 개"),
    ("2", "브라운도트호텔 신안점", "4.5 (20)", "약 1.4km",
     "3성급. 평점은 가장 높지만 리뷰가 20개뿐이고 야구장과 거리가 있음"),
    ("3", "소풍호텔", "4.3 (32)", "약 730m", "편의시설 정보는 구글 결과에 없었음"),
    ("4", "광주 에디션호텔", "4.2 (163)", "약 940m", "3성급. 조식 포함. 리뷰 수가 5곳 중 가장 많음"),
    ("5", "비지니스호텔 어반라이프", "4.2 (21)", "약 950m",
     "4위와 평점·거리가 거의 같음. 리뷰 수가 더 많은 4위를 위에 둠"),
]
LODGING_EXCLUDED = [
    "비엔날레호텔 (3.8 (103), 약 640m) — 가깝고 \"챔피언스필드 도보권\" 후기가 있지만 평점이 낮아서 제외",
    "호텔더아라보다 화정점 (4.2 (26), 약 1.5km) — 같은 평점 구간의 다른 곳보다 멀어서 제외",
    "여기조아무인호텔 (4.1 (20), 약 720m) — 평점이 3~5위보다 낮아서 제외",
    "광주 이지스테이호텔 (5.0 (8), 약 1.5km) — \"챔피언스필드 도보 가능\" 후기가 있지만 리뷰가 8개뿐이라 제외",
]


def lodging_table():
    header = ["#", "숙소", "구글 평점 (리뷰 수)", "야구장에서 거리", "참고"]
    data = [[p(h, head_style) for h in header]]
    for r in LODGINGS:
        data.append([p(r[0]), p(f"<font name='NanumBold'>{r[1]}</font>"), p(r[2]), p(r[3]), p(r[4])])
    t = Table(data, colWidths=[8 * mm, 40 * mm, 30 * mm, 24 * mm, 78 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def lodging_story():
    s = []
    s.append(Paragraph("2부. 광주-기아 챔피언스 필드 야구 관람 후 숙소 5선", part_style))
    s.append(Paragraph("구글 호텔 평점 + 야구장에서의 거리 기준 · 거리 제한 없음", subtitle_style))
    s.append(Spacer(1, 8))
    s.append(info_table([
        ["기준점", "광주-기아 챔피언스 필드"],
        ["조사일", "2026-11-12 (조사 도구: ego-browser)"],
        ["출처", "구글 호텔 검색 결과(\"광주 기아챔피언스필드 근처 호텔\" → 주변 124개), "
               "네이버 검색 결과(\"기아챔피언스필드 숙소\", \"챔피언스필드 근처 호텔\")"],
    ]))

    s.append(Paragraph("1. 숙소 추천 5곳", h1_style))
    s.append(lodging_table())

    s.append(Paragraph("2. 후보였지만 뺀 곳", h1_style))
    s.extend(bullets(LODGING_EXCLUDED))

    s.append(Paragraph("3. 선정 기준", h1_style))
    s.extend(bullets([
        "구글 호텔 검색의 평점(5점 만점)과 챔피언스 필드에서의 거리를 기준으로 삼았다.",
        "리뷰가 20개보다 적은 곳, 스폰서(광고) 결과, 공유숙박(에어비앤비 같은 집 숙소)은 뺐다.",
        "평점을 0.2점 폭으로 나누고(4.4~4.5 구간: 1~2위, 4.2~4.3 구간: 3~5위), "
        "같은 구간 안에서는 야구장에서 가까운 순으로 순위를 매겼다.",
        "1km 제한은 두지 않았다. 네이버 블로그 후기는 참고로만 적었다.",
    ]))

    s.append(Paragraph("4. 주의할 점", h1_style))
    s.extend(bullets([
        "거리는 구글 호텔 검색에 표시된 거리다. 실제로 걷는 거리는 더 길 수 있다.",
        "평점과 리뷰 수는 조사 날짜 기준이고 바뀔 수 있다.",
        "가격은 날짜마다 달라서 적지 않았다. 경기 날에는 근처 숙소가 빨리 찬다는 후기가 있다.",
        "정확한 주소, 체크인·체크아웃 시간, 주차 조건은 확인하지 않았다(<font name='NanumBold'>미확인</font>). "
        "예약 전에 숙소 페이지에서 다시 확인하는 것이 좋다.",
        "네이버 플레이스의 거리는 야구장이 아니라 검색 위치 기준이라서 쓰지 않았다.",
    ]))
    return s


def build(out_path):
    label = "광주 터미널 식당·카페 및 야구장 근처 숙소 가이드"
    s = [Paragraph("광주 여행 가이드", title_style),
         Paragraph("1부: 광주종합버스터미널 주변 식당·카페 · 2부: 챔피언스 필드 근처 숙소", subtitle_style),
         Spacer(1, 10)]
    s.extend(terminal_story(header_style=part_style))
    s[3] = Paragraph("1부. 광주종합버스터미널(유스퀘어) 주변 식당·카페", part_style)
    s.append(PageBreak())
    s.extend(lodging_story())
    footer = make_footer(label)
    new_doc(out_path, label).build(s, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "research/광주터미널및숙소.pdf")
