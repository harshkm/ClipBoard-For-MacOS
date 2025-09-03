#!/usr/bin/env python3
"""
Utility functions for the clipboard manager
"""

import os
from pathlib import Path
from typing import Optional
from PySide6.QtGui import QIcon

def get_data_directory() -> Path:
    """Get the application data directory for ForeverClipboard"""
    # Use Application Support directory on macOS
    app_support = Path.home() / "Library" / "Application Support" / "ForeverClipboard"
    app_support.mkdir(parents=True, exist_ok=True)
    return app_support


def get_database_path() -> Path:
    """Get the database file path"""
    data_dir = get_data_directory()
    return data_dir / "clipboard_history.db"


def get_log_path() -> Path:
    """Get the log file path"""
    data_dir = get_data_directory()
    logs_dir = data_dir / "logs"
    logs_dir.mkdir(exist_ok=True)
    return logs_dir / "clipboard_manager.log"


def get_settings_path() -> Path:
    """Get the settings file path"""
    data_dir = get_data_directory()
    return data_dir / "settings.json"


def format_clipboard_content(content: str, max_length: int = 100) -> str:
    """Format clipboard content for display"""
    if not content:
        return ""
        
    # Remove extra whitespace
    content = content.strip()
    
    # Handle very long content
    if len(content) > max_length:
        # Try to break at word boundary
        truncated = content[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > max_length * 0.7:
            truncated = truncated[:last_space]
            
        return truncated + "..."
        
    return content


def get_file_icon(file_path: str) -> Optional[QIcon]:
    """Get appropriate icon for file type"""
    if not file_path or not os.path.exists(file_path):
        return None
        
    # Get file extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Define icon mappings for common file types
    icon_mappings = {
        '.txt': '📄',
        '.py': '🐍',
        '.js': '📜',
        '.html': '🌐',
        '.css': '🎨',
        '.json': '📋',
        '.xml': '📄',
        '.csv': '📊',
        '.pdf': '📕',
        '.doc': '📘',
        '.docx': '📘',
        '.xls': '📊',
        '.xlsx': '📊',
        '.ppt': '��️',
        '.pptx': '📽️',
        '.jpg': '🖼️',
        '.jpeg': '🖼️',
        '.png': '🖼️',
        '.gif': '🎬',
        '.mp4': '🎥',
        '.mp3': '🎵',
        '.zip': '📦',
        '.tar': '📦',
        '.gz': '📦',
        '.exe': '⚙️',
        '.app': '📱'
    }
    
    # Return emoji as text for now (you can replace with actual icons)
    return icon_mappings.get(ext, '📄')


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp for display"""
    try:
        from datetime import datetime
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        now = datetime.now()
        
        # Calculate time difference
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days != 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours != 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
        else:
            return "Just now"
            
    except Exception:
        return timestamp_str


def is_binary_content(content: str) -> bool:
    """Check if content appears to be binary"""
    if not content:
        return False
        
    # Check for null bytes or control characters
    try:
        content.encode('utf-8')
        return False
    except UnicodeEncodeError:
        return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe saving"""
    import re
    
    # Remove or replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "clipboard_content"
        
    return filename


def get_content_preview(content: str, max_length: int = 100) -> str:
    """Get a preview of content with smart truncation"""
    if not content:
        return ""
        
    # Remove extra whitespace
    content = content.strip()
    
    if len(content) <= max_length:
        return content
        
    # Try to break at word boundary
    truncated = content[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.7:
        truncated = truncated[:last_space]
        
    return truncated + "..."