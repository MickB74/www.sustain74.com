# ESG News Automation Setup

## 🚀 Automated Daily Updates

Your ESG news site now automatically updates **twice daily**:
- **8:00 AM** - Morning news update
- **12:00 PM** - Afternoon news update

## 📁 Files Created

- `automated_update.py` - Main automation script
- `manage_automation.py` - Control script for automation
- `com.sustain74.esg-update.plist` - macOS LaunchAgent configuration
- `automation.log` - Log file for automation runs

## 🎛️ Managing Automation

### Check Status
```bash
python manage_automation.py status
```

### Start Automation
```bash
python manage_automation.py start
```

### Stop Automation
```bash
python manage_automation.py stop
```

### Run Manual Update
```bash
python manage_automation.py update
```

### View Logs
```bash
python manage_automation.py logs
```

## 📋 What Happens During Automation

1. **Fetch Latest News** - Runs RSS aggregator to get fresh articles
2. **Generate TLDR** - Creates AI summary using Gemini
3. **Update Files** - Updates `feed.xml` and `esg-news-static.html`
4. **Git Commit** - Commits changes with timestamp
5. **Deploy** - Pushes to live site automatically

## 🔧 Troubleshooting

### Check if Automation is Running
```bash
launchctl list | grep com.sustain74.esg-update
```

### View Automation Logs
```bash
tail -f automation.log
```

### Manual Restart
```bash
python manage_automation.py stop
python manage_automation.py start
```

## 📊 Current Status

✅ **Automation is ACTIVE**
- Next update: 8:00 AM tomorrow
- Then: 12:00 PM tomorrow
- Logs: `automation.log`

## 🌐 Live Site

Your site automatically updates at: https://www.sustain74.com/esg-news-static.html

The automation ensures your ESG news feed stays fresh with the latest content twice daily!















