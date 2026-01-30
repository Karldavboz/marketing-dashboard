# Deploy Dashboard to PythonAnywhere

## Quick Setup (Free)

### 1. Create Account
Go to https://www.pythonanywhere.com and sign up (free tier is fine)

### 2. Upload Files
In PythonAnywhere dashboard:
- Go to **Files**
- Create folder: `marketing-dashboard`
- Upload these files:
  - `dashboard_web.py`
  - `requirements.txt`
  - `Daily Opportunities/` folder (with your .md files)

### 3. Create Web App
- Go to **Web** tab
- Click **Add a new web app**
- Choose **Flask**
- Set Python version (3.9+)
- Set source code path: `/home/YOUR_USERNAME/marketing-dashboard`
- Set WSGI file to point to your app

### 4. Configure WSGI
Edit the WSGI file and replace contents with:
```python
import sys
sys.path.insert(0, '/home/YOUR_USERNAME/marketing-dashboard')
from dashboard_web import app as application
```

### 5. Install Dependencies
Open a **Bash console** and run:
```bash
pip install --user flask
```

### 6. Reload
Click **Reload** on the Web tab. Your dashboard is live at:
`https://YOUR_USERNAME.pythonanywhere.com`

---

## Keeping Data Updated

The dashboard reads from markdown files. To update the web version:

### Option A: Manual Upload
After your daily/weekly scripts run locally, upload the new files to PythonAnywhere.

### Option B: GitHub Sync (Recommended)
1. Push your `Daily Opportunities/` folder to a GitHub repo
2. On PythonAnywhere, clone the repo
3. Set up a scheduled task to `git pull` daily

Example scheduled task (PythonAnywhere > Tasks):
```bash
cd /home/YOUR_USERNAME/marketing-dashboard && git pull
```

### Option C: Direct Push from Local
Add to your cron job after the daily script:
```bash
cd "/Users/karl/Documents/Obsidian/xtract ABM" && \
git add "Daily Opportunities/*.md" && \
git commit -m "Daily update $(date +%Y-%m-%d)" && \
git push
```

---

## Files Needed

```
marketing-dashboard/
├── dashboard_web.py
├── requirements.txt
└── Daily Opportunities/
    ├── 2026-01-30_opportunities.md
    ├── 2026-01-30_weekly_summary.md
    ├── actions_log.json
    └── ... (other files)
```
