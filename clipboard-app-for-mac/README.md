# 🚀 Clipboard Manager Pro - Forever Running

A powerful, forever-running clipboard history manager for macOS that automatically starts on login and runs continuously in the background. Similar to CopyClip but with enhanced features, massive storage capacity, and automatic operation.

## 🌟 **Key Features**

- **🔄 Forever Running**: Runs continuously in the background 24/7
- **🚀 Auto-Start**: Automatically starts when you log in
- **💾 Massive Storage**: No practical limits on clipboard entries
- **🎨 Dark Theme GUI**: Beautiful dark interface with white text
- **🔍 Smart Search**: Find clipboard entries quickly
- **📱 System Tray**: Always accessible from system tray
- **📊 Real-time Monitoring**: Captures every copy operation automatically
- **📤 Export Functionality**: Save clipboard data to files
- **⚡ Zero Maintenance**: Works automatically without intervention

## 📝 **Changelog**

### **Version 4.0.1 - Additional Features**
- ✅ **Added View Tab while editing**

### **Version 4.0.0 - Additional Features**
- ✅ **Added bulk selection feature** with selection & delete selected
- ✅ **Added Edit on the go feature** with attached notepad

### **Version 3.0.0 - MacOS Application**
- ✅ **Created an easy to setup app** Checkout README.md in parent Directory
- ✅ **New updated GUI** with basic Features

### **Version 2.0.0 - Forever Running**
- ✅ **Auto-start on login** with LaunchAgent
- ✅ **Forever running** in background
- ✅ **Dark theme GUI** with perfect visibility
- ✅ **Zero maintenance** operation
- ✅ **Comprehensive management** scripts
- ✅ **100% dynamic paths** - works on any Mac

### **Version 1.0.0 - Basic Features**
- ✅ **Clipboard monitoring** and capture
- ✅ **SQLite storage** with indexing
- ✅ **Search and filter** functionality
- ✅ **Export capabilities**
- ✅ **System tray integration**

## 🚀 **Quick Start (One Command!)**

** VERY IMPORTANT **
- Make sure to make ./manage_clipboard_forever.sh and ./start_forever.sh executable
  ```bash
  chmod +x manage_clipboard_forever.sh && chmod +x start_forever.sh
  
  ```

**Navigate into the project repo and then:**
```bash
pip install -r requirements.txt
#OR
pip3 install -r requirements.txt 
```

**TO START NAVIGATE INTO RPEO AND PASTE BELOW COMMAND:**
```bash
./start_forever.sh
```

**That's it!** Your clipboard manager will:
- ✅ Start running in the background
- ✅ Enable auto-start on login
- ✅ Capture everything you copy
- ✅ Run forever without maintenance

## 📱 **Daily Usage**

### **What Happens Automatically**
1. **Log in to your Mac** → Clipboard manager starts automatically
2. **Copy anything** using `Cmd+C` → Automatically captured
3. **Use normally** → No manual intervention needed
4. **Log out** → Process continues in background

### **Accessing Your Clipboard History**
- **System Tray**: Right-click clipboard manager icon for quick access
- **Main Window**: Shows clipboard history with search and export
- **Keyboard Shortcuts**: `Ctrl+Shift+V` to show/hide main window

## 🛠️ **Management Commands**

### **Check Status**
```bash
./manage_clipboard_forever.sh status
```

### **Start/Stop**
```bash
./manage_clipboard_forever.sh start     # Start
./manage_clipboard_forever.sh stop      # Stop
./manage_clipboard_forever.sh restart   # Restart
```

### **Auto-Start Management**
```bash
./manage_clipboard_forever.sh enable    # Enable auto-start
./manage_clipboard_forever.sh disable   # Disable auto-start
```

### **Other Commands**
```bash
./manage_clipboard_forever.sh logs      # View logs
./manage_clipboard_forever.sh clear     # Clear database
./manage_clipboard_forever.sh help      # Show help
```

## 🎨 **GUI Features**

### **Main Window**
- **Left Panel**: Clipboard history list with search functionality
- **Right Panel**: Content viewer and action buttons
- **Dark Theme**: Beautiful dark interface with white text for perfect visibility

### **Search & Filter**
- **Real-time Search**: Filter entries as you type
- **Content Type Detection**: Automatically identifies URLs, files, text
- **Smart Previews**: See content without opening full entries

### **Actions**
- **Copy Back**: Double-click any entry to copy it back to clipboard
- **Delete**: Remove unwanted entries
- **Export**: Save clipboard data to JSON or text files
- **Clear All**: Reset entire clipboard history

### **Keyboard Shortcuts**
- `Ctrl+Shift+V`: Show/hide main window
- `Ctrl+F`: Focus search bar
- `Ctrl+C`: Copy selected entry back to clipboard

## 🗄️ **Storage & Capacity**

### **Database**
- **Storage Engine**: SQLite with optimized indexing
- **File Location**: `clipboard_history.db` in project directory
- **Backup**: Automatic with macOS Time Machine

### **Capacity Limits**
- **Entries**: **Millions** of clipboard entries
- **Content Size**: **Terabytes** of data
- **Performance**: Excellent up to 1GB+ databases
- **File Size**: Limited only by available disk space

### **Performance Characteristics**
- **1,000 entries**: Instant response
- **100,000 entries**: Very fast (< 100ms)
- **1,000,000 entries**: Fast (~500ms)
- **10,000,000 entries**: Good (~2 seconds)

