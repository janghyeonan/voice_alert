"""
voice_alert 사용설명서 PDF 생성 스크립트

설치:
    pip3 install fpdf2

실행:
    python3 make_manual.py
"""

from fpdf import FPDF
from fpdf.enums import XPos, YPos
import os
import sys

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_alert_manual.pdf")
FONT_TTF = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

# ── 폰트 존재 확인 ────────────────────────────────────────────────────────────
if not os.path.exists(FONT_TTF):
    print("오류: AppleSDGothicNeo.ttc 폰트를 찾을 수 없습니다.")
    print("이 스크립트는 macOS에서만 실행 가능합니다.")
    sys.exit(1)

# ── PDF 클래스 ────────────────────────────────────────────────────────────────

class ManualPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Ko", "",  FONT_TTF)
        self.add_font("Ko", "B", FONT_TTF)
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        self.set_font("Ko", "B", 10)
        self.set_text_color(140, 140, 140)
        self.cell(0, 8, "Voice Alert  —  사용설명서",
                  new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="R")
        self.set_draw_color(215, 215, 215)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-14)
        self.set_font("Ko", "", 9)
        self.set_text_color(180, 180, 180)
        self.cell(0, 8, str(self.page_no()), align="C")

    # ── 스타일 헬퍼 ──────────────────────────────────────────────────────────

    def h2(self, text: str):
        self.set_font("Ko", "B", 13)
        self.set_text_color(35, 85, 190)
        self.ln(5)
        self.cell(0, 9, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_draw_color(35, 85, 190)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def body(self, text: str, indent: int = 0):
        self.set_font("Ko", "", 11)
        self.set_text_color(50, 50, 50)
        self.set_x(10 + indent)
        self.multi_cell(0, 7, text)
        self.ln(1)

    def bullet(self, text: str, indent: int = 4):
        self.set_font("Ko", "", 11)
        self.set_text_color(50, 50, 50)
        x_orig = self.get_x()
        self.set_x(10 + indent)
        self.cell(5, 7, "•")
        self.multi_cell(0, 7, text)
        self.set_x(x_orig)

    def code(self, text: str):
        self.set_font("Ko", "", 10)
        self.set_fill_color(240, 242, 246)
        self.set_text_color(30, 30, 30)
        self.set_x(10)
        self.multi_cell(0, 6.5, text, fill=True)
        self.ln(2)

    def table(self, headers: list, rows: list, col_widths: list):
        # 헤더 행
        self.set_font("Ko", "B", 10)
        self.set_fill_color(35, 85, 190)
        self.set_text_color(255, 255, 255)
        for h, w in zip(headers, col_widths):
            self.cell(w, 8, h, border=1, fill=True)
        self.ln()
        # 데이터 행 (홀짝 줄무늬)
        self.set_font("Ko", "", 10)
        self.set_text_color(40, 40, 40)
        for i, row in enumerate(rows):
            if i % 2 == 0:
                self.set_fill_color(245, 248, 255)
            else:
                self.set_fill_color(255, 255, 255)
            for cell_text, w in zip(row, col_widths):
                self.cell(w, 8, cell_text, border=1, fill=True)
            self.ln()
        self.ln(3)


# ── PDF 내용 작성 ─────────────────────────────────────────────────────────────

pdf = ManualPDF()
pdf.add_page()

# 타이틀 블록
pdf.set_font("Ko", "B", 26)
pdf.set_text_color(20, 20, 20)
pdf.ln(4)
pdf.cell(0, 15, "Voice Alert",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
pdf.set_font("Ko", "", 13)
pdf.set_text_color(110, 110, 110)
pdf.cell(0, 8, "macOS 한국어 음성 알림 앱  —  사용설명서",
         new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
pdf.ln(10)

# ── 1. 개요 ──────────────────────────────────────────────────────────────────
pdf.h2("1. 개요")
pdf.body(
    "Voice Alert는 지정한 시각이 되면 한국어 TTS(음성합성)로 알림 내용을 읽어주는 macOS 전용 앱입니다.\n"
    "직관적인 UI로 알림을 추가·수정·삭제할 수 있으며, 다음 알림까지 남은 시간이 실시간으로 표시됩니다.\n"
    "알림 데이터는 자동 저장되어 앱을 재시작해도 유지됩니다."
)

# ── 2. 설치 요구사항 ─────────────────────────────────────────────────────────
pdf.h2("2. 설치 요구사항")
pdf.body("앱 실행(voice_alert.py)에는 외부 패키지가 전혀 필요하지 않습니다.", indent=2)
pdf.ln(1)

pdf.table(
    headers=["항목", "요구사항", "비고"],
    rows=[
        ["운영체제",     "macOS 12 이상 권장",  "say / afplay 명령어 필요"],
        ["Python",       "3.10 이상",            "int | None 타입 힌트 사용"],
        ["pip 패키지",   "없음",                 "표준 라이브러리만 사용"],
        ["macOS 명령어", "say, afplay",           "OS 내장 — 별도 설치 불필요"],
    ],
    col_widths=[38, 54, 98]
)

pdf.body("Python 버전 확인:", indent=2)
pdf.code("    python3 --version")

pdf.body("Python 3.10 미만이면 Homebrew로 업그레이드:", indent=2)
pdf.code("    brew install python")

pdf.body("Homebrew가 없다면 먼저 설치하세요:", indent=2)
pdf.code(
    '    /bin/bash -c \\\n'
    '    "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
)

pdf.body("PDF 설명서 재생성(make_manual.py)에만 fpdf2가 필요합니다:", indent=2)
pdf.code("    pip3 install fpdf2")

# ── 3. 실행 방법 ─────────────────────────────────────────────────────────────
pdf.h2("3. 실행 방법")
pdf.body("터미널에서 아래 명령어를 실행하세요:", indent=2)
pdf.code(
    "    cd ~/Documents/voice_alert\n"
    "    python3 voice_alert.py"
)
pdf.body(
    "앱이 실행되면 macOS 창이 열립니다. 창을 최소화해도 알림은 계속 동작합니다.",
    indent=2
)

# ── 4. 화면 구성 ─────────────────────────────────────────────────────────────
pdf.h2("4. 화면 구성")
pdf.table(
    headers=["영역", "설명"],
    rows=[
        ["알림 추가 (상단 패널)",       "시간·내용·사전알림·TTS 음성 입력 후 추가"],
        ["저장된 알림 (목록)",           "등록된 알림 전체 표시 — 더블클릭하면 수정 로드"],
        ["수정 / 삭제 버튼",             "목록에서 항목 선택 후 클릭"],
        ["다음 알림 카운트다운 (하단)", "가장 가까운 미완료 알림까지 남은 시간 실시간 표시"],
    ],
    col_widths=[62, 128]
)

# ── 5. 알림 추가 방법 ────────────────────────────────────────────────────────
pdf.h2("5. 알림 추가 방법")
pdf.bullet("시간 — HH:MM 형식의 스핀박스로 입력합니다.")
pdf.bullet("알림 내용 — 지정 시각에 TTS로 읽어줄 텍스트. Enter 키로도 추가 가능합니다.")
pdf.bullet("몇 분 전 알림 — 0이면 사전 알림 없음. 예: 5 → 지정 시각 5분 전에 먼저 알림.")
pdf.bullet("TTS 음성 — 콤보박스에서 원하는 목소리 선택. [미리듣기] 버튼으로 미리 들을 수 있습니다.")
pdf.bullet("[추가] 버튼 클릭 — 알림이 목록에 저장됩니다.")
pdf.ln(2)

# ── 6. 알림 수정 / 삭제 ──────────────────────────────────────────────────────
pdf.h2("6. 알림 수정 / 삭제")
pdf.bullet("수정 — 목록 항목 더블클릭 또는 선택 후 [수정] → 입력란에 내용 로드 → 변경 후 [수정 완료].")
pdf.bullet("삭제 — 항목 선택 후 [삭제] → 확인 대화상자에서 승인.")
pdf.bullet("취소 — 수정 중 [취소] 버튼으로 편집 모드를 빠져나옵니다.")
pdf.ln(2)

# ── 7. TTS 음성 목록 ─────────────────────────────────────────────────────────
pdf.h2("7. 지원 TTS 음성 (한국어)")
pdf.table(
    headers=["음성 이름", "성별", "특징"],
    rows=[
        ["Yuna",    "여성", "기본값 — 자연스럽고 또렷한 발음"],
        ["Eddy",    "남성", "깔끔하고 명확한 남성 목소리"],
        ["Flo",     "여성", "부드러운 여성 목소리"],
        ["Reed",    "남성", "차분한 남성 목소리"],
        ["Sandy",   "여성", "밝고 친근한 여성 목소리"],
        ["Shelley", "여성", "명확한 여성 목소리"],
        ["Grandma", "여성", "연로한 여성 목소리"],
        ["Grandpa", "남성", "연로한 남성 목소리"],
    ],
    col_widths=[38, 28, 124]
)
pdf.body("* [미리듣기] 버튼으로 저장 전에 음성을 직접 확인할 수 있습니다.", indent=2)

# ── 8. 알림 동작 방식 ────────────────────────────────────────────────────────
pdf.h2("8. 알림 동작 방식")
pdf.bullet("앱은 1초마다 현재 시각을 체크합니다.")
pdf.bullet("지정 시각이 되면: Glass 차임 소리 → 1.2초 대기 → TTS로 알림 내용 낭독.")
pdf.bullet("사전 알림(N분 전)이 설정된 경우: 지정 시각 N분 전에 추가로 한 번 더 울립니다.")
pdf.bullet("같은 알림은 하루에 한 번만 울립니다 (날짜 기준). 다음날 자동 초기화됩니다.")
pdf.bullet(
    "자정 경계 케이스 자동 처리: 예를 들어 00:05 알림에 10분 전 사전 알림을 설정하면\n"
    "     전날 23:55에 정확히 발화됩니다."
)
pdf.bullet("알림 데이터는 alerts.json에 자동 저장되어 앱 재시작 후에도 유지됩니다.")
pdf.ln(2)

# ── 9. 파일 구성 ─────────────────────────────────────────────────────────────
pdf.h2("9. 파일 구성")
pdf.table(
    headers=["파일명", "설명"],
    rows=[
        ["voice_alert.py",         "메인 앱 소스코드"],
        ["alerts.json",            "저장된 알림 데이터 (첫 실행 시 자동 생성)"],
        ["requirements.txt",       "패키지 목록 (앱 실행은 설치 불필요, PDF 생성은 fpdf2 필요)"],
        ["make_manual.py",         "이 PDF를 생성하는 스크립트"],
        ["voice_alert_manual.pdf", "사용설명서 (이 파일)"],
        [".gitignore",             "Git 제외 파일 목록"],
    ],
    col_widths=[60, 130]
)

# ── 10. 자주 묻는 질문 ───────────────────────────────────────────────────────
pdf.h2("10. 자주 묻는 질문 (FAQ)")

faqs = [
    (
        "앱을 닫으면 알림도 꺼지나요?",
        "네. 앱이 실행 중이어야 알림이 울립니다. 창을 최소화해도 백그라운드에서 계속 동작합니다."
    ),
    (
        "알림이 울리지 않아요.",
        "시스템 설정 → 개인정보 보호 및 보안 → 손쉬운 사용에서\n"
        "터미널(또는 Python)에 접근 권한이 있는지 확인하세요."
    ),
    (
        "TTS 속도를 바꾸고 싶어요.",
        "voice_alert.py의 speak() 함수에서 say 명령어에 -r 옵션을 추가하세요.\n"
        "예: ['say', '-v', voice, '-r', '160', text]  (기본값 약 200, 낮을수록 느림)"
    ),
    (
        "차임 소리를 바꾸고 싶어요.",
        "voice_alert.py 상단의 CHIME_SOUND 경로를\n"
        "/System/Library/Sounds/ 안의 다른 .aiff 파일로 변경하세요.\n"
        "선택 가능: Ping.aiff / Tink.aiff / Hero.aiff / Funk.aiff / Bottle.aiff 등"
    ),
    (
        "alerts.json이 GitHub에 올라가나요?",
        "아니요. .gitignore에 alerts.json이 포함되어 있어 자동으로 제외됩니다.\n"
        "개인 알림 데이터는 로컬에만 보관됩니다."
    ),
]

for q, a in faqs:
    pdf.set_font("Ko", "B", 11)
    pdf.set_text_color(35, 85, 190)
    pdf.cell(6, 7, "Q.")
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(0, 7, q)
    pdf.set_font("Ko", "", 11)
    pdf.set_text_color(70, 70, 70)
    pdf.set_x(16)
    pdf.multi_cell(0, 7, "A.  " + a)
    pdf.ln(3)

pdf.output(OUT)
print(f"PDF 생성 완료: {OUT}")
