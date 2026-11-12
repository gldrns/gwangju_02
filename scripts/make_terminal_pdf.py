"""research/터미널_식당.md와 research/터미널_카페.md 내용을 통합해 광주터미널.pdf를 만든다.

사용법: python scripts/make_terminal_pdf.py [출력경로]
필요: reportlab, 나눔고딕 글꼴 (Ubuntu: apt-get install fonts-nanum)
"""
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

# 글꼴 경로는 환경 변수로 바꿀 수 있다.
FONT_DIR = os.environ.get("NANUM_FONT_DIR", "/usr/share/fonts/truetype/nanum")
pdfmetrics.registerFont(TTFont("Nanum", os.path.join(FONT_DIR, "NanumGothic.ttf")))
pdfmetrics.registerFont(TTFont("NanumBold", os.path.join(FONT_DIR, "NanumGothicBold.ttf")))

ACCENT = colors.HexColor("#1F4E79")
LIGHT = colors.HexColor("#EAF1F8")
GRID = colors.HexColor("#B7C9DB")

title_style = ParagraphStyle("title", fontName="NanumBold", fontSize=18, leading=24,
                             alignment=TA_CENTER, textColor=ACCENT, spaceAfter=4)
subtitle_style = ParagraphStyle("subtitle", fontName="Nanum", fontSize=10, leading=14,
                                alignment=TA_CENTER, textColor=colors.HexColor("#555555"))
h1_style = ParagraphStyle("h1", fontName="NanumBold", fontSize=13, leading=18,
                          textColor=ACCENT, spaceBefore=12, spaceAfter=6, keepWithNext=1)
h2_style = ParagraphStyle("h2", fontName="NanumBold", fontSize=11, leading=15,
                          spaceBefore=6, spaceAfter=3, keepWithNext=1)
body_style = ParagraphStyle("body", fontName="Nanum", fontSize=9.5, leading=14)
bullet_style = ParagraphStyle("bullet", parent=body_style, leftIndent=10, bulletIndent=2)
cell_style = ParagraphStyle("cell", fontName="Nanum", fontSize=8.5, leading=12)
head_style = ParagraphStyle("head", fontName="NanumBold", fontSize=8.5, leading=12,
                            textColor=colors.white, alignment=TA_CENTER)

# ---- 통합 데이터 (두 md 파일 내용 정리) ----
RESTAURANTS = [
    ("1", "시골집", "김치찌개, 김치주물럭", "77점 / 4.7 (12명)", "약 500m",
     "서구 내방로398번길 4. 블로그 후기에 유스퀘어 광주터미널에서 멀지 않다고 나옴"),
    ("2", "왕뼈사랑 유스퀘어", "뼈해장국", "75점 / 4.4 (40명)", "약 310m",
     "서구 무진대로 937. \"광주터미널 근처 혼밥\" 후기 여러 개. 24시간 영업이라는 후기 있음"),
    ("3", "월드밥", "한식뷔페", "74점 / 4.9 (11명)", "약 360m",
     "서구 군분2로 54(금호월드 지하 1층). \"생생정보통\" 태그. \"터미널 맛집\" 후기 있음"),
]
CAFES = [
    ("1", "라이크 마이 베이커리 유스퀘어", "베이커리카페", "74점 / 4.1 (14명)", "약 240m",
     "서구 무진대로 921. \"버스 기다리는 동안 머무르기 좋은 대형카페\" 후기 여러 개. 반려동물동반 태그"),
    ("2", "육각커피 신세계백화점광주점", "커피", "68점 / 4.3 (5명)", "약 260m",
     "서구 무진대로 932(신세계백화점). 광주 지역 체인"),
    ("3", "마리앤마르코", "브런치카페", "66점 / 4.4 (7명)", "약 480m",
     "서구 내방로338번길 7-16. \"예쁜\", \"테라스\" 태그"),
]
ALTERNATIVES = [
    ("터미널 밖으로 안 나가고 싶을 때", [
        "모모정 광주유스퀘어점 (식당, 일본가정식, 70점, 터미널 건물 안)",
        "카페 미뇽 (카페, 58점 / 4.7 (4명), 터미널 2층) — 버스 타기 전에 에그타르트를 포장한다는 후기",
    ]),
    ("밤늦게 갈 때 (24시간 영업 후기 있음)", [
        "왕뼈사랑 유스퀘어 (식당 추천 2위)",
        "갤러리24 (카페, 65점 / 4.6 (10명), 약 790m) — 카페 3위와 1점 차이",
    ]),
    ("메뉴를 바꾸고 싶을 때", [
        "광주옥1947 (평양냉면, 74점 / 4.2 (20명), 약 930m) — 월드밥과 점수 같음. \"흑백요리사\" 태그",
    ]),
    ("점수는 높지만 뺀 곳", [
        "루키초밥 농성점 (81점) — 직선거리 약 1.3km로 범위 밖",
        "궁전제과 신세계백화점광주점 (69점) — 빵집이라서 제외",
        "심경희 라라랜드 (LA갈비, 70점, 약 380m), 양푼매운갈비찜 2호점 (67점, 약 390m) — 점수가 낮아서 제외",
        "플레이커피 (디저트카페, 65점 / 4.3 (6명), 약 770m) — 점수가 낮아서 제외",
    ]),
]


