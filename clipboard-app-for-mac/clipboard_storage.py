#!/usr/bin/env python3
"""
Clipboard storage module for managing clipboard history
"""

import sqlite3
import hashlib
from typing import List, Dict
from utils import get_database_path


class ClipboardStorage:
    """Manages clipboard history storage with SQLite database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            self.db_path = str(get_database_path())
        else:
            self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create clipboard entries table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clipboard_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                content_hash TEXT UNIQUE NOT NULL,
                preview TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                size_bytes INTEGER NOT NULL,
                content_type TEXT DEFAULT 'text'
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON clipboard_entries(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON clipboard_entries(content_hash)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_type ON clipboard_entries(content_type)')
        
        conn.commit()
        conn.close()
        
    def add_clipboard_entry(self, content: str) -> bool:
        """Add a new clipboard entry"""
        if not content or not content.strip():
            return False
            
        content_hash = hashlib.md5(content.encode('utf-8')).hexdigest()
        preview = self._create_preview(content)
        size_bytes = len(content.encode('utf-8'))
        content_type = self._detect_content_type(content)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if content already exists
            cursor.execute('SELECT id FROM clipboard_entries WHERE content_hash = ?', (content_hash,))
            existing = cursor.fetchone()
            
            if existing:
                # Update timestamp if content already exists
                cursor.execute('UPDATE clipboard_entries SET timestamp = CURRENT_TIMESTAMP WHERE id = ?', (existing[0],))
            else:
                # Insert new entry
                cursor.execute('''
                    INSERT INTO clipboard_entries (content, content_hash, preview, size_bytes, content_type)
                    VALUES (?, ?, ?, ?, ?)
                ''', (content, content_hash, preview, size_bytes, content_type))
                
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding clipboard entry: {e}")
            return False
            
    def get_all_entries(self, limit: int = 1000) -> List[Dict]:
        """Get all clipboard entries, most recent first"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, content, preview, timestamp, size_bytes, content_type
                FROM clipboard_entries
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'content': row[1],
                    'preview': row[2],
                    'timestamp': row[3],
                    'size_bytes': row[4],
                    'content_type': row[5]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Error getting clipboard entries: {e}")
            return []
            
    def search_entries(self, query: str, limit: int = 100) -> List[Dict]:
        """Search clipboard entries by content"""
        if not query or not query.strip():
            return self.get_all_entries(limit)
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, content, preview, timestamp, size_bytes, content_type
                FROM clipboard_entries
                WHERE content LIKE ? OR preview LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'content': row[1],
                    'preview': row[2],
                    'timestamp': row[3],
                    'size_bytes': row[4],
                    'content_type': row[5]
                }
                for row in rows
            ]
            
        except Exception as e:
            print(f"Error searching clipboard entries: {e}")
            return []
            
    def update_entry_content(self, entry_id: int, new_content: str) -> bool:
        """Update the content of a specific clipboard entry"""
        if not new_content or not new_content.strip():
            return False
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get the old entry to calculate new values
            cursor.execute('SELECT content FROM clipboard_entries WHERE id = ?', (entry_id,))
            old_entry = cursor.fetchone()
            
            if not old_entry:
                conn.close()
                return False
                
            # Calculate new values
            new_content_hash = hashlib.md5(new_content.encode('utf-8')).hexdigest()
            new_preview = self._create_preview(new_content)
            new_size_bytes = len(new_content.encode('utf-8'))
            new_content_type = self._detect_content_type(new_content)
            
            # Update the entry
            cursor.execute('''
                UPDATE clipboard_entries 
                SET content = ?, content_hash = ?, preview = ?, size_bytes = ?, content_type = ?
                WHERE id = ?
            ''', (new_content, new_content_hash, new_preview, new_size_bytes, new_content_type, entry_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating entry content: {e}")
            return False
            
    def get_entry_by_id(self, entry_id: int) -> Dict:
        """Get a specific clipboard entry by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, content, preview, timestamp, size_bytes, content_type
                FROM clipboard_entries
                WHERE id = ?
            ''', (entry_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'content': row[1],
                    'preview': row[2],
                    'timestamp': row[3],
                    'size_bytes': row[4],
                    'content_type': row[5]
                }
            return None
            
        except Exception as e:
            print(f"Error getting entry by ID: {e}")
            return None
            
    def delete_entry(self, entry_id: int) -> bool:
        """Delete a specific clipboard entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM clipboard_entries WHERE id = ?', (entry_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error deleting entry: {e}")
            return False
            
    def clear_all_entries(self) -> bool:
        """Clear all clipboard entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM clipboard_entries')
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error clearing entries: {e}")
            return False
            
    def get_total_entries(self) -> int:
        """Get total number of clipboard entries"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM clipboard_entries')
            count = cursor.fetchone()[0]
            
            conn.close()
            return count
            
        except Exception as e:
            print(f"Error getting entry count: {e}")
            return 0
            
    def get_storage_size_mb(self) -> float:
        """Get total storage size used in MB"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT SUM(size_bytes) FROM clipboard_entries')
            total_bytes = cursor.fetchone()[0] or 0
            
            conn.close()
            return total_bytes / (1024 * 1024)
            
        except Exception as e:
            print(f"Error getting storage size: {e}")
            return 0.0
            
    def _create_preview(self, content: str, max_length: int = 50) -> str:
        """Create a preview of the clipboard content"""
        if len(content) <= max_length:
            return content
            
        # Try to find a good break point
        preview = content[:max_length]
        last_space = preview.rfind(' ')
        
        if last_space > max_length * 0.7:  # If we can break at a reasonable point
            preview = preview[:last_space]
            
        return preview + "..."
        
    def _detect_content_type(self, content: str) -> str:
        """Detect the type of clipboard content"""
        if content.startswith('http://') or content.startswith('https://'):
            return 'url'
        elif content.startswith('file://'):
            return 'file'
        elif len(content.splitlines()) > 1:
            return 'multiline'
        else:
            return 'text'
            
    def close(self):
        """Close database connections"""
        pass  # SQLite handles this automatically
