"""research 폴더의 md 자료 5개를 지역별로 종합해 광주_지역별_가이드.pdf를 만든다.

  - 광주송정역: 광주송정역_맛집카페_추천.md
  - 광주종합버스터미널(유스퀘어): 터미널_식당.md, 터미널_카페.md
  - 광주-기아 챔피언스 필드: 챔필주변맛집.md, 광주_숙소.md

지역마다 식당·카페·숙소를 3~5곳씩 넣는다(자료가 없는 숙소는 '조사 자료 없음'으로 표시).
사진은 research/images/, 출처는 research/images/sources.json에서 읽는다.

사용법: python scripts/make_region_pdf.py [출력경로]
"""
import json
import os
import sys
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, Spacer, Table, TableStyle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_summary_pdf import SOURCES, card  # noqa: E402
from make_terminal_pdf import (  # noqa: E402
    ACCENT, GRID, LIGHT, bullets, h1_style, h2_style, head_style, info_table, make_footer,
    new_doc, p, subtitle_style, title_style,
)

part_style = ParagraphStyle("region", parent=title_style, fontSize=16, leading=22, spaceAfter=2)
# 첫 카드와 KeepTogether로 직접 묶으므로 keepWithNext는 끈다(켜 두면 쪽이 불필요하게 넘어간다).
sec_style = ParagraphStyle("sec", parent=h1_style, keepWithNext=0)
empty_style = ParagraphStyle("empty", parent=p("").style, textColor=colors.grey, fontSize=9)


def b(label, value):
    return f"<font name='NanumBold'>{label}</font> {value}"


# 사진 키 → (출처 이름, 비고). sources.json에 없는 송정역 사진은 원본 md에 적힌 출처를 쓴다.
SONGJEONG_PHOTO = "네이버 플레이스 업체 사진"

# ---------------------------------------------------------------- 지역 데이터
# 각 가게: (사진 키, 이름, [설명 줄...])
REGIONS = [
    {
        "name": "광주송정역",
        "subtitle": "KTX·SRT 광주송정역과 1913송정역시장 주변",
        "info": [
            ["기준점", "광주송정역 (광주 광산구)"],
            ["조사일", "2026-11-12"],
            ["출처", "네이버 플레이스 검색 결과 (별점·리뷰 수는 조사 시점 기준)"],
        ],
        "restaurants": [
            ("01_bitgoeul_tteokgalbi", "빛고을떡갈비 광주송정본점", [
                b("메뉴:", "한우숯불떡갈비 26,000원 / 돼지숯불떡갈비 17,000원 / 육회비빔밥"),
                b("별점:", "★4.78 · 리뷰 7,215개"),
                b("주소:", "광산구 광산로29번길 14 1층"),
                b("포인트:", "송정리 떡갈비 대표 가게. 리필되는 맑은 등뼈국이 인기. 착한가격업소"),
            ]),
            ("02_youngmyeong_gukbap", "영명국밥해장국", [
                b("메뉴:", "살코기국밥 10,000원 / 모듬국밥 11,000원 / 새끼보국밥 11,000원"),
                b("별점:", "★4.34 · 리뷰 4,167개"),
                b("주소:", "광산구 송정로8번길 5 (송정역 2번 출구 도보 약 2분)"),
                b("포인트:", "암뽕순대 국밥. 새벽 2시 30분까지 영업해서 늦은 기차 전후에 좋음"),
            ]),
            ("03_jangbaeksan_yanggochi", "장백산양꼬치 송정본점", [
                b("메뉴:", "양꼬치구이(10개) 16,000원 / 양갈비살꼬치 / 옥수수온면"),
                b("별점:", "★4.71 · 리뷰 860개"),
                b("주소:", "광산구 송정로1번길 20"),
                b("포인트:", "숯불 양꼬치가 잡내 없이 깔끔하다는 후기. 저녁 모임에 좋음"),
            ]),
        ],
        "cafes": [
            ("05_fromus", "프로머스 (FROMUS)", [
                b("메뉴:", "어스커피 6,500원 / 어스레이디 6,500원 / 아메리카노 4,000원"),
                b("별점:", "★4.95 · 리뷰 2,234개"),
                b("주소:", "광산구 도산로9번길 43"),
                b("포인트:", "원목 가구로 꾸민 넓은 대형 카페. 크림라떼 '어스커피'가 인기. 21시 주문 마감"),
            ]),
            ("04_gaengsonyeon", "갱소년", [
                b("메뉴:", "팥도넛 3,800원 / 팥두유 슈페너 6,500원 / 무등산 양갱 8pcs 30,000원"),
                b("별점:", "★4.77 · 리뷰 2,803개"),
                b("주소:", "광산구 송정로8번길 7-4 1층"),
                b("포인트:", "수제 양갱 카페. 양갱 세트는 광주 기념품·선물용으로 좋음"),
            ]),
            ("06_cheongja_dabang", "청자다방 송정역점", [
                b("메뉴:", "리얼군고구마라떼 / 흑당라떼 / 인절미 빙수"),
                b("별점:", "별점 정보 없음 · 리뷰 554개"),
                b("주소:", "광산구 광산로 5 (송정역 1번 출구 약 137m, 송정역시장 맞은편)"),
                b("포인트:", "역에서 걸어서 2분. 아메리카노 1천 원대. 23시까지 영업"),
            ]),
        ],
        "lodgings": [],
        "tips": [
            "기차 시간 전후로는 역 앞의 영명국밥해장국(새벽 2시 30분까지)과 청자다방(23시까지)이 가장 가깝다.",
            "갱소년 양갱 세트는 포장이 예뻐서 돌아가는 길에 선물로 사기 좋다.",
        ],
    },
    {
        "name": "광주종합버스터미널(유스퀘어)",
        "subtitle": "유스퀘어 · 신세계백화점 광주점 주변 (터미널에서 직선거리 1km 안)",
        "info": [
            ["기준점", "광주종합버스터미널(유스퀘어), 광주 서구 무진대로 904"],
            ["조사일", "2026-11-12 (조사 도구: ego-browser)"],
            ["출처", "다이닝코드 검색 결과(점수·평점·지도 좌표), 네이버 블로그 후기(참고용)"],
        ],
        "restaurants": [
            ("r1", "시골집", [
                b("메뉴:", "김치찌개, 김치주물럭"),
                b("다이닝코드:", "77점 / 4.7 (12명)"),
                b("위치:", "서구 내방로398번길 4 · 터미널에서 직선 약 500m"),
                b("포인트:", "유스퀘어에서 멀지 않은 김치찌개 밥집"),
            ]),
            ("r2", "왕뼈사랑 유스퀘어", [
                b("메뉴:", "뼈해장국"),
                b("다이닝코드:", "75점 / 4.4 (40명)"),
                b("위치:", "서구 무진대로 937 · 직선 약 310m"),
                b("포인트:", "'광주터미널 근처 혼밥' 후기 여러 개. 24시간 영업이라는 후기 있음"),
            ]),
            ("r3", "월드밥", [
                b("메뉴:", "한식뷔페"),
                b("다이닝코드:", "74점 / 4.9 (11명)"),
                b("위치:", "서구 군분2로 54 (금호월드 지하 1층) · 직선 약 360m"),
                b("포인트:", "'생생정보통' 소개. '터미널 맛집' 후기 있음"),
            ]),
        ],
        "cafes": [
            ("c1", "라이크 마이 베이커리 유스퀘어", [
                b("종류:", "베이커리카페"),
                b("다이닝코드:", "74점 / 4.1 (14명)"),
                b("위치:", "서구 무진대로 921 · 직선 약 240m"),
                b("포인트:", "버스 기다리는 동안 머무르기 좋은 대형 카페. 반려동물 동반 가능"),
            ]),
            ("c2", "육각커피 신세계백화점광주점", [
                b("종류:", "커피 (광주 지역 체인)"),
                b("다이닝코드:", "68점 / 4.3 (5명)"),
                b("위치:", "서구 무진대로 932 (신세계백화점) · 직선 약 260m"),
                b("포인트:", "터미널 바로 옆 백화점 안이라 들르기 쉬움"),
            ]),
            ("c3", "마리앤마르코", [
                b("종류:", "브런치카페"),
                b("다이닝코드:", "66점 / 4.4 (7명)"),
                b("위치:", "서구 내방로338번길 7-16 · 직선 약 480m"),
                b("포인트:", "'예쁜', '테라스' 태그가 붙은 분위기 좋은 카페"),
            ]),
        ],
        "lodgings": [],
        "tips": [
            "터미널을 나가기 싫다면 건물 안의 모모정(일본가정식)이나 2층의 카페 미뇽(에그타르트 포장)도 있다.",
            "밤늦게는 왕뼈사랑 유스퀘어, 24시간 영업 후기가 있는 카페 갤러리24(직선 약 790m)를 고려할 만하다.",
            "터미널에서 챔피언스 필드까지는 버스로 금방 갈 수 있다(챔필주변맛집.md).",
        ],
    },
    {
        "name": "광주-기아 챔피언스 필드",
        "subtitle": "야구장에서 걸어서 20분 안의 맛집·카페 + 야구 관람 후 숙소",
        "info": [
            ["기준점", "광주-기아 챔피언스 필드 (광주 북구 서림로 10)"],
            ["조사일", "2026-11-12"],
            ["출처", "맛집·카페: 네이버 플레이스(주소·영업시간·가격), 야구팬 카페·원정 후기 / "
                   "숙소: 구글 호텔 검색 평점·거리, 네이버 블로그 후기(참고용)"],
        ],
        "restaurants": [
            ("cf_gumbada", "금바다수산", [
                b("메뉴:", "챔필 물회BOX(포장) 20,000원 / 대방어회 1인 37,000원 / 회덮밥 10,000원"),
                b("거리:", "직선 210m · 도보 약 4분 (북구 서림로 19)"),
                b("영업:", "토 12:00–22:00 / 일 15:00–22:00 · 월요일 휴무"),
                b("포인트:", "물회를 박스에 담아 야구장에 들고 갈 수 있음"),
            ]),
            ("cf_cheongwadae", "청와대 (중식당)", [
                b("메뉴:", "짬뽕 8,000원 / 우삼겹짬뽕 11,000원 / 짜장 6,000원"),
                b("거리:", "직선 290m · 도보 5~10분 (북구 천변우로79번길 83)"),
                b("영업:", "토·일 10:00–19:00 (주말 브레이크 15:30–16:00) · 화요일 휴무"),
                b("포인트:", "야구 선수들도 찾는 곳. 착한가격업소. 19시 마감이라 저녁 경기는 경기 전에"),
            ]),
            ("cf_hajun", "하준족발보쌈", [
                b("메뉴:", "반반세트(중) 43,000원 / 족발(소) 35,000원"),
                b("거리:", "직선 930m · 도보 약 15분 (북구 서림로 95 1층)"),
                b("영업:", "매일 17:00–24:00 (주문 마감 23:30)"),
                b("포인트:", "별점 4.86. 경기 끝난 뒤 늦은 저녁으로 좋음. 네이버 예약 가능"),
            ]),
            ("cf_idaepo", "이대포땔나무집", [
                b("메뉴:", "통삼겹바베큐 16,000원 / 갈매기살양념바베큐 15,000원"),
                b("거리:", "직선 930m · 도보 약 15분 (북구 중흥로 37)"),
                b("영업:", "토 16:00–23:50 · 일요일 정기 휴무"),
                b("포인트:", "참나무 장작 불향의 오래된 고깃집. KIA 선수들도 자주 찾는다고 알려짐"),
            ]),
            ("cf_mandu", "박소영왕만두", [
                b("메뉴:", "작은고기만두·작은김치만두 (8개) 각 6,000원"),
                b("거리:", "직선 1.1km · 도보 약 18분 (북구 대자로 64)"),
                b("영업:", "토·일 11:00–17:00 · 월요일, 둘째·넷째 화요일 휴무"),
                b("포인트:", "팬카페 추천 만두 포장집. 2인분부터 포장, 전화 주문 추천"),
            ]),
        ],
        "cafes": [
            ("cf_inke", "인크커피 광주기아챔피언스필드점", [
                b("메뉴:", "야구공빵 5,000원 / 아메리카노 5,400원 / 바닐라빈 라떼 6,500원"),
                b("거리:", "직선 80m · 야구장 건물 안 (1루 쪽 1층)"),
                b("영업:", "매일 10:00–19:00 (홈경기 날은 22시까지라는 후기 있음)"),
                b("포인트:", "약 800평 대형 카페. 타이거즈 굿즈샵·포토존. 경기 날은 오픈 때가 한산"),
            ]),
            ("cf_phil", "필로스팅하우스", [
                b("메뉴:", "사이폰 8,000원 / 핸드드립 6,000원 / 카페라떼 5,000원"),
                b("거리:", "직선 310m · 도보 5~10분 (북구 무등로 20-1 2층)"),
                b("영업:", "토 11:00–18:30 · 일·월요일 휴무"),
                b("포인트:", "유리 기구로 내리는 사이폰 커피 전문점"),
            ]),
            ("cf_crepe", "크레페스타", [
                b("메뉴:", "크레페(누텔라/로투스/땅콩버터) 3,500원 + 토핑"),
                b("거리:", "직선 550m · 도보 약 10분 (북구 금호로 42 1층)"),
                b("영업:", "토·일 14:30–19:30 · 화요일 휴무"),
                b("포인트:", "들고 걸으며 먹기 좋아서 경기 전에 사 가기 좋음"),
            ]),
            ("cf_asteri", "아스테리", [
                b("메뉴:", "페레로로쉐 라떼 7,000원 / 브라운치즈 크로플 8,500원"),
                b("거리:", "직선 820m · 도보 약 15분 (북구 운용로 31 1층)"),
                b("영업:", "매일 07:30–23:00 (주문 마감 22:30)"),
                b("포인트:", "아침 일찍부터 밤늦게까지 열어서 언제 가도 좋음"),
            ]),
            ("cf_muhwa", "무화과로스터스", [
                b("메뉴:", "롱블랙 4,300원 / 핸드드립 · 디카페인"),
                b("거리:", "직선 840m · 도보 약 15분 (북구 금호로 79 2층)"),
                b("영업:", "매일 10:00–24:00"),
                b("포인트:", "교회 의자가 있는 로스터리 카페. 밤 12시까지라 경기 뒤에도 갈 수 있음"),
            ]),
        ],
        "lodgings": [
            ("h1", "에이치원호텔", [
                b("구글 평점:", "4.4 (리뷰 84)"),
                b("거리:", "야구장에서 약 620m"),
                b("포인트:", "수영장, 무료 주차. '챔필 도보 10~15분', '원정 직관 숙소' 후기 여러 개"),
            ]),
            ("h2", "브라운도트호텔 신안점", [
                b("구글 평점:", "4.5 (리뷰 20)"),
                b("거리:", "약 1.4km"),
                b("포인트:", "3성급. 평점은 가장 높지만 리뷰가 적고 야구장과 거리가 있음"),
            ]),
            ("h3", "소풍호텔", [
                b("구글 평점:", "4.3 (리뷰 32)"),
                b("거리:", "약 730m"),
                b("포인트:", "편의시설 정보는 구글 결과에 없었음"),
            ]),
            ("h4", "광주 에디션호텔", [
                b("구글 평점:", "4.2 (리뷰 163)"),
                b("거리:", "약 940m"),
                b("포인트:", "3성급. 조식 포함. 리뷰 수가 가장 많음"),
            ]),
            ("h5", "비지니스호텔 어반라이프", [
                b("구글 평점:", "4.2 (리뷰 21)"),
                b("거리:", "약 950m"),
                b("포인트:", "에디션호텔과 평점·거리가 거의 같음"),
            ]),
        ],
        "tips": [
            "일요일에는 이대포땔나무집·필로스팅하우스가 쉬고, 금바다수산은 15시에 연다.",
            "경기가 끝난 뒤에는 하준족발보쌈(24시), 무화과로스터스(24시), 아스테리(23시)가 늦게까지 연다.",
            "챔필 물품보관함은 경기 시작 2시간 전부터 쓸 수 있다는 원정 후기가 있다.",
            "경기 날에는 근처 숙소가 빨리 찬다는 후기가 있다. 숙소 거리는 구글 호텔 검색 표시 거리다.",
        ],
    },
]


