"""
Advanced Cheat Menu System with ESP, Aim Assist, and Customizable UI
Supports: ESP Detection, Silent Aim, Lock Features, and Real-time Settings
"""

import json
from dataclasses import dataclass, asdict
from typing import Dict, List, Tuple
from enum import Enum
from datetime import datetime


class AimMode(Enum):
    """Aim assist modes"""
    OFF = "OFF"
    SILENT = "SILENT"
    VISIBLE = "VISIBLE"
    LOCK = "LOCK"


class ESPMode(Enum):
    """ESP detection modes"""
    DISABLED = "DISABLED"
    BOXES = "BOXES"
    SKELETON = "SKELETON"
    FULL = "FULL"


@dataclass
class Color:
    """RGBA Color representation"""
    r: int
    g: int
    b: int
    a: int = 255

    def to_hex(self) -> str:
        """Convert to hex color"""
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_rgb(self) -> Tuple[int, int, int]:
        """Convert to RGB tuple"""
        return (self.r, self.g, self.b)

    def to_rgba(self) -> Tuple[int, int, int, int]:
        """Convert to RGBA tuple"""
        return (self.r, self.g, self.b, self.a)


@dataclass
class CheatSettings:
    """Main cheat configuration"""
    # ESP Settings
    esp_enabled: bool = True
    esp_mode: ESPMode = ESPMode.BOXES
    esp_color: Color = None
    esp_distance: float = 500.0  # Max ESP render distance
    
    # Aim Settings
    aim_enabled: bool = False
    aim_mode: AimMode = AimMode.SILENT
    aim_fov: float = 45.0  # Field of view for aim assist
    aim_smooth: float = 0.8  # Smoothing factor (0-1)
    aim_lock_color: Color = None
    
    # Visual Settings
    ui_color: Color = None
    ui_opacity: float = 0.9
    ui_scale: float = 1.0
    ui_position: Tuple[int, int] = (10, 10)
    
    # Detection Settings
    detect_enemies: bool = True
    detect_teammates: bool = False
    detect_distance: float = 1000.0
    
    # Performance
    render_distance: float = 2000.0
    update_rate: float = 60.0  # Hz

    def __post_init__(self):
        """Initialize default colors"""
        if self.esp_color is None:
            self.esp_color = Color(0, 255, 0, 200)  # Green
        if self.aim_lock_color is None:
            self.aim_lock_color = Color(255, 0, 0, 200)  # Red
        if self.ui_color is None:
            self.ui_color = Color(50, 150, 255, 200)  # Blue