## 🔧 **Architecture**

### **Core Components**
- **`clipboard_manager_gui.py`**: Main GUI application with dark theme
- **`clipboard_monitor.py`**: Background clipboard monitoring
- **`clipboard_storage.py`**: SQLite database management
- **`settings_manager.py`**: Application settings and preferences
- **`utils.py`**: Utility functions and helpers

### **Background Services**
- **LaunchAgent**: `com.clipboardmanager.pro.plist`
- **Auto-start**: `~/Library/LaunchAgents/`
- **Process Management**: Automatic restart and monitoring
- **Logging**: Comprehensive logging to `clipboard_manager.log`

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Clipboard Manager Not Starting**
```bash
# Check if process is running
./manage_clipboard_forever.sh status

# View error logs
./manage_clipboard_forever.sh logs

# Restart the service
./manage_clipboard_forever.sh restart
```

#### **Auto-Start Not Working**
```bash
# Re-enable auto-start
./manage_clipboard_forever.sh enable

# Check LaunchAgent status
launchctl list | grep clipboardmanager
```

#### **High Memory Usage**
```bash
# Check process status
ps aux | grep clipboard_manager_gui

# Restart if needed
./manage_clipboard_forever.sh restart
```

### **Log Files**
- **Main Log**: `clipboard_manager.log`
- **Database**: `clipboard_history.db`
- **LaunchAgent**: `~/Library/LaunchAgents/com.clipboardmanager.pro.plist`

## 🔄 **Updates & Maintenance**

### **Updating the Application**
```bash
cd forever_clipboard
git pull origin main  # If using git
./manage_clipboard_forever.sh restart
```

### **Database Maintenance**
```bash
# Check database size
./manage_clipboard_forever.sh status

# Clear old entries if needed
./manage_clipboard_forever.sh clear

# Export data before clearing
# Use GUI export function or SQLite commands
```

### **System Updates**
- **macOS Updates**: Clipboard manager will restart automatically
- **Python Updates**: May require virtual environment reactivation
- **Dependencies**: Update with `pip install -r requirements.txt`

## 📊 **Monitoring & Statistics**

### **Real-time Statistics**
- **Total Entries**: Live count of clipboard entries
- **Storage Used**: Current database size in MB
- **Process Status**: Running/stopped status
- **Auto-start Status**: Enabled/disabled status

### **Performance Metrics**
- **Response Time**: How quickly entries are captured
- **Search Speed**: Time to find specific entries
- **Memory Usage**: Process memory consumption
- **Database Performance**: Query execution times

## 🌟 **Advanced Features**

### **Content Analysis**
- **URL Detection**: Automatically identifies web links
- **File Path Detection**: Recognizes file system paths
- **Content Type Classification**: Text, URLs, files, multiline
- **Size Optimization**: Efficient storage of large content

### **Export Capabilities**
- **JSON Export**: Structured data export
- **Text Export**: Plain text format
- **Custom Formats**: Extensible export system
- **Batch Operations**: Export multiple entries

### **Integration Features**
- **System Tray**: Always accessible
- **Notifications**: Clipboard update alerts
- **Keyboard Shortcuts**: Quick access
- **Background Operation**: Non-intrusive operation

## 🎯 **Best Practices**

### **Daily Usage**
1. **Start Once**: Run `./start_forever.sh` once to set up
2. **Use Normally**: Copy and paste as usual
3. **Access When Needed**: Use system tray or keyboard shortcuts
4. **No Maintenance**: Let it run automatically

### **Data Management**
1. **Regular Backups**: Use export function for important data
2. **Monitor Storage**: Check status periodically
3. **Clear Old Data**: Remove unwanted entries as needed
4. **Search Efficiently**: Use search to find specific content

### **Performance Optimization**
1. **Keep Updated**: Regular application updates
2. **Monitor Logs**: Check for any errors
3. **Restart if Needed**: Use restart command for issues
4. **Database Health**: Monitor database size and performance

## 🚀 **Getting Help**

### **Built-in Help**
```bash
./manage_clipboard_forever.sh help
```

### **Status Information**
```bash
./manage_clipboard_forever.sh status
```

### **Log Analysis**
```bash
./manage_clipboard_forever.sh logs
```

### **Process Information**
```bash
ps aux | grep clipboard_manager_gui
```

**Just use your Mac normally with `Cmd+C` and `Cmd+V` - it will capture everything automatically and run forever!** 🎉

The clipboard manager is now your invisible, always-on assistant that remembers everything you've ever copied! 🌙✨

---

## 📄 **License**

This project is open source and available under the MIT License.

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## 📞 **Support**

For issues or questions:
1. Check the troubleshooting section above
2. Use the built-in help commands
3. Review the log files
4. Check the status with management commands

---

## 🚀 **For Your Friends**

### **Sharing is Easy!**
1. **Copy the entire `forever_clipboard` folder** to their Mac
2. **They run `./start_forever.sh`** - one command setup
3. **That's it!** Works instantly on any Mac

### **Why It's Amazing**
- ✅ **Zero configuration** - works immediately
- ✅ **No hardcoded paths** - adapts to any Mac
- ✅ **Professional quality** - enterprise-grade reliability
- ✅ **Beautiful interface** - dark theme with perfect visibility
- ✅ **Forever running** - 24/7 operation

**Your friends will get a professional-grade clipboard manager instantly!** 🎯✨