# ---------------------------------------------------------------- 화면 구성
def overview_table():
    data = [[p(h, head_style) for h in ["지역", "식당", "카페", "숙소"]]]
    for r in REGIONS:
        def names(items):
            return "<br/>".join(n for _, n, _ in items) if items else "<font color='grey'>조사 자료 없음</font>"
        data.append([p(f"<font name='NanumBold'>{r['name']}</font>"), p(names(r["restaurants"])),
                     p(names(r["cafes"])), p(names(r["lodgings"]))])
    t = Table(data, colWidths=[36 * mm, 48 * mm, 52 * mm, 44 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def section(title, items):
    out = [Paragraph(f"{title} ({len(items)}곳)" if items else title, sec_style)]
    if not items:
        out.append(Paragraph("이 지역은 숙소 조사 자료가 없어서 넣지 않았다.", empty_style))
        return out
    cards = [card(key, i, name, lines) for i, (key, name, lines) in enumerate(items, 1)]
    # 제목이 쪽 끝에 혼자 남지 않도록 첫 카드와 묶는다.
    out = [KeepTogether([out[0]] + list(cards[0]._content))] + cards[1:]
    return out


def region_story(idx, r):
    s = [Paragraph(f"{idx}. {r['name']}", part_style), Paragraph(r["subtitle"], subtitle_style),
         Spacer(1, 8), info_table(r["info"])]
    s += section("식당", r["restaurants"])
    s += section("카페", r["cafes"])
    s += section("숙소", r["lodgings"])
    s.append(Paragraph("알아 두면 좋은 점", h2_style))
    s += bullets(r["tips"])
    return s


def sources_story():
    link_style = ParagraphStyle("link2", parent=p("").style, fontSize=7.5, leading=10)
    out = [Paragraph("부록. 사진 출처", h1_style),
           p("송정역 사진은 원본 자료(광주송정역_맛집카페_추천.md)에 적힌 대로 네이버 플레이스 업체 사진이다. "
             "나머지는 네이버 블로그 후기 사진이고(소풍호텔은 사용자가 직접 제공), 저작권은 각 작성자에게 있다."),
           Spacer(1, 6)]
    data = [[p(h, head_style) for h in ["지역", "가게 · 숙소", "출처", "블로그 글 제목 / 주소"]]]
    for r in REGIONS:
        for key, name, _ in r["restaurants"] + r["cafes"] + r["lodgings"]:
            src = SOURCES.get(key)
            if src is None or src.get("_temp"):
                who, where = SONGJEONG_PHOTO, "원본 md의 images/ 폴더 사진"
            elif src.get("link"):
                who = f"{escape(src['writer'])}" + (f"<br/>({src['date']})" if src.get("date") else "")
                where = (f"{escape(src['title'])}<br/>" if src.get("title") else "") + \
                        f"<link href='{src['link']}' color='blue'>{src['link']}</link>"
            else:
                who, where = src["site"], "사용자가 직접 제공한 사진"
            data.append([p(r["name"].split("(")[0]), p(name), p(who), Paragraph(where, link_style)])
    t = Table(data, colWidths=[26 * mm, 38 * mm, 34 * mm, 82 * mm], repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    out.append(t)
    return out


def build(out_path):
    # 송정역 사진은 sources.json에 없으므로 사진 아래 출처 문구를 따로 넣는다.
    for r in REGIONS[:1]:
        for key, _, _ in r["restaurants"] + r["cafes"]:
            SOURCES.setdefault(key, {"site": SONGJEONG_PHOTO, "writer": "", "date": "", "title": "",
                                     "link": "", "_temp": True})
    label = "광주 지역별 맛집·카페·숙소 가이드"
    s = [Paragraph("광주 지역별 맛집·카페·숙소 가이드", title_style),
         Paragraph("광주송정역 · 광주종합버스터미널(유스퀘어) · 광주-기아 챔피언스 필드", subtitle_style),
         Spacer(1, 10), Paragraph("한눈에 보기", h1_style), overview_table(), Spacer(1, 6)]
    s += bullets([
        "지역마다 식당·카페·숙소를 3~5곳씩 골랐다. 송정역과 터미널은 숙소 조사 자료가 없어서 숙소를 넣지 않았다.",
        "지역마다 조사한 사이트가 달라서 점수 기준이 다르다(송정역·챔필 맛집: 네이버 플레이스, "
        "터미널: 다이닝코드, 숙소: 구글 호텔). 지역끼리 점수를 바로 비교하지 않는 것이 좋다.",
        "모든 정보는 2026-11-12 조사 기준이다. 영업시간·가격은 바뀔 수 있으니 가기 전에 지도 앱에서 다시 확인한다.",
    ])
    for i, r in enumerate(REGIONS, 1):
        s.append(PageBreak())
        s += region_story(i, r)
    s.append(PageBreak())
    s += sources_story()
    footer = make_footer(label)
    new_doc(out_path, label).build(s, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "research/광주_지역별_가이드.pdf")
