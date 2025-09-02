#!/usr/bin/env python3
"""
Clipboard Manager GUI - A powerful clipboard history manager with modern interface
"""

import sys
import json
import time
import signal
import os
import tempfile
from datetime import datetime
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                               QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, 
                               QLabel, QLineEdit, QTextEdit, QSplitter,
                               QSystemTrayIcon, QMenu, QMessageBox,
                               QProgressBar, QFileDialog)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QCoreApplication
from PySide6.QtGui import QFont, QKeySequence, QShortcut, QAction
import pyperclip

# Import our existing modules
from clipboard_storage import ClipboardStorage
from settings_manager import SettingsManager


class SingleInstanceLock:
    """Prevents multiple instances of the application from running"""
    
    def __init__(self, app_name="ForeverClipboard"):
        self.app_name = app_name
        self.lock_file = os.path.join(tempfile.gettempdir(), f"{app_name}.lock")
        self.lock_acquired = False
        
    def acquire(self):
        """Try to acquire the lock"""
        try:
            # Check if lock file exists and contains a valid PID
            if os.path.exists(self.lock_file):
                try:
                    with open(self.lock_file, 'r') as f:
                        pid = int(f.read().strip())
                    
                    # Check if the process is still running
                    if self._is_process_running(pid):
                        return False  # Another instance is running
                    else:
                        # Process is dead, remove stale lock file
                        os.remove(self.lock_file)
                except (ValueError, IOError):
                    # Invalid lock file, remove it
                    os.remove(self.lock_file)
            
            # Create new lock file
            with open(self.lock_file, 'w') as f:
                f.write(str(os.getpid()))
            
            self.lock_acquired = True
            return True
            
        except Exception as e:
            print(f"Error acquiring lock: {e}")
            return False
    
    def release(self):
        """Release the lock"""
        try:
            if self.lock_acquired and os.path.exists(self.lock_file):
                os.remove(self.lock_file)
                self.lock_acquired = False
        except Exception as e:
            print(f"Error releasing lock: {e}")
    
    def _is_process_running(self, pid):
        """Check if a process with given PID is running"""
        try:
            os.kill(pid, 0)  # Signal 0 doesn't kill, just checks if process exists
            return True
        except OSError:
            return False
    
    def __enter__(self):
        return self.acquire()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()


class ClipboardMonitorThread(QThread):
    """Thread that monitors clipboard for changes"""
    
    clipboard_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.last_content = ""
        self.check_interval = 0.5  # Check every 500ms
        
    def run(self):
        """Main monitoring loop"""
        self.running = True
        self.last_content = pyperclip.paste()
        
        while self.running:
            try:
                current_content = pyperclip.paste()
                
                if current_content != self.last_content:
                    self.last_content = current_content
                    if current_content and current_content.strip():
                        self.clipboard_changed.emit(current_content)
                        
                time.sleep(self.check_interval)
                
            except Exception as e:
                print(f"Clipboard monitoring error: {e}")
                time.sleep(1)
                
    def stop(self):
        """Stop the monitoring thread safely"""
        self.running = False
        # Give the thread a moment to finish its current iteration
        if self.isRunning():
            self.wait(2000)  # Wait up to 2 seconds
            if self.isRunning():
                self.terminate()  # Force terminate if still running
                self.wait(1000)   # Wait for termination


