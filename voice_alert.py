import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import subprocess
import threading
import time
from datetime import datetime, timedelta

ALERTS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alerts.json")
CHIME_SOUND = "/System/Library/Sounds/Glass.aiff"
TTS_VOICE = "Yuna"

KO_VOICES = [
    ("Yuna  — 여성 (기본)", "Yuna"),
    ("Eddy  — 남성",        "Eddy"),
    ("Flo   — 여성",        "Flo"),
    ("Reed  — 남성",        "Reed"),
    ("Sandy — 여성",        "Sandy"),
    ("Shelley — 여성",      "Shelley"),
    ("Grandma — 여성 (노인)", "Grandma"),
    ("Grandpa — 남성 (노인)", "Grandpa"),
]

# ── 데이터 저장/불러오기 ──────────────────────────────────────────────────────

def load_alerts():
    if os.path.exists(ALERTS_FILE):
        with open(ALERTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_alerts(alerts):
    with open(ALERTS_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, ensure_ascii=False, indent=2)

# ── TTS / 사운드 ─────────────────────────────────────────────────────────────

def play_chime():
    subprocess.Popen(["afplay", CHIME_SOUND])

def speak(text, voice=None):
    subprocess.Popen(["say", "-v", voice or TTS_VOICE, text])

def notify(message, is_pre=False, pre_minutes=0, voice=None):
    play_chime()
    time.sleep(1.2)
    if is_pre:
        speak(f"{pre_minutes}분 후 알림이 있습니다. {message}", voice)
    else:
        speak(message, voice)

# ── 메인 앱 ──────────────────────────────────────────────────────────────────

class VoiceAlertApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("음성 알림")
        self.root.geometry("640x620")
        self.root.resizable(False, False)

        self.alerts = load_alerts()
        self.editing_index: int | None = None
        self._lock = threading.Lock()   # alerts 접근 보호

        self._build_ui()
        self._refresh_list()
        self._start_checker()
        self._update_countdown()

    # ── UI 구성 ──────────────────────────────────────────────────────────────

    def _build_ui(self):
        style = ttk.Style()
        # macOS aqua 테마 자동 적용; 색상만 약간 보정
        try:
            style.theme_use("aqua")
        except Exception:
            pass

        # ── 입력 영역 ──
        input_frame = ttk.LabelFrame(self.root, text="  알림 추가  ", padding=(16, 10))
        input_frame.pack(fill="x", padx=14, pady=(14, 6))
        input_frame.columnconfigure(1, weight=1)

        # 시간
        ttk.Label(input_frame, text="시간").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=6)
        time_box = ttk.Frame(input_frame)
        time_box.grid(row=0, column=1, sticky="w", pady=6)

        self.hour_var = tk.StringVar(value=datetime.now().strftime("%H"))
        self.min_var = tk.StringVar(value="00")

        vcmd_hh = (self.root.register(lambda v: v.isdigit() and 0 <= int(v) <= 23 or v == ""), "%P")
        vcmd_mm = (self.root.register(lambda v: v.isdigit() and 0 <= int(v) <= 59 or v == ""), "%P")

        ttk.Spinbox(time_box, from_=0, to=23, width=4, textvariable=self.hour_var,
                    format="%02.0f", validate="key", validatecommand=vcmd_hh).pack(side="left")
        ttk.Label(time_box, text=" : ", font=("Helvetica", 14, "bold")).pack(side="left")
        ttk.Spinbox(time_box, from_=0, to=59, width=4, textvariable=self.min_var,
                    format="%02.0f", validate="key", validatecommand=vcmd_mm).pack(side="left")

        # 알림 내용
        ttk.Label(input_frame, text="알림 내용").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=6)
        self.message_var = tk.StringVar()
        msg_entry = ttk.Entry(input_frame, textvariable=self.message_var, font=("Helvetica", 13))
        msg_entry.grid(row=1, column=1, sticky="ew", pady=6)
        msg_entry.bind("<Return>", lambda _: self._submit())

        # 몇 분 전 알림
        ttk.Label(input_frame, text="몇 분 전 알림").grid(row=2, column=0, sticky="w", padx=(0, 10), pady=6)
        before_box = ttk.Frame(input_frame)
        before_box.grid(row=2, column=1, sticky="w", pady=6)
        self.before_var = tk.StringVar(value="0")
        ttk.Spinbox(before_box, from_=0, to=120, width=5, textvariable=self.before_var).pack(side="left")
        ttk.Label(before_box, text=" 분 전", foreground="#555").pack(side="left")

        # TTS 음성 선택
        ttk.Label(input_frame, text="TTS 음성").grid(row=3, column=0, sticky="w", padx=(0, 10), pady=6)
        voice_box = ttk.Frame(input_frame)
        voice_box.grid(row=3, column=1, sticky="w", pady=6)
        voice_labels = [label for label, _ in KO_VOICES]
        self.voice_var = tk.StringVar(value=voice_labels[0])
        voice_combo = ttk.Combobox(voice_box, textvariable=self.voice_var,
                                   values=voice_labels, state="readonly", width=26)
        voice_combo.pack(side="left")
        ttk.Button(voice_box, text="미리듣기", width=7,
                   command=self._preview_voice).pack(side="left", padx=(8, 0))

        # 추가/수정 버튼
        self.submit_btn = ttk.Button(input_frame, text="추가", command=self._submit, width=8)
        self.submit_btn.grid(row=4, column=1, sticky="e", pady=(8, 2))
        self.cancel_btn = ttk.Button(input_frame, text="취소", command=self._cancel_edit, width=6)
        self.cancel_btn.grid(row=4, column=1, sticky="w", pady=(8, 2))
        self.cancel_btn.grid_remove()

        # ── 알림 목록 ──
        list_frame = ttk.LabelFrame(self.root, text="  저장된 알림  ", padding=(10, 8))
        list_frame.pack(fill="both", expand=True, padx=14, pady=(4, 6))

        cols = ("time", "message", "before", "status")
        self.tree = ttk.Treeview(list_frame, columns=cols, show="headings",
                                 selectmode="browse", height=10)
        self.tree.heading("time", text="시간")
        self.tree.heading("message", text="알림 내용")
        self.tree.heading("before", text="사전 알림")
        self.tree.heading("status", text="상태")
        self.tree.column("time", width=70, anchor="center")
        self.tree.column("message", width=320)
        self.tree.column("before", width=90, anchor="center")
        self.tree.column("status", width=70, anchor="center")

        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # 더블클릭 → 수정 로드
        self.tree.bind("<Double-1>", lambda _: self._load_for_edit())

        # ── 수정/삭제 버튼 ──
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=14, pady=(0, 14))
        ttk.Button(btn_frame, text="수정", command=self._load_for_edit, width=8).pack(side="left", padx=(0, 6))
        ttk.Button(btn_frame, text="삭제", command=self._delete_alert, width=8).pack(side="left")

        # 상태바 (다음 알림 카운트다운)
        self.status_var = tk.StringVar(value="저장된 알림 없음")
        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                               foreground="#555", anchor="center",
                               font=("Helvetica", 12, "bold"))
        status_bar.pack(fill="x", padx=14, pady=(2, 8))

    # ── 음성 선택 헬퍼 ───────────────────────────────────────────────────────

    def _selected_voice(self) -> str:
        label = self.voice_var.get()
        for lbl, name in KO_VOICES:
            if lbl == label:
                return name
        return TTS_VOICE

    def _preview_voice(self):
        voice = self._selected_voice()
        threading.Thread(
            target=lambda: subprocess.Popen(["say", "-v", voice, f"안녕하세요. 저는 {voice}입니다."]),
            daemon=True
        ).start()

    # ── CRUD ─────────────────────────────────────────────────────────────────

    def _submit(self):
        try:
            hour = int(self.hour_var.get() or 0)
            minute = int(self.min_var.get() or 0)
            before = int(self.before_var.get() or 0)
        except ValueError:
            messagebox.showwarning("입력 오류", "시간 값이 올바르지 않습니다.", parent=self.root)
            return

        message = self.message_var.get().strip()
        if not message:
            messagebox.showwarning("입력 오류", "알림 내용을 입력하세요.", parent=self.root)
            return

        alert = {
            "time": f"{hour:02d}:{minute:02d}",
            "message": message,
            "before": before,
            "voice": self._selected_voice(),
            "last_notified_date": "",
            "last_pre_notified_date": "",
        }

        with self._lock:
            if self.editing_index is not None:
                self.alerts[self.editing_index] = alert
            else:
                self.alerts.append(alert)
            save_alerts(self.alerts)

        if self.editing_index is not None:
            self._cancel_edit()
        self._refresh_list()
        self.message_var.set("")
        self.before_var.set("0")

    def _load_for_edit(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("선택 오류", "수정할 알림을 선택하세요.", parent=self.root)
            return
        idx = self.tree.index(sel[0])
        alert = self.alerts[idx]
        h, m = alert["time"].split(":")
        self.hour_var.set(h)
        self.min_var.set(m)
        self.message_var.set(alert["message"])
        self.before_var.set(str(alert["before"]))
        # 저장된 음성 복원
        saved_voice = alert.get("voice", TTS_VOICE)
        for label, name in KO_VOICES:
            if name == saved_voice:
                self.voice_var.set(label)
                break
        self.editing_index = idx
        self.submit_btn.config(text="수정 완료")
        self.cancel_btn.grid()

    def _cancel_edit(self):
        self.editing_index = None
        self.submit_btn.config(text="추가")
        self.cancel_btn.grid_remove()
        self.message_var.set("")
        self.before_var.set("0")

    def _delete_alert(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("선택 오류", "삭제할 알림을 선택하세요.", parent=self.root)
            return
        idx = self.tree.index(sel[0])
        if messagebox.askyesno("삭제 확인",
                               f"'{self.alerts[idx]['message']}' 알림을 삭제할까요?",
                               parent=self.root):
            with self._lock:
                self.alerts.pop(idx)
                save_alerts(self.alerts)
            self._refresh_list()
            if self.editing_index == idx:
                self._cancel_edit()

    def _refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for alert in self.alerts:
            before_text = f"{alert['before']}분 전" if alert["before"] > 0 else "-"
            today = datetime.now().strftime("%Y-%m-%d")
            status = "완료" if alert.get("last_notified_date") == today else "대기"
            self.tree.insert("", "end", values=(
                alert["time"], alert["message"], before_text, status
            ))

    # ── 알림 체크 루프 ────────────────────────────────────────────────────────

    def _start_checker(self):
        t = threading.Thread(target=self._check_loop, daemon=True)
        t.start()

    def _update_countdown(self):
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")

        with self._lock:
            alerts_snap = [dict(a) for a in self.alerts]

        pending = []
        for alert in alerts_snap:
            # 오늘 아직 안 울린 알림만
            if alert.get("last_notified_date") == today:
                continue
            alert_h, alert_m = map(int, alert["time"].split(":"))
            fire_dt = now.replace(hour=alert_h, minute=alert_m,
                                  second=0, microsecond=0)
            if fire_dt <= now:
                fire_dt += timedelta(days=1)
            pending.append((fire_dt, alert))

        if not pending:
            self.status_var.set("예정된 알림 없음")
        else:
            pending.sort(key=lambda x: x[0])
            next_dt, next_alert = pending[0]
            diff = int((next_dt - now).total_seconds())
            h, rem = divmod(diff, 3600)
            m, s = divmod(rem, 60)
            if h > 0:
                countdown = f"{h}시간 {m:02d}분 {s:02d}초"
            elif m > 0:
                countdown = f"{m}분 {s:02d}초"
            else:
                countdown = f"{s}초"
            self.status_var.set(
                f"다음 알림 → {next_alert['time']}  \"{next_alert['message']}\"  |  {countdown} 후"
            )

        # 1초마다 갱신
        self.root.after(1000, self._update_countdown)

    def _check_loop(self):
        while True:
            now = datetime.now()
            to_notify: list[tuple] = []
            changed = False

            with self._lock:
                for alert in self.alerts:
                    alert_h, alert_m = map(int, alert["time"].split(":"))

                    # ── 메인 알림 발화 시각 (오늘 날짜 기준) ──
                    main_dt = now.replace(hour=alert_h, minute=alert_m,
                                          second=0, microsecond=0)
                    main_date = main_dt.strftime("%Y-%m-%d")

                    # ── 본 알림: 정수 (hour, minute) 비교 ──
                    if (now.hour == alert_h and now.minute == alert_m
                            and alert.get("last_notified_date") != main_date):
                        alert["last_notified_date"] = main_date
                        changed = True
                        to_notify.append((
                            alert["message"], False, 0,
                            alert.get("voice", TTS_VOICE)
                        ))

                    # ── 사전 알림 ──
                    if alert["before"] > 0:
                        # timedelta 뺄셈으로 자정 경계 자동 처리
                        pre_dt = main_dt - timedelta(minutes=alert["before"])
                        # 사이클 기준은 메인 알림 날짜로 통일
                        # (예: 00:05 알림 10분 전 → 23:55 발화, 기준은 익일)
                        cycle_date = main_date

                        if (now.hour == pre_dt.hour and now.minute == pre_dt.minute
                                and alert.get("last_pre_notified_date") != cycle_date
                                and alert.get("last_notified_date") != cycle_date):
                            alert["last_pre_notified_date"] = cycle_date
                            changed = True
                            to_notify.append((
                                alert["message"], True, alert["before"],
                                alert.get("voice", TTS_VOICE)
                            ))

                if changed:
                    alerts_to_save = [dict(a) for a in self.alerts]

            # ── Lock 해제 후: I/O 및 스레드 생성 ──
            if changed:
                save_alerts(alerts_to_save)
                self.root.after(0, self._refresh_list)

            for args in to_notify:
                threading.Thread(target=notify, args=args, daemon=True).start()

            time.sleep(1)


# ── 진입점 ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceAlertApp(root)
    root.mainloop()