def p(text, style=cell_style):
    return Paragraph(text, style)


def place_table(rows, kind_label):
    """추천 가게 표를 만든다."""
    header = ["#", "가게", kind_label, "점수 / 평점 (인원)", "직선거리", "주소 · 참고"]
    data = [[p(h, head_style) for h in header]]
    for r in rows:
        data.append([p(r[0]), p(f"<font name='NanumBold'>{r[1]}</font>"),
                     p(r[2]), p(r[3]), p(r[4]), p(r[5])])
    widths = [8 * mm, 34 * mm, 24 * mm, 28 * mm, 17 * mm, 69 * mm]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return t


def summary_table():
    """식당·카페 6곳을 거리순으로 한눈에 보는 표."""
    items = [("식당", r) for r in RESTAURANTS] + [("카페", c) for c in CAFES]
    items.sort(key=lambda x: int(x[1][4].replace("약 ", "").replace("m", "")))
    data = [[p(h, head_style) for h in ["구분", "가게", "메뉴 / 종류", "점수", "직선거리"]]]
    for kind, r in items:
        data.append([p(kind), p(r[1]), p(r[2]), p(r[3].split(" / ")[0]), p(r[4])])
    t = Table(data, colWidths=[16 * mm, 62 * mm, 42 * mm, 22 * mm, 22 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
    ]))
    return t


def bullets(items):
    return [Paragraph(i, bullet_style, bulletText="•") for i in items]


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Nanum", 8)
    canvas.setFillColor(colors.grey)
    canvas.drawCentredString(A4[0] / 2, 10 * mm, f"광주종합버스터미널 주변 식당·카페 가이드 — {doc.page}")
    canvas.restoreState()


def build(out_path):
    doc = SimpleDocTemplate(out_path, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=15 * mm, bottomMargin=18 * mm,
                            title="광주종합버스터미널 주변 식당·카페 가이드")
    s = []
    s.append(Paragraph("광주종합버스터미널(유스퀘어) 주변 식당·카페 가이드", title_style))
    s.append(Paragraph("터미널에서 직선거리 1km 안 · 식당 3곳 + 카페 3곳", subtitle_style))
    s.append(Spacer(1, 8))

    info = [
        ["기준점", "광주종합버스터미널(유스퀘어), 광주광역시 서구 무진대로 904"],
        ["조사일", "2026-11-12 (조사 도구: ego-browser)"],
        ["출처", "다이닝코드 검색 결과(유스퀘어·광천동·농성동·화정동 상위 결과, 가게 페이지의 주소와 지도 좌표), "
               "네이버 검색 결과(\"광주버스터미널 맛집\", \"광주버스터미널 카페\")"],
    ]
    it = Table([[p(f"<font name='NanumBold'>{k}</font>"), p(v)] for k, v in info],
               colWidths=[22 * mm, 158 * mm])
    it.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    s.append(it)

    s.append(Paragraph("1. 한눈에 보기 (가까운 순)", h1_style))
    s.append(summary_table())

    s.append(Paragraph("2. 식당 추천 3곳", h1_style))
    s.append(place_table(RESTAURANTS, "메뉴"))

    s.append(Paragraph("3. 카페 추천 3곳", h1_style))
    s.append(place_table(CAFES, "종류"))

    s.append(Paragraph("4. 상황별 대안", h1_style))
    for heading, items in ALTERNATIVES:
        s.append(Paragraph(heading, h2_style))
        s.extend(bullets(items))

    s.append(Paragraph("5. 선정 기준", h1_style))
    s.extend(bullets([
        "다이닝코드 검색 결과 4개에서 나온 가게의 지도 좌표로 터미널과의 <font name='NanumBold'>직선거리</font>를 "
        "계산해서 1km 안인 곳만 남기고, 다이닝코드 점수가 높은 순서로 3곳씩 골랐다.",
        "식당: 카페, 베이커리, 떡집, 디저트, 술집 위주의 가게는 뺐다.",
        "카페: 커피와 음료가 중심인 곳만 넣었다. 빵집, 도넛·크로플 같은 디저트 가게, 카페 태그가 붙은 식당은 뺐다.",
        "네이버 플레이스 상단 결과는 대부분 광고라서 근거로 쓰지 않았고, 네이버 블로그 후기는 참고로만 적었다.",
    ]))

    s.append(Paragraph("6. 주의할 점", h1_style))
    s.extend(bullets([
        "거리는 지도 좌표로 계산한 <font name='NanumBold'>직선거리</font>다. 실제로 걷는 거리는 더 길다.",
        "검색 결과마다 상위 20곳만 봤다. 1km 안의 가게를 전부 본 것은 아니다.",
        "카페 2위(육각커피), 3위(마리앤마르코)는 평가 인원이 10명보다 적다.",
        "점수, 평점, 리뷰 내용은 조사 날짜 기준이고 바뀔 수 있다.",
        "영업시간, 가격, 휴무일은 확인하지 않았다(<font name='NanumBold'>미확인</font>). "
        "가기 전에 지도 앱에서 다시 확인하는 것이 좋다.",
    ]))

    doc.build(s, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "research/광주터미널.pdf")