class CheatMenu:
    """Main cheat menu system"""

    def __init__(self):
        self.settings = CheatSettings()
        self.detected_players: List[Dict] = []
        self.is_open = True
        self.selected_option = 0
        self.menu_state = "MAIN"
        self.last_update = datetime.now()

    def detect_players(self) -> List[Dict]:
        """
        Detect players in the game world
        Returns list of player data with position, health, distance, etc.
        """
        players = []
        # This would integrate with game memory/API
        # For now, returns structured format
        return players

    def update_esp(self) -> List[Dict]:
        """Update ESP detection data"""
        if not self.settings.esp_enabled:
            return []

        players = self.detect_players()
        rendered = []

        for player in players:
            distance = player.get("distance", 0)
            
            # Check distance filters
            if distance > self.settings.esp_distance:
                continue
            
            # Check team filter
            if not self.settings.detect_enemies and player.get("is_enemy"):
                continue
            if not self.settings.detect_teammates and not player.get("is_enemy"):
                continue

            rendered.append({
                "name": player.get("name", "Unknown"),
                "health": player.get("health", 100),
                "distance": distance,
                "position": player.get("position", (0, 0, 0)),
                "mode": self.settings.esp_mode.value,
                "color": self.settings.esp_color.to_rgba(),
            })

        self.detected_players = rendered
        return rendered

    def update_aim(self, target=None) -> Dict:
        """Update aim assist system"""
        if not self.settings.aim_enabled or not target:
            return {"locked": False}

        aim_data = {
            "locked": True,
            "mode": self.settings.aim_mode.value,
            "target": target.get("name", "Unknown"),
            "smoothing": self.settings.aim_smooth,
            "fov": self.settings.aim_fov,
            "lock_color": self.settings.aim_lock_color.to_rgba(),
        }

        return aim_data

    def toggle_esp(self):
        """Toggle ESP on/off"""
        self.settings.esp_enabled = not self.settings.esp_enabled
        return f"ESP: {'ON' if self.settings.esp_enabled else 'OFF'}"

    def toggle_aim(self):
        """Toggle Aim Assist on/off"""
        self.settings.aim_enabled = not self.settings.aim_enabled
        return f"AIM: {'ON' if self.settings.aim_enabled else 'OFF'}"

    def set_esp_mode(self, mode: ESPMode):
        """Change ESP display mode"""
        self.settings.esp_mode = mode
        return f"ESP Mode: {mode.value}"

    def set_aim_mode(self, mode: AimMode):
        """Change Aim Assist mode"""
        self.settings.aim_mode = mode
        return f"Aim Mode: {mode.value}"

    def set_color(self, target: str, color: Color):
        """Set color for ESP or Aim"""
        if target == "esp":
            self.settings.esp_color = color
            return f"ESP Color: {color.to_hex()}"
        elif target == "aim":
            self.settings.aim_lock_color = color
            return f"Aim Lock Color: {color.to_hex()}"
        elif target == "ui":
            self.settings.ui_color = color
            return f"UI Color: {color.to_hex()}"
        return "Invalid target"

    def adjust_fov(self, value: float):
        """Adjust aim FOV"""
        self.settings.aim_fov = max(10.0, min(180.0, value))
        return f"FOV: {self.settings.aim_fov:.1f}°"

    def adjust_smoothing(self, value: float):
        """Adjust aim smoothing (0-1)"""
        self.settings.aim_smooth = max(0.0, min(1.0, value))
        return f"Smoothing: {self.settings.aim_smooth:.2f}"

    def adjust_distance(self, distance_type: str, value: float):
        """Adjust detection distance"""
        if distance_type == "esp":
            self.settings.esp_distance = max(100.0, value)
            return f"ESP Distance: {self.settings.esp_distance:.0f}"
        elif distance_type == "detect":
            self.settings.detect_distance = max(100.0, value)
            return f"Detect Distance: {self.settings.detect_distance:.0f}"
        return "Invalid distance type"

    def get_menu_display(self) -> str:
        """Generate menu UI string"""
        menu = []
        menu.append("╔════════════════════════════════════╗")
        menu.append("║       QUANTUM CHEAT MENU v1.0       ║")
        menu.append("╠════════════════════════════════════╣")
        menu.append(f"║ ESP: {'✓ ON' if self.settings.esp_enabled else '✗ OFF':^30} ║")
        menu.append(f"║   Mode: {self.settings.esp_mode.value:^22} ║")
        menu.append(f"║   Distance: {self.settings.esp_distance:>6.0f}m{'':<15} ║")
        menu.append(f"║   Color: {self.settings.esp_color.to_hex():^20} ║")
        menu.append("╠════════════════════════════════════╣")
        menu.append(f"║ AIM: {'✓ ON' if self.settings.aim_enabled else '✗ OFF':^29} ║")
        menu.append(f"║   Mode: {self.settings.aim_mode.value:^22} ║")
        menu.append(f"║   FOV: {self.settings.aim_fov:>6.1f}°{'':<16} ║")
        menu.append(f"║   Smoothing: {self.settings.aim_smooth:>4.2f}{'':<15} ║")
        menu.append(f"║   Lock Color: {self.settings.aim_lock_color.to_hex():^17} ║")
        menu.append("╠════════════════════════════════════╣")
        menu.append(f"║ Detected Players: {len(self.detected_players):>14} ║")
        for i, player in enumerate(self.detected_players[:3]):
            health_bar = f"[{'█' * (player['health']//10)}{'░' * (10-player['health']//10)}]"
            menu.append(f"║ {player['name'][:15]:<15} {health_bar} {player['distance']:>5.0f}m ║")
        menu.append("╠════════════════════════════════════╣")
        menu.append("║ [1] Toggle ESP     [5] Adjust FOV  ║")
        menu.append("║ [2] Toggle Aim     [6] Smoothing   ║")
        menu.append("║ [3] ESP Mode       [7] Colors      ║")
        menu.append("║ [4] Aim Mode       [0] Close Menu  ║")
        menu.append("╚════════════════════════════════════╝")
        
        return "\n".join(menu)

    def save_config(self, filename: str = "cheat_config.json"):
        """Save settings to file"""
        config = asdict(self.settings)
        # Convert Color objects to dict
        config["esp_color"] = asdict(self.settings.esp_color)
        config["aim_lock_color"] = asdict(self.settings.aim_lock_color)
        config["ui_color"] = asdict(self.settings.ui_color)
        # Convert enums to strings
        config["esp_mode"] = self.settings.esp_mode.value
        config["aim_mode"] = self.settings.aim_mode.value
        
        with open(filename, "w") as f:
            json.dump(config, f, indent=2)
        return f"Config saved to {filename}"

    def load_config(self, filename: str = "cheat_config.json"):
        """Load settings from file"""
        try:
            with open(filename, "r") as f:
                config = json.load(f)
            
            # Restore Color objects
            self.settings.esp_color = Color(**config["esp_color"])
            self.settings.aim_lock_color = Color(**config["aim_lock_color"])
            self.settings.ui_color = Color(**config["ui_color"])
            # Restore enums
            self.settings.esp_mode = ESPMode(config["esp_mode"])
            self.settings.aim_mode = AimMode(config["aim_mode"])
            
            return f"Config loaded from {filename}"
        except FileNotFoundError:
            return f"Config file {filename} not found"

    def update(self):
        """Main update loop"""
        self.update_esp()
        self.last_update = datetime.now()

    def handle_input(self, key: str) -> str:
        """Handle menu input"""
        if key == "1":
            return self.toggle_esp()
        elif key == "2":
            return self.toggle_aim()
        elif key == "3":
            return f"ESP Mode: {self.settings.esp_mode.value} → Next"
        elif key == "4":
            return f"Aim Mode: {self.settings.aim_mode.value} → Next"
        elif key == "0":
            self.is_open = False
            return "Menu closed"
        else:
            return "Invalid input"


# Example Usage
if __name__ == "__main__":
    menu = CheatMenu()
    
    # Customize colors
    menu.set_color("esp", Color(0, 255, 100, 220))  # Bright green
    menu.set_color("aim", Color(255, 50, 50, 220))  # Bright red
    menu.set_color("ui", Color(100, 200, 255, 220))  # Sky blue
    
    # Adjust settings
    menu.adjust_fov(60.0)
    menu.adjust_smoothing(0.85)
    menu.adjust_distance("esp", 750.0)
    
    # Display menu
    print(menu.get_menu_display())
    
    # Save configuration
    menu.save_config()
