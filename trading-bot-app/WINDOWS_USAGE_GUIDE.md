# Windows Batch Files Usage Guide

## 📁 Available Batch Files

| File | Purpose | When to Use |
|------|---------|-------------|
| `install.bat` | Sets up Python environment and dependencies | First time only |
| `start.bat` | Stops any running instances, then starts bot + dashboard | Every time you want to use the app |
| `stop.bat` | Gracefully stops all running services | When you want to pause trading |
| `uninstall.bat` | Removes virtual environment and data | When removing the app completely |

---

## 🚀 Quick Start Workflow

### Step 1: Installation (First Time Only)
```
Double-click: install.bat
```
- Checks Python installation
- Creates virtual environment
- Installs all dependencies
- Creates storage directories
- Creates default .env file

**Wait for:** "INSTALLATION COMPLETED SUCCESSFULLY!"

---

### Step 2: Start the Application
```
Double-click: start.bat
```
**What it does:**
1. ✅ Automatically runs `stop.bat` first (clears any stuck processes)
2. ✅ Checks if virtual environment exists
3. ✅ Activates Python environment
4. ✅ Creates necessary directories
5. ✅ Opens TWO new windows:
   - **Window 1:** Trading Bot - Strategy Engine (background learning)
   - **Window 2:** Trading Bot - Dashboard (web interface)

**Wait for:** "SERVICES STARTED SUCCESSFULLY!"

**Then open your browser:** http://localhost:5000

---

### Step 3: Stop the Application
```
Double-click: stop.bat
```
**What it does:**
1. Kills all trading bot processes
2. Finds and stops dashboard on port 5000
3. Cleans up PID files

**Wait for:** "ALL SERVICES STOPPED SUCCESSFULLY!"

---

### Step 4: Uninstall (If Needed)
```
Double-click: uninstall.bat
```
**What it removes:**
- Virtual environment (venv folder)
- All storage data (strategies, logs, trades)
- Configuration files (.env)
- Python cache files

**What it keeps:**
- Batch files themselves
- Source code (src folder)
- Documentation
- requirements.txt

---

## 🔄 Daily Usage Pattern

### Morning (Start Trading)
1. Double-click `start.bat`
2. Wait for two windows to open
3. Open browser to http://localhost:5000
4. Monitor dashboard throughout the day

### Evening (Stop Trading)
1. Double-click `stop.bat`
2. Wait for confirmation
3. Close the two console windows if still open

---

## ⚠️ Important Notes

### Before Running start.bat:
- Ensure no other applications are using port 5000
- If you get port conflicts, run `stop.bat` first manually

### If start.bat Fails:
1. Run `stop.bat` manually
2. Check if Python is installed: `python --version`
3. Re-run `install.bat` if needed

### Running Multiple Instances:
- **DO NOT** run multiple instances simultaneously
- `start.bat` automatically stops existing instances first
- Always use `stop.bat` before manually starting anything

### Firewall Alerts:
- Windows may show firewall alerts when dashboard starts
- Click "Allow Access" for private networks
- This is normal for localhost web servers

---

## 🛠️ Troubleshooting

### Problem: "Python not found"
**Solution:** Install Python from https://www.python.org/downloads/
- During installation, CHECK "Add Python to PATH"

### Problem: "Port 5000 already in use"
**Solution:** 
1. Run `stop.bat`
2. Wait 10 seconds
3. Run `start.bat` again

### Problem: "Virtual environment missing"
**Solution:** Run `install.bat` again

### Problem: Dashboard won't load
**Solution:**
1. Check if both windows opened
2. Look for errors in the Dashboard window
3. Try http://127.0.0.1:5000 instead

---

## 📊 What Each Window Does

### Window 1: Trading Bot - Strategy Engine
```
Title: Trading Bot - Strategy Engine
Process: python src/main.py
```
- Runs the main orchestrator
- Manages strategy lab
- Executes shadow trades
- Collects market data
- Optimizes strategies
- **DO NOT CLOSE** unless stopping

### Window 2: Trading Bot - Dashboard
```
Title: Trading Bot - Dashboard
Process: python src/dashboard/app.py
```
- Runs Flask web server
- Serves the UI at port 5000
- Shows real-time data
- **DO NOT CLOSE** unless stopping

---

## 🔐 Security Notes

- Never share your `.env` file (contains API keys)
- Run batch files as standard user (no admin needed)
- Keep the application folder in a secure location
- Regularly update dependencies

---

## 📞 Support

If issues persist:
1. Check `storage/logs/` for error logs
2. Review console output in both windows
3. Ensure Python version is 3.8 or higher
4. Re-run `install.bat` to repair installation