class ClipboardManagerGUI(QMainWindow):
    """Main application window for the clipboard manager"""
    
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.storage = ClipboardStorage()
        self.monitor_thread = ClipboardMonitorThread()
        
        # Connect signals
        self.monitor_thread.clipboard_changed.connect(self.on_clipboard_changed)
        
        self.init_ui()
        self.setup_shortcuts()
        self.load_clipboard_history()
        
        # Start monitoring clipboard
        self.monitor_thread.start()
        
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_statistics)
        self.status_timer.start(5000)  # Update every 5 seconds
        
        # Setup signal handlers for graceful shutdown
        self.setup_signal_handlers()
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        # Handle SIGINT (Ctrl+C) gracefully
        signal.signal(signal.SIGINT, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        print(f"Received signal {signum}, shutting down gracefully...")
        self.cleanup_and_quit()
        
    def cleanup_and_quit(self):
        """Clean up resources and quit gracefully"""
        try:
            # Stop the status timer
            if hasattr(self, 'status_timer'):
                self.status_timer.stop()
                
            # Stop the monitor thread safely
            if hasattr(self, 'monitor_thread') and self.monitor_thread.isRunning():
                self.monitor_thread.stop()
                
            # Close storage
            if hasattr(self, 'storage'):
                self.storage.close()
                
            # Quit the application
            QCoreApplication.quit()
            
        except Exception as e:
            print(f"Error during cleanup: {e}")
            # Force quit if cleanup fails
            QCoreApplication.quit()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Forever Clipboard Pro - GUI")
        self.setGeometry(800, 600, 1200, 800)
        
        # Set window icon (if available)
        self.setWindowIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left panel - Clipboard history list
        self.create_history_panel(splitter)
        
        # Right panel - Content viewer and actions
        self.create_content_panel(splitter)
        
        # Set splitter proportions
        splitter.setSizes([400, 800])
        
        # Create system tray icon
        self.create_system_tray()
        
        # Status bar
        self.statusBar().showMessage("Ready - Monitoring clipboard...")
        
        # Apply modern styling
        self.apply_styling()
        
    def create_history_panel(self, parent):
        """Create the left panel with clipboard history"""
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search clipboard history...")
        self.search_input.textChanged.connect(self.filter_history)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #404040;
                border-radius: 8px;
                font-size: 14px;
                background: #2d2d2d;
                color: #ffffff;
            }
            QLineEdit:focus {
                border-color: #007AFF;
                background: #333333;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        # Clear button
        clear_btn = QPushButton("🗑️ Clear All")
        clear_btn.clicked.connect(self.clear_all_history)
        clear_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background: #FF3B30;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #D70015;
            }
        """)
        search_layout.addWidget(clear_btn)
        
        left_layout.addLayout(search_layout)
        
        # History list
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_item_selected)
        self.history_list.itemDoubleClicked.connect(self.on_history_item_double_clicked)
        self.history_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_list.customContextMenuRequested.connect(self.show_context_menu)
        self.history_list.setAlternatingRowColors(True)
        self.history_list.setStyleSheet("""
            QListWidget {
                border: 2px solid #404040;
                border-radius: 8px;
                background: #2d2d2d;
                color: #ffffff;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #404040;
                background: #2d2d2d;
                color: #ffffff;
            }
            QListWidget::item:selected {
                background: #007AFF;
                color: #ffffff;
            }
            QListWidget::item:alternate {
                background: #333333;
                color: #ffffff;
            }
            QListWidget::item:hover {
                background: #404040;
                color: #ffffff;
            }
        """)
        left_layout.addWidget(self.history_list)
        
        # Info label
        info_label = QLabel("💡 Double-click to copy • Right-click for copy/delete options")
        info_label.setStyleSheet("color: #ffffff; font-size: 11px; padding: 8px;")
        left_layout.addWidget(info_label)
        
        parent.addWidget(left_widget)
        
    def create_content_panel(self, parent):
        """Create the right panel with content viewer and actions"""
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Content viewer header
        content_header = QHBoxLayout()
        content_label = QLabel("📋 Clipboard Content:")
        content_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        content_label.setStyleSheet("color: #ffffff; padding: 8px;")
        content_header.addWidget(content_label)
        
        # Entry info
        self.entry_info = QLabel("No entry selected")
        self.entry_info.setStyleSheet("color: #ffffff; font-size: 12px; padding: 8px;")
        content_header.addWidget(self.entry_info)
        content_header.addStretch()
        
        right_layout.addLayout(content_header)
        
        # Content viewer
        self.content_viewer = QTextEdit()
        self.content_viewer.setReadOnly(True)
        self.content_viewer.setFont(QFont("Monaco", 11))
        self.content_viewer.setStyleSheet("""
            QTextEdit {
                border: 2px solid #404040;
                border-radius: 8px;
                background: #2d2d2d;
                color: #ffffff;
                padding: 12px;
                font-family: 'Monaco', 'Menlo', monospace;
            }
        """)
        right_layout.addWidget(self.content_viewer)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        # Add some spacing on the left
        actions_layout.addStretch()
        
        export_btn = QPushButton("📤 Export Clipboard Data")
        export_btn.clicked.connect(self.export_clipboard_data)
        export_btn.setStyleSheet("""
            QPushButton {
                padding: 12px 24px;
                background: #34C759;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #28A745;
            }
        """)
        actions_layout.addWidget(export_btn)
        
        right_layout.addLayout(actions_layout)
        
        # Statistics
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("📊 Total entries: 0 | Storage used: 0 MB")
        self.stats_label.setStyleSheet("color: #ffffff; font-size: 12px; padding: 8px;")
        stats_layout.addWidget(self.stats_label)
        
        # Progress bar for storage
        self.storage_progress = QProgressBar()
        self.storage_progress.setMaximum(100)
        self.storage_progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #404040;
                border-radius: 8px;
                text-align: center;
                background: #2d2d2d;
                color: #ffffff;
            }
            QProgressBar::chunk {
                background: #007AFF;
                border-radius: 6px;
            }
        """)
        stats_layout.addWidget(self.storage_progress)
        
        right_layout.addLayout(stats_layout)
        
        parent.addWidget(right_widget)
        
    def create_system_tray(self):
        """Create system tray icon and menu"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ComputerIcon))
        
        # Create tray menu
        tray_menu = QMenu()
        
        show_action = QAction("👁️ Show", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("🙈 Hide", self)
        hide_action.triggered.connect(self.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("🚪 Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Global shortcuts for quick access
        show_shortcut = QShortcut(QKeySequence("Ctrl+Shift+V"), self)
        show_shortcut.activated.connect(self.toggle_window)
        
        # Copy shortcut
        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        copy_shortcut.activated.connect(self.copy_selected_to_clipboard)
        
        # Search shortcut
        search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        search_shortcut.activated.connect(lambda: self.search_input.setFocus())
        
    def apply_styling(self):
        """Apply modern dark styling to the application"""
        self.setStyleSheet("""
            QMainWindow {
                background: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background: #1e1e1e;
                color: #ffffff;
            }
            QMenu {
                background: #2d2d2d;
                color: #ffffff;
                border: 1px solid #404040;
            }
            QMenu::item:selected {
                background: #007AFF;
            }
            QStatusBar {
                background: #2d2d2d;
                color: #ffffff;
            }
        """)
        
    def on_clipboard_changed(self, content: str):
        """Handle clipboard content changes"""
        if content and content.strip():
            # Add to storage
            self.storage.add_clipboard_entry(content)
            
            # Update UI
            self.load_clipboard_history()
            
            # Show notification
            self.tray_icon.showMessage(
                "Clipboard Updated",
                f"Added new entry ({len(content)} chars)",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
            
    def load_clipboard_history(self):
        """Load and display clipboard history"""
        self.history_list.clear()
        entries = self.storage.get_all_entries()
        
        for entry in entries:
            item = QListWidgetItem()
            
            # Create rich text for the item
            preview_text = entry['preview']
            if entry['content_type'] == 'url':
                preview_text = f"🌐 {preview_text}"
            elif entry['content_type'] == 'file':
                preview_text = f"📁 {preview_text}"
            elif entry['content_type'] == 'multiline':
                preview_text = f"📄 {preview_text}"
            else:
                preview_text = f"📝 {preview_text}"
                
            item.setText(preview_text)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            
            # Set tooltip with full content
            tooltip = entry['content'][:200] + "..." if len(entry['content']) > 200 else entry['content']
            item.setToolTip(tooltip)
            
            self.history_list.addItem(item)
            
        # Update statistics
        self.update_statistics()
        
    def filter_history(self, search_text: str):
        """Filter clipboard history based on search text"""
        if not search_text:
            self.load_clipboard_history()
            return
            
        self.history_list.clear()
        entries = self.storage.search_entries(search_text)
        
        for entry in entries:
            item = QListWidgetItem()
            preview_text = entry['preview']
            if entry['content_type'] == 'url':
                preview_text = f"🌐 {preview_text}"
            elif entry['content_type'] == 'file':
                preview_text = f"📁 {preview_text}"
            elif entry['content_type'] == 'multiline':
                preview_text = f"📄 {preview_text}"
            else:
                preview_text = f"📝 {preview_text}"
                
            item.setText(preview_text)
            item.setData(Qt.ItemDataRole.UserRole, entry)
            self.history_list.addItem(item)
            
    def on_history_item_selected(self, item: QListWidgetItem):
        """Handle history item selection"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry:
            self.content_viewer.setText(entry['content'])
            
            # Update entry info
            timestamp = entry['timestamp']
            size_kb = entry['size_bytes'] / 1024
            self.entry_info.setText(f"📅 {timestamp} • 📏 {size_kb:.1f} KB • 🏷️ {entry['content_type']}")
            
    def on_history_item_double_clicked(self, item: QListWidgetItem):
        """Handle double-click on history item - copy to clipboard"""
        entry = item.data(Qt.ItemDataRole.UserRole)
        if entry:
            pyperclip.copy(entry['content'])
            self.statusBar().showMessage(f"✅ Copied to clipboard: {entry['preview']}", 3000)
            
    def show_context_menu(self, position):
        """Show context menu for history items"""
        item = self.history_list.itemAt(position)
        if not item:
            return
            
        entry = item.data(Qt.ItemDataRole.UserRole)
        if not entry:
            return
            
        context_menu = QMenu(self)
        
        # Copy action
        copy_action = QAction("📋 Copy to Clipboard", self)
        copy_action.triggered.connect(lambda: self.copy_entry_to_clipboard(entry))
        context_menu.addAction(copy_action)
        
        # Delete action
        delete_action = QAction("🗑️ Delete Entry", self)
        delete_action.triggered.connect(lambda: self.delete_entry_from_context(entry))
        context_menu.addAction(delete_action)
        
        # Separator
        context_menu.addSeparator()
        
        # Entry info
        info_action = QAction(f"📅 {entry['timestamp']} • 📏 {entry['size_bytes']/1024:.1f} KB", self)
        info_action.setEnabled(False)
        context_menu.addAction(info_action)
        
        # Show menu at cursor position
        context_menu.exec(self.history_list.mapToGlobal(position))
        
    def copy_entry_to_clipboard(self, entry):
        """Copy specific entry to clipboard"""
        pyperclip.copy(entry['content'])
        self.statusBar().showMessage(f"✅ Copied to clipboard: {entry['preview']}", 3000)
        
    def delete_entry_from_context(self, entry):
        """Delete entry from context menu"""
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete this entry?\n\n{entry['preview']}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.delete_entry(entry['id'])
            self.load_clipboard_history()
            self.content_viewer.clear()
            self.entry_info.setText("No entry selected")
            
    def copy_selected_to_clipboard(self):
        """Copy selected entry back to clipboard"""
        current_item = self.history_list.currentItem()
        if current_item:
            entry = current_item.data(Qt.ItemDataRole.UserRole)
            if entry:
                pyperclip.copy(entry['content'])
                self.statusBar().showMessage(f"✅ Copied to clipboard: {entry['preview']}", 3000)
                    
    def clear_all_history(self):
        """Clear all clipboard history"""
        reply = QMessageBox.question(
            self, "Confirm Clear All",
            "Are you sure you want to clear all clipboard history? This cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.storage.clear_all_entries()
            self.load_clipboard_history()
            self.content_viewer.clear()
            self.entry_info.setText("No entry selected")
            
    def export_clipboard_data(self):
        """Export clipboard data to file"""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Clipboard Data", 
                f"clipboard_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;Text Files (*.txt);;All Files (*)"
            )
            
            if filename:
                entries = self.storage.get_all_entries()
                export_data = []
                
                for entry in entries:
                    export_data.append({
                        'content': entry['content'],
                        'timestamp': entry['timestamp'],
                        'content_type': entry['content_type'],
                        'size_bytes': entry['size_bytes']
                    })
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(self, "Export Successful", f"Exported {len(export_data)} entries to:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{str(e)}")
            
    def update_statistics(self):
        """Update statistics display"""
        total_entries = self.storage.get_total_entries()
        storage_used = self.storage.get_storage_size_mb()
        
        self.stats_label.setText(f"📊 Total entries: {total_entries:,} | Storage used: {storage_used:.2f} MB")
        
        # Update progress bar (assuming 1GB max for now)
        max_storage = 1024  # 1GB
        progress = min(int((storage_used / max_storage) * 100), 100)
        self.storage_progress.setValue(progress)
        
    def toggle_window(self):
        """Toggle window visibility"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
            
    def quit_application(self):
        """Quit the application gracefully"""
        self.cleanup_and_quit()
        
    def closeEvent(self, event):
        """Handle window close event"""
        # Hide the window instead of closing
        self.hide()
        event.ignore()
        
    def __del__(self):
        """Destructor to ensure cleanup"""
        try:
            if hasattr(self, 'monitor_thread') and self.monitor_thread.isRunning():
                self.monitor_thread.stop()
        except:
            pass


def main():
    """Main application entry point"""
    # Check for single instance
    lock = SingleInstanceLock("ForeverClipboard")
    
    if not lock.acquire():
        QMessageBox.critical(None, "Forever Clipboard", 
                           "Forever Clipboard is already running!\n\nOnly one instance is allowed.")
        sys.exit(1)
    
    try:
        app = QApplication(sys.argv)
        app.setApplicationName("Forever Clipboard")
        app.setApplicationVersion("1.0.0")
        
        # Create and show main window
        window = ClipboardManagerGUI()
        window.show()
        
        # Setup application cleanup
        def cleanup():
            try:
                if hasattr(window, 'cleanup_and_quit'):
                    window.cleanup_and_quit()
            except:
                pass
            finally:
                lock.release()
        
        # Connect cleanup to application aboutToQuit signal
        app.aboutToQuit.connect(cleanup)
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error starting application: {e}")
        lock.release()
        sys.exit(1)


if __name__ == "__main__":
    main()
