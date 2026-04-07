# 🔔 Voice Alert

> macOS 한국어 음성 알림 앱

지정한 시각이 되면 **한국어 TTS(음성합성)** 로 알림 내용을 읽어주는 macOS 전용 데스크탑 앱입니다.  
직관적인 GUI로 알림을 추가·수정·삭제할 수 있으며, 다음 알림까지 남은 시간이 실시간으로 카운트다운됩니다.

---

## 📅 버전 정보

| 항목 | 내용 |
|------|------|
| 최초 작성일 | 2026-04-08 |
| 플랫폼 | macOS |
| 언어 | Python 3.10+ |

---

## ✨ 주요 기능

- **시간 지정 알림** — 원하는 시각(HH:MM)에 알림 설정
- **한국어 TTS** — macOS 내장 `say` 명령어로 알림 내용을 한국어로 낭독
- **차임 효과음** — 알림 발화 전 시보 차임 재생
- **사전 알림** — 지정 시각 N분 전에 미리 한 번 더 알림
- **TTS 음성 선택** — 8가지 한국어 음성 중 선택 + 미리듣기
- **실시간 카운트다운** — 다음 알림까지 남은 시간 1초마다 갱신
- **알림 관리** — 목록에서 추가·수정·삭제 / 더블클릭으로 수정 로드
- **자동 저장** — `alerts.json`에 저장되어 앱 재시작 후에도 유지
- **자정 경계 처리** — 00:05 알림의 10분 전 사전 알림(23:55)도 정확히 발화

---

## 🖥️ 스크린샷

```
┌─────────────────────────────────────────┐
│  알림 추가                              │
│  시간       [ 09 ] : [ 00 ]             │
│  알림 내용  [ 회의 시작               ] │
│  몇 분 전   [ 5  ] 분 전               │
│  TTS 음성   [ Yuna — 여성 (기본) ▾ ] [미리듣기] │
│                              [추가]     │
├─────────────────────────────────────────┤
│  저장된 알림                            │
│  시간  │ 알림 내용 │ 사전 알림 │ 상태  │
│  09:00 │ 회의 시작 │ 5분 전    │ 대기  │
├─────────────────────────────────────────┤
│  [수정]  [삭제]                         │
│  다음 알림 → 09:00 "회의 시작" | 32분 14초 후 │
└─────────────────────────────────────────┘
```

---

## 📋 요구사항

| 항목 | 요구사항 | 비고 |
|------|----------|------|
| 운영체제 | macOS 12 이상 권장 | `say` / `afplay` 명령어 필요 |
| Python | 3.10 이상 | `int \| None` 타입 힌트 사용 |
| pip 패키지 | **없음** | 표준 라이브러리만 사용 |
| macOS 명령어 | `say`, `afplay` | OS 내장 — 별도 설치 불필요 |

---

## ⚙️ 설치 방법

### 1. Python 확인

```bash
python3 --version
```

Python 3.10 미만이면 Homebrew로 업그레이드합니다.

```bash
# Homebrew 설치 (없는 경우)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Python 설치
brew install python
```

### 2. 저장소 클론

```bash
git clone https://github.com/janghyeonan/voice_alert.git
cd voice_alert
```

### 3. 앱 실행

```bash
python3 voice_alert.py
```

> 별도의 `pip install` 없이 바로 실행됩니다.

---

## 📖 사용 방법

### 알림 추가

1. **시간** 스핀박스에서 HH:MM 입력
2. **알림 내용** 입력란에 TTS로 읽어줄 텍스트 입력 (Enter로도 추가 가능)
3. **몇 분 전 알림** 설정 (0 = 사전 알림 없음)
4. **TTS 음성** 콤보박스에서 원하는 음성 선택 → [미리듣기]로 확인 가능
5. **[추가]** 버튼 클릭

### 알림 수정

- 목록에서 항목 **더블클릭** 또는 선택 후 **[수정]** 버튼
- 입력란에 기존 내용이 로드됨 → 수정 후 **[수정 완료]**
- 취소하려면 **[취소]** 버튼

### 알림 삭제

- 목록에서 항목 선택 → **[삭제]** → 확인 대화상자에서 승인

### 카운트다운

- 하단 상태바에 **다음 알림까지 남은 시간**이 실시간으로 표시됩니다.
- 예: `다음 알림 → 09:00  "회의 시작"  |  32분 14초 후`

---

## 🎙️ 지원 TTS 음성 (한국어)

| 음성 | 성별 | 특징 |
|------|------|------|
| **Yuna** | 여성 | 기본값 — 자연스럽고 또렷한 발음 |
| Eddy | 남성 | 깔끔하고 명확한 목소리 |
| Flo | 여성 | 부드러운 목소리 |
| Reed | 남성 | 차분한 목소리 |
| Sandy | 여성 | 밝고 친근한 목소리 |
| Shelley | 여성 | 명확한 목소리 |
| Grandma | 여성 | 연로한 여성 목소리 |
| Grandpa | 남성 | 연로한 남성 목소리 |

---

## 🔧 커스터마이징

### TTS 속도 변경

[voice_alert.py](voice_alert.py) 의 `speak()` 함수에서 `-r` 옵션 추가:

```python
subprocess.Popen(["say", "-v", voice or TTS_VOICE, "-r", "160", text])
# 기본값 약 200 / 낮을수록 느림
```

### 차임 소리 변경

파일 상단의 `CHIME_SOUND` 경로를 변경:

```python
CHIME_SOUND = "/System/Library/Sounds/Ping.aiff"
# 선택 가능: Glass / Ping / Tink / Hero / Funk / Bottle / Frog / Pop / Purr
```

---

## 📁 파일 구성

```
voice_alert/
├── voice_alert.py         # 메인 앱
├── make_manual.py         # PDF 사용설명서 생성 스크립트
├── requirements.txt       # 패키지 목록
├── .gitignore
└── README.md
```

> `alerts.json` — 알림 데이터 파일은 첫 실행 시 자동 생성되며 `.gitignore`에 포함되어 있습니다.

---

## 📄 PDF 사용설명서 생성

상세 사용설명서를 PDF로 생성할 수 있습니다.

```bash
# fpdf2 설치 (make_manual.py 전용)
pip3 install fpdf2

# PDF 생성
python3 make_manual.py
# → voice_alert_manual.pdf 생성
```

---

## 🧩 오픈소스 사용 내역

이 앱은 아래 오픈소스 라이브러리를 사용합니다.

| 라이브러리 | 용도 | 라이선스 |
|-----------|------|---------|
| [fpdf2](https://github.com/py-pdf/fpdf2) | PDF 사용설명서 생성 (`make_manual.py` 전용) | LGPL-3.0 |

앱 본체(`voice_alert.py`)는 Python 표준 라이브러리와 macOS 내장 명령어만 사용합니다.

| 모듈 / 명령어 | 출처 |
|--------------|------|
| `tkinter` | Python 표준 라이브러리 |
| `threading`, `subprocess`, `json`, `datetime` | Python 표준 라이브러리 |
| `say` | macOS 내장 TTS |
| `afplay` | macOS 내장 오디오 플레이어 |

---

## 📜 라이선스

MIT License — 자유롭게 사용·수정·배포할 수 있습니다.
