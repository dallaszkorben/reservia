# Reservia Integration Examples

This directory contains integration examples demonstrating how to interact with the Reservia resource reservation system programmatically.

## 📁 Contents

### Python Integration (`reservia_integration.py`)
Complete Python example showing the full Reservia workflow:
- User authentication with SHA-256 password hashing
- Resource reservation management
- Status monitoring with keep-alive messages
- Configurable script/command execution with reservation maintenance
- Automatic reservation cleanup on failures
- Command-line parameter support

### Mock Script (`mock_script.py`)
Simple test script that simulates a 30-second workload for demonstration purposes.

## 🚀 Quick Start

### Prerequisites
```bash
pip install requests
```

### Basic Usage
```bash
# Use defaults (mock_script.py, 10-second intervals)
python3 reservia_integration.py

# Show help and all options
python3 reservia_integration.py --help
```

### Configuration
Edit the configuration section in `reservia_integration.py` for server settings:
```python
RESERVIA_BASE_URL = "https://reservia.bss.seli.gic.ericsson.se"
RESOURCE_ID = 1
USERNAME = "your_username"
PASSWORD = "your_password"
```

## 🛠️ Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--script` | `-s` | Script/command to execute | `mock_script.py` |
| `--interval` | `-i` | Keep-alive interval (seconds) | `10` |
| `--help` | `-h` | Show help message | - |

## 📋 Usage Examples

### Python Scripts
```bash
# Default Python script
python3 reservia_integration.py

# Custom Python script in same directory
python3 reservia_integration.py --script my_work.py

# Python script with relative path
python3 reservia_integration.py --script ./scripts/analysis.py

# Python script with absolute path
python3 reservia_integration.py --script /home/user/scripts/data_processing.py
```

### System Commands
```bash
# Ubuntu system command
python3 reservia_integration.py --script xcalc

# Shell command
python3 reservia_integration.py --script "sleep 30"

# System executable
python3 reservia_integration.py --script /usr/bin/firefox
```

### Custom Intervals
```bash
# Fast monitoring (5-second intervals)
python3 reservia_integration.py --interval 5

# Slow monitoring (30-second intervals)
python3 reservia_integration.py --interval 30

# Combined options
python3 reservia_integration.py --script "my_long_job.sh" --interval 15
```

## 📋 Workflow Overview

1. **Parse Arguments**: Process command-line parameters
2. **Authentication**: Login with hashed credentials
3. **Reservation**: Request resource or check existing reservation
4. **Approval Wait**: Monitor status, send keep-alive if needed
5. **Execution**: Run specified script/command while maintaining reservation
6. **Cleanup**: Release resource when complete or cancel/release on failure

## 🔧 API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `POST /session/login` | User authentication |
| `POST /reservation/request` | Request resource reservation |
| `GET /reservation/active` | Check reservation status |
| `POST /reservation/keep_alive` | Extend reservation validity |
| `POST /reservation/cancel` | Cancel requested reservation |
| `POST /reservation/release` | Release approved reservation |

## 📊 Expected Output

```
============================================================
🎯 RESERVIA INTEGRATION SCRIPT
============================================================
📄 Script to execute: xcalc
⏱️  Keep-alive interval: 10 seconds
============================================================
Logging in as user1...
✅ Login successful
📋 Found existing reservation with status: approved
🚀 Starting: xcalc
📋 Process started with PID: 12345
🔄 Monitoring script execution...
⏰ Keep alive sent
⏰ Keep alive sent
⏰ Keep alive sent
✅ Script completed successfully
Releasing resource...
✅ Resource released successfully
============================================================
🎉 WORKFLOW COMPLETED SUCCESSFULLY
============================================================
```

## 🛡️ Error Handling

### Script Execution Failures
If the specified script/command fails to start:
```
❌ Script not found: /path/to/script
⚠️  Script execution failed, cleaning up reservation...
Releasing approved reservation...
✅ Reservation released successfully
```

### Automatic Cleanup
- **Requested reservations**: Automatically cancelled
- **Approved reservations**: Automatically released
- **Network errors**: Graceful error messages with status codes

## 🔍 Troubleshooting

### Common Issues

**Script Not Found**
```bash
❌ Script not found: /path/to/script
```
- Check file path and permissions
- For Python scripts, ensure `.py` extension
- For system commands, verify they're in PATH

**Login Failed (422)**
- Check username/password in configuration
- Ensure password is properly hashed

**Reservation Failed (409)**
- User already has active reservation
- Script will detect and use existing reservation

**Keep Alive Failed**
- Check network connectivity
- Verify session is still valid

### Debug Mode
Add debug output by modifying the script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Advanced Features

### Smart Executable Detection
- **Python files** (`.py`): Automatically uses Python interpreter
- **System commands**: Uses shell execution
- **Path handling**: Supports absolute, relative, and command names

### Flexible Reservation Management
- **Existing reservations**: Detects and uses existing reservations
- **Status-aware cleanup**: Uses cancel for requested, release for approved
- **Keep-alive optimization**: Configurable intervals for different workloads

### Comprehensive Error Handling
- **Process monitoring**: Reliable subprocess completion detection
- **Network resilience**: Proper HTTP status code handling
- **Resource cleanup**: Ensures no abandoned reservations

## 📚 Documentation

- **Reservia Repository**: https://github.com/dallaszkorben/reservia
- **API Documentation**: See main repository README
- **Server Status**: `https://reservia.bss.seli.gic.ericsson.se/info/is_alive`

## 🤝 Contributing

To add more integration examples:
1. Create language-specific subdirectories
2. Follow the same workflow pattern
3. Include comprehensive documentation
4. Add error handling and logging
5. Support command-line configuration

## 📄 License

Same as main Reservia project.
