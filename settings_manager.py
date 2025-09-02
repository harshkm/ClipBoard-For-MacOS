#!/usr/bin/env python3
"""
Settings management module for the clipboard manager
"""

import json
import os
from typing import Any, Dict, Optional
from utils import get_settings_path


class SettingsManager:
    """Manages application settings and preferences"""
    
    def __init__(self, config_file: str = None):
        if config_file is None:
            self.config_file = str(get_settings_path())
        else:
            self.config_file = config_file
        self.default_settings = {
            'max_entries': 10000,
            'max_content_size_mb': 100,
            'auto_start': False,
            'minimize_to_tray': True,
            'check_interval_ms': 500,
            'enable_notifications': True,
            'theme': 'system',
            'font_size': 12,
            'window_width': 1200,
            'window_height': 800,
            'splitter_position': [400, 800],
            'recent_searches': [],
            'favorite_entries': []
        }
        self.settings = self.load_settings()
        
    def load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create with defaults"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_settings = json.load(f)
                    
                # Merge with defaults to ensure all keys exist
                settings = self.default_settings.copy()
                settings.update(loaded_settings)
                return settings
            else:
                # Create default settings file
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
                
        except Exception as e:
            print(f"Error loading settings: {e}")
            return self.default_settings.copy()
            
    def save_settings(self, settings: Optional[Dict[str, Any]] = None) -> bool:
        """Save current settings to file"""
        if settings is None:
            settings = self.settings
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(settings, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
            
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        return self.settings.get(key, default)
        
    def set_setting(self, key: str, value: Any) -> bool:
        """Set a specific setting value"""
        try:
            self.settings[key] = value
            return self.save_settings()
        except Exception as e:
            print(f"Error setting setting {key}: {e}")
            return False
            
    def reset_to_defaults(self) -> bool:
        """Reset all settings to default values"""
        try:
            self.settings = self.default_settings.copy()
            return self.save_settings()
        except Exception as e:
            print(f"Error resetting settings: {e}")
            return False
            
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings"""
        return self.settings.copy()
        
    def update_multiple_settings(self, updates: Dict[str, Any]) -> bool:
        """Update multiple settings at once"""
        try:
            self.settings.update(updates)
            return self.save_settings()
        except Exception as e:
            print(f"Error updating multiple settings: {e}")
            return False
            
    def add_recent_search(self, search_term: str) -> bool:
        """Add a search term to recent searches"""
        if not search_term or not search_term.strip():
            return False
            
        recent_searches = self.settings.get('recent_searches', [])
        
        # Remove if already exists
        if search_term in recent_searches:
            recent_searches.remove(search_term)
            
        # Add to beginning
        recent_searches.insert(0, search_term)
        
        # Keep only last 20 searches
        recent_searches = recent_searches[:20]
        
        self.settings['recent_searches'] = recent_searches
        return self.save_settings()
        
    def add_favorite_entry(self, entry_id: int) -> bool:
        """Add an entry to favorites"""
        favorites = self.settings.get('favorite_entries', [])
        
        if entry_id not in favorites:
            favorites.append(entry_id)
            self.settings['favorite_entries'] = favorites
            return self.save_settings()
            
        return True
        
    def remove_favorite_entry(self, entry_id: int) -> bool:
        """Remove an entry from favorites"""
        favorites = self.settings.get('favorite_entries', [])
        
        if entry_id in favorites:
            favorites.remove(entry_id)
            self.settings['favorite_entries'] = favorites
            return self.save_settings()
            
        return True
        
    def is_favorite(self, entry_id: int) -> bool:
        """Check if an entry is in favorites"""
        favorites = self.settings.get('favorite_entries', [])
        return entry_id in favorites
