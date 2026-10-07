import json
import tkinter as tk
from tkinter import ttk, colorchooser
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
from enum import Enum


class AimMode(Enum):
    OFF = "OFF"
    SILENT = "SILENT"
    VISIBLE = "VISIBLE"
    LOCK = "LOCK"


class ESPMode(Enum):
    DISABLED = "DISABLED"
    BOXES = "BOXES"
    SKELETON = "SKELETON"
    FULL = "FULL"


@dataclass
class ColorSpec:
    r: int = 0
    g: int = 255
    b: int = 128
    a: int = 200

    def to_hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_rgb_tuple(self) -> Tuple[int, int, int]:
        return (self.r, self.g, self.b)


@dataclass
class CheatSettings:
    esp_enabled: bool = True
    esp_mode: str = ESPMode.BOXES.value
    esp_color: Dict = None
    aim_enabled: bool = False
    aim_mode: str = AimMode.SILENT.value
    aim_color: Dict = None
    ui_color: Dict = None
    aim_fov: float = 45.0
    aim_smooth: float = 0.80
    esp_distance: float = 500.0
    detect_distance: float = 1000.0
    ui_scale: float = 1.0

    def __post_init__(self):
        if self.esp_color is None:
            self.esp_color = {"r": 0, "g": 255, "b": 120, "a": 200}
        if self.aim_color is None:
            self.aim_color = {"r": 255, "g": 50, "b": 50, "a": 200}
        if self.ui_color is None:
            self.ui_color = {"r": 80, "g": 170, "b": 255, "a": 220}


class GameMenuDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum UI")
        self.root.geometry("760x520")
        self.root.configure(bg="#0d1117")

        self.settings = CheatSettings()
        self.player_samples = [
            {"name": "Player 1", "health": 92, "distance": 230},
            {"name": "Player 2", "health": 74, "distance": 410},
            {"name": "Player 3", "health": 55, "distance": 680},
        ]

        self._build_theme()
        self._build_ui()
        self.refresh_preview()

    def _build_theme(self):
        self.bg = "#0d1117"
        self.panel = "#151b23"
        self.panel_alt = "#1b2430"
        self.accent = "#5aa9ff"
        self.accent2 = "#4af0b5"
        self.alert = "#ff5b5b"
        self.text = "#e6edf3"
        self.muted = "#8b949e"

    def _build_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)

        outer = tk.Frame(self.root, bg=self.bg)
        outer.pack(fill="both", expand=True, padx=16, pady=16)

        title = tk.Label(
            outer,
            text="QUANTUM UI",
            fg=self.accent2,
            bg=self.bg,
            font=("Segoe UI", 22, "bold"),
        )
        title.pack(anchor="w", pady=(6, 10))

        content = tk.Frame(outer, bg=self.bg)
        content.pack(fill="both", expand=True)

        left = tk.Frame(content, bg=self.panel, padx=16, pady=14)
        left.pack(side="left", fill="y", padx=(0, 12), ipadx=8, ipady=8)
        left.configure(highlightbackground="#2a3644", highlightthickness=1)

        right = tk.Frame(content, bg=self.panel, padx=16, pady=14)
        right.pack(side="left", fill="both", expand=True, ipadx=8, ipady=8)
        right.configure(highlightbackground="#2a3644", highlightthickness=1)

        self._build_switches(left)
        self._build_sliders(right)

    def _build_switches(self, parent):
        section = tk.LabelFrame(
            parent,
            text=" Toggles ",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 11, "bold"),
            bd=1,
            highlightbackground="#2a3644",
            highlightthickness=1,
        )
        section.pack(fill="x", pady=(0, 12))

        self.esp_var = tk.BooleanVar(value=self.settings.esp_enabled)
        self.aim_var = tk.BooleanVar(value=self.settings.aim_enabled)

        def toggle_row(frame, label, var, command):
            row = tk.Frame(frame, bg=self.panel)
            row.pack(fill="x", pady=6)
            tk.Label(row, text=label, fg=self.text, bg=self.panel, font=("Segoe UI", 10)).pack(side="left")
            tk.Checkbutton(row, variable=var, command=command, bg=self.panel, activebackground=self.panel, fg=self.text, selectcolor="#0f1720").pack(side="right")

        toggle_row(section, "ESP", self.esp_var, self.toggle_esp)
        toggle_row(section, "AIM", self.aim_var, self.toggle_aim)

        self.mode_box = ttk.Combobox(section, values=[m.value for m in ESPMode], state="readonly", width=12)
        self.mode_box.set(self.settings.esp_mode)
        self.mode_box.pack(fill="x", pady=(10, 6))
        self.mode_box.bind("<<ComboboxSelected>>", self.apply_esp_mode)

        self.aim_mode_box = ttk.Combobox(section, values=[m.value for m in AimMode], state="readonly", width=12)
        self.aim_mode_box.set(self.settings.aim_mode)
        self.aim_mode_box.pack(fill="x", pady=(4, 6))
        self.aim_mode_box.bind("<<ComboboxSelected>>", self.apply_aim_mode)

        color_btn_frame = tk.Frame(section, bg=self.panel)
        color_btn_frame.pack(fill="x", pady=(10, 0))
        tk.Button(color_btn_frame, text="ESP Color", command=lambda: self.pick_color("esp"), bg="#1c2632", fg=self.text, activebackground="#2a3644", bd=0, padx=10, pady=6).pack(side="left", expand=True, fill="x", padx=(0, 6))
        tk.Button(color_btn_frame, text="Aim Color", command=lambda: self.pick_color("aim"), bg="#1c2632", fg=self.text, activebackground="#2a3644", bd=0, padx=10, pady=6).pack(side="left", expand=True, fill="x", padx=(6, 0))

    def _build_sliders(self, parent):
        section = tk.LabelFrame(
            parent,
            text=" Visuals / Tuning ",
            bg=self.panel,
            fg=self.text,
            font=("Segoe UI", 11, "bold"),
            bd=1,
            highlightbackground="#2a3644",
            highlightthickness=1,
        )
        section.pack(fill="both", expand=True)

        self.slider_vars = {}
        config_rows = [
            ("FOV", "aim_fov", 10, 180, 45),
            ("Smoothing", "aim_smooth", 0.0, 1.0, 0.8),
            ("ESP Distance", "esp_distance", 100, 1500, 500),
            ("Detect Distance", "detect_distance", 100, 2000, 1000),
        ]

        for label, key, low, high, default in config_rows:
            row = tk.Frame(section, bg=self.panel)
            row.pack(fill="x", pady=8)

            tk.Label(row, text=label, fg=self.text, bg=self.panel, width=14, anchor="w", font=("Segoe UI", 10)).pack(side="left")

            scale = tk.Scale(
                row,
                from_=low,
                to=high,
                orient="horizontal",
                resolution=0.1 if key == "aim_smooth" else 1,
                bg=self.panel,
                fg=self.text,
                highlightbackground=self.panel,
                activebackground=self.accent,
                troughcolor="#111827",
                length=260,
                command=lambda val, k=key: self.update_numeric(k, val),
            )
            scale.set(default)
            scale.pack(side="right")
            self.slider_vars[key] = scale

        self.preview = tk.Text(
            parent,
            height=12,
            bg="#0d1117",
            fg="#daf3ff",
            insertbackground="#daf3ff",
            font=("Consolas", 10),
            wrap="word",
            bd=0,
            padx=12,
            pady=12,
        )
        self.preview.pack(fill="both", expand=True, pady=(16, 0))

    def update_numeric(self, key, value):
        value = float(value)
        if key == "aim_fov":
            self.settings.aim_fov = value
        elif key == "aim_smooth":
            self.settings.aim_smooth = value
        elif key == "esp_distance":
            self.settings.esp_distance = value
        elif key == "detect_distance":
            self.settings.detect_distance = value
        self.refresh_preview()

    def toggle_esp(self):
        self.settings.esp_enabled = self.esp_var.get()
        self.refresh_preview()

    def toggle_aim(self):
        self.settings.aim_enabled = self.aim_var.get()
        self.refresh_preview()

    def apply_esp_mode(self, event=None):
        selected = self.mode_box.get()
        self.settings.esp_mode = selected
        self.refresh_preview()

    def apply_aim_mode(self, event=None):
        selected = self.aim_mode_box.get()
        self.settings.aim_mode = selected
        self.refresh_preview()

    def pick_color(self, target):
        current = self.settings.esp_color if target == "esp" else self.settings.aim_color
        rgb = (current["r"], current["g"], current["b"])
        color = colorchooser.askcolor(color=rgb, title=f"Choose {target.upper()} color")
        if color and color[0] is not None:
            r, g, b = [int(v) for v in color[0]]
            if target == "esp":
                self.settings.esp_color = {"r": r, "g": g, "b": b, "a": 200}
            else:
                self.settings.aim_color = {"r": r, "g": g, "b": b, "a": 200}
            self.refresh_preview()

    def refresh_preview(self):
        esp_status = "ON" if self.settings.esp_enabled else "OFF"
        aim_status = "ON" if self.settings.aim_enabled else "OFF"

        lines = [
            "╔════════════════════════════════════╗",
            "║       QUANTUM MENU PREVIEW       ║",
            "╠════════════════════════════════════╣",
            f"║ ESP: {esp_status:<16}            ║",
            f"║ Mode: {self.settings.esp_mode:<14}      ║",
            f"║ Aim: {aim_status:<16}            ║",
            f"║ Mode: {self.settings.aim_mode:<14}      ║",
            f"║ FOV: {self.settings.aim_fov:>6.1f}°{'':<13} ║",
            f"║ Smoothing: {self.settings.aim_smooth:>4.2f}{'':<13} ║",
            f"║ ESP Color: {self._hex(self.settings.esp_color):<12} ║",
            f"║ Aim Color: {self._hex(self.settings.aim_color):<12} ║",
            "╠════════════════════════════════════╣",
            "║ Detected players                  ║",
            "║  [████████] Player 1  230m         ║",
            "║  [████████] Player 2  410m         ║",
            "║  [█████░░░░] Player 3  680m         ║",
            "╚════════════════════════════════════╝",
        ]
        self.preview.delete("1.0", tk.END)
        self.preview.insert(tk.END, "\n".join(lines))

    def _hex(self, color):
        return f"#{color['r']:02x}{color['g']:02x}{color['b']:02x}"

    def save_config(self, path="cheat_config.json"):
        payload = {
            "settings": {
                "esp_enabled": self.settings.esp_enabled,
                "esp_mode": self.settings.esp_mode,
                "esp_color": self.settings.esp_color,
                "aim_enabled": self.settings.aim_enabled,
                "aim_mode": self.settings.aim_mode,
                "aim_color": self.settings.aim_color,
                "aim_fov": self.settings.aim_fov,
                "aim_smooth": self.settings.aim_smooth,
                "esp_distance": self.settings.esp_distance,
                "detect_distance": self.settings.detect_distance,
            }
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)


def main():
    root = tk.Tk()
    app = GameMenuDemo(root)
    root.mainloop()


if __name__ == "__main__":
    main()
