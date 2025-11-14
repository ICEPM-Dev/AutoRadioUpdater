import json
import os
from pathlib import Path
from typing import List, Dict, Any


class ConfigManager:
    """Manager for radio program configuration"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            # Default config file path
            self.config_file = Path(__file__).parent.parent / "config" / "radio_programs.json"
        else:
            self.config_file = Path(config_file)
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Config file not found: {self.config_file}")
                return self._get_default_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "radio_programs": [],
            "settings": {
                "download_directory": "programas",
                "max_episodes_per_program": 5,
                "cleanup_old_files": True,
                "cleanup_days": 30
            }
        }
    
    def save_config(self):
        """Save current configuration to file"""
        try:
            # Create config directory if it doesn't exist
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            print(f"Configuration saved to {self.config_file}")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_enabled_programs(self) -> List[Dict[str, Any]]:
        """Get list of enabled radio programs"""
        return [
            program for program in self.config.get("radio_programs", [])
            if program.get("enabled", True)
        ]
    
    def get_all_programs(self) -> List[Dict[str, Any]]:
        """Get all radio programs"""
        return self.config.get("radio_programs", [])
    
    def add_program(self, name: str, url: str, description: str = "", enabled: bool = True):
        """Add a new radio program"""
        new_program = {
            "name": name,
            "url": url,
            "enabled": enabled,
            "description": description
        }
        
        if "radio_programs" not in self.config:
            self.config["radio_programs"] = []
        
        self.config["radio_programs"].append(new_program)
        self.save_config()
    
    def remove_program(self, name: str):
        """Remove a radio program by name"""
        if "radio_programs" in self.config:
            self.config["radio_programs"] = [
                program for program in self.config["radio_programs"]
                if program.get("name") != name
            ]
            self.save_config()
    
    def enable_program(self, name: str):
        """Enable a radio program"""
        self._set_program_status(name, True)
    
    def disable_program(self, name: str):
        """Disable a radio program"""
        self._set_program_status(name, False)
    
    def _set_program_status(self, name: str, enabled: bool):
        """Set program enabled status"""
        for program in self.config.get("radio_programs", []):
            if program.get("name") == name:
                program["enabled"] = enabled
                self.save_config()
                break
    
    def get_setting(self, key: str, default=None):
        """Get a setting value"""
        return self.config.get("settings", {}).get(key, default)
    
    def set_setting(self, key: str, value):
        """Set a setting value"""
        if "settings" not in self.config:
            self.config["settings"] = {}
        
        self.config["settings"][key] = value
        self.save_config()
    
    def get_download_directory(self) -> str:
        """Get download directory"""
        return self.get_setting("download_directory", "programas")
    
    def get_max_episodes_per_program(self) -> int:
        """Get maximum episodes per program"""
        return self.get_setting("max_episodes_per_program", 5)
    
    def should_cleanup_old_files(self) -> bool:
        """Check if old files should be cleaned up"""
        return self.get_setting("cleanup_old_files", True)
    
    def get_cleanup_days(self) -> int:
        """Get number of days after which files should be cleaned up"""
        return self.get_setting("cleanup_days", 30)
