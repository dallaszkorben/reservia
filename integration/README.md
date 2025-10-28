# Reservia Integration Examples

This directory contains integration examples demonstrating how to interact with the Reservia resource reservation system programmatically.

## 📁 Contents

### Python Integration (`reservia_integration.py`)
Complete Python example showing the full Reservia workflow:
- User authentication with SHA-256 password hashing
- Resource reservation management
- Status monitoring with keep-alive messages
- Script execution with reservation maintenance
- Proper resource cleanup

### Mock Script (`mock_script.py`)
Simple test script that simulates a 30-second workload for demonstration purposes.

## 🚀 Quick Start

### Prerequisites
```bash
pip install requests
```

### Configuration
Edit the configuration section in `reservia_integration.py`:
```python
RESERVIA_BASE_URL = "https://reservia.bss.seli.gic.ericsson.se"
RESOURCE_ID = 1
USERNAME = "your_username"
PASSWORD = "your_password"
```

### Run the Integration
```bash
python3 reservia_integration.py
```

## 📋 Workflow Overview

1. **Authentication**: Login with hashed credentials
2. **Reservation**: Request resource or check existing reservation
3. **Approval Wait**: Monitor status, send keep-alive if needed
4. **Execution**: Run mock script while maintaining reservation
5. **Cleanup**: Release resource when complete

## 🔧 API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `POST /session/login` | User authentication |
| `POST /reservation/request` | Request resource reservation |
| `GET /reservation/active` | Check reservation status |
| `POST /reservation/keep_alive` | Extend reservation validity |
| `POST /reservation/release` | Release resource |

## 📊 Expected Output

```
============================================================
🎯 RESERVIA INTEGRATION SCRIPT
============================================================
Logging in as user1...
✅ Login successful
📋 Found existing reservation with status: approved
🚀 Starting mock script...
📋 Mock script started with PID: 12345
🔄 Monitoring script execution...
⏰ Keep alive sent
⏰ Keep alive sent
⏰ Keep alive sent
⏰ Keep alive sent
⏰ Keep alive sent
⏰ Keep alive sent
✅ Mock script completed successfully
Releasing resource...
✅ Resource released successfully
============================================================
🎉 WORKFLOW COMPLETED SUCCESSFULLY
============================================================
```

## 🛠️ Customization

### Timing Configuration
Adjust intervals in the configuration section:
```python
STATUS_CHECK_INTERVAL = 1    # Status check frequency (seconds)
KEEP_ALIVE_INTERVAL = 5      # Keep-alive frequency (seconds)
```

### Replace Mock Script
Replace `mock_script.py` with your actual workload:
```python
# In reservia_integration.py, modify execute_mock_script()
script_path = "path/to/your/actual/script.py"
```

## 🔍 Troubleshooting

### Common Issues

**Login Failed (422)**
- Check username/password
- Ensure password is properly hashed

**Reservation Failed (409)**
- User already has active reservation
- Try releasing existing reservation first

**Keep Alive Failed**
- Check network connectivity
- Verify session is still valid

### Debug Mode
Add debug output by modifying the script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

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

## 📄 License

Same as main Reservia project.
