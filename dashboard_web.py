#!/usr/bin/env python3
"""
Marketing Intelligence Dashboard - Web Version
For deployment to PythonAnywhere, Render, etc.
"""

import os
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template_string

app = Flask(__name__)

# Use relative paths for web deployment
BASE_DIR = Path(__file__).parent
DAILY_DIR = BASE_DIR / "Daily Opportunities"
ACTIONS_LOG = DAILY_DIR / "actions_log.json"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Marketing Intelligence</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #e8eef5 0%, #f5f7fa 100%);
            color: #333;
            padding: 40px;
            min-height: 100vh;
        }
        @media (max-width: 768px) {
            body { padding: 16px; }
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
        }
        .header h1 {
            font-size: 32px;
            font-weight: 700;
            color: #1a1a2e;
        }
        .header .subtitle {
            color: #888;
            font-size: 14px;
            margin-top: 8px;
        }

        .stats-row {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto 30px;
        }
        @media (max-width: 768px) {
            .stats-row { grid-template-columns: repeat(2, 1fr); gap: 12px; }
        }

        .stat-card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            text-align: center;
        }
        .stat-card .number {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 4px;
        }
        .stat-card .label {
            font-size: 13px;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .stat-card .sublabel {
            font-size: 12px;
            color: #aaa;
            margin-top: 4px;
        }

        .red .number { color: #e74c3c; }
        .amber .number { color: #f39c12; }
        .green .number { color: #27ae60; }
        .purple .number { color: #8b5cf6; }
        .blue .number { color: #3b82f6; }
        .pink .number { color: #ec4899; }

        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            max-width: 1200px;
            margin: 0 auto;
        }
        @media (max-width: 768px) {
            .main-grid { grid-template-columns: 1fr; }
        }

        .card {
            background: white;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            border: 2px solid #e5e7eb;
        }
        .card.border-red { border-color: #e74c3c; }
        .card.border-amber { border-color: #f39c12; }
        .card.border-green { border-color: #27ae60; }
        .card.border-blue { border-color: #3b82f6; }
        .card.border-purple { border-color: #8b5cf6; }
        .card h2 {
            font-size: 14px;
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            gap: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .card h2 .dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        .card h2 .dot.red { background: #e74c3c; }
        .card h2 .dot.amber { background: #f39c12; }
        .card h2 .dot.green { background: #27ae60; }
        .card h2 .dot.blue { background: #3b82f6; }

        .card ul { list-style: none; }
        .card li {
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
            font-size: 14px;
            line-height: 1.5;
            color: #444;
        }
        .card li:last-child { border-bottom: none; }
        .card li strong { color: #1a1a2e; }

        .full-width { grid-column: 1 / -1; }

        .quick-win {
            background: #f8fafc;
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 12px;
            border-left: 4px solid #8b5cf6;
        }
        .quick-win:last-child { margin-bottom: 0; }
        .quick-win .title {
            font-weight: 600;
            color: #1a1a2e;
            margin-bottom: 6px;
        }
        .quick-win .what {
            font-size: 14px;
            color: #555;
            margin-bottom: 8px;
        }
        .quick-win .action {
            font-size: 13px;
            color: #8b5cf6;
        }

        .empty {
            color: #aaa;
            font-style: italic;
            font-size: 14px;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            color: #aaa;
            font-size: 13px;
        }
        .footer a { color: #8b5cf6; text-decoration: none; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Marketing Intelligence</h1>
        <div class="subtitle">Week of {{ week_start }} - {{ week_end }}</div>
    </div>

    <div class="stats-row">
        <div class="stat-card red">
            <div class="number">{{ outreach_count }}</div>
            <div class="label">Outreach Triggers</div>
            <div class="sublabel">Act immediately</div>
        </div>
        <div class="stat-card amber">
            <div class="number">{{ signals_count }}</div>
            <div class="label">Buying Signals</div>
            <div class="sublabel">This week</div>
        </div>
        <div class="stat-card purple">
            <div class="number">{{ competitor_count }}</div>
            <div class="label">Competitor Moves</div>
            <div class="sublabel">Monitor</div>
        </div>
        <div class="stat-card blue">
            <div class="number">{{ actions_count }}</div>
            <div class="label">Actions Taken</div>
            <div class="sublabel">This week</div>
        </div>
    </div>

    <div class="main-grid">
        <div class="card border-red">
            <h2><span class="dot red"></span> Immediate Outreach</h2>
            {% if outreach_triggers %}
            <ul>
                {% for item in outreach_triggers %}
                <li>{{ item | safe }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p class="empty">No immediate triggers this week</p>
            {% endif %}
        </div>

        <div class="card border-amber">
            <h2><span class="dot amber"></span> Buying Signals</h2>
            {% if buying_signals %}
            <ul>
                {% for item in buying_signals %}
                <li>{{ item | safe }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p class="empty">No buying signals detected</p>
            {% endif %}
        </div>

        <div class="card border-amber">
            <h2><span class="dot amber"></span> Competitor Activity</h2>
            {% if competitor_activity %}
            <ul>
                {% for item in competitor_activity %}
                <li>{{ item | safe }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p class="empty">No competitor activity</p>
            {% endif %}
        </div>

        <div class="card border-blue">
            <h2><span class="dot blue"></span> Target Accounts</h2>
            {% if target_accounts %}
            <ul>
                {% for item in target_accounts %}
                <li>{{ item | safe }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p class="empty">No target account news</p>
            {% endif %}
        </div>

        <div class="card border-green">
            <h2><span class="dot green"></span> Content Opportunities</h2>
            {% if content_opps %}
            <ul>
                {% for item in content_opps %}
                <li>{{ item | safe }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p class="empty">No content opportunities</p>
            {% endif %}
        </div>

        <div class="card border-green">
            <h2><span class="dot green"></span> Trends to Watch</h2>
            {% if trends %}
            <ul>
                {% for item in trends %}
                <li>{{ item | safe }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p class="empty">No trends identified</p>
            {% endif %}
        </div>

        <div class="card full-width border-blue">
            <h2><span class="dot blue"></span> Key Takeaways</h2>
            {% if takeaways %}
            <ul>
                {% for item in takeaways %}
                <li>{{ item | safe }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p class="empty">No takeaways</p>
            {% endif %}
        </div>

        <div class="card full-width border-amber">
            <h2><span class="dot amber"></span> Today's Quick Wins</h2>
            {% if quick_wins %}
                {% for win in quick_wins %}
                <div class="quick-win">
                    <div class="title">{{ win.title }}</div>
                    <div class="what">{{ win.what }}</div>
                    <div class="action">→ {{ win.action }}</div>
                </div>
                {% endfor %}
            {% else %}
            <p class="empty">No quick wins today</p>
            {% endif %}
        </div>
    </div>

    <div class="footer">
        Last updated: {{ now }} | <a href="/">Refresh</a>
    </div>
</body>
</html>
"""

def get_latest_weekly():
    files = list(DAILY_DIR.glob("*_weekly_summary.md"))
    if not files:
        return None
    files.sort(reverse=True)
    return files[0]

def get_latest_daily():
    files = list(DAILY_DIR.glob("*_opportunities.md"))
    if not files:
        return None
    files.sort(reverse=True)
    return files[0]

def parse_section(content, section_name):
    pattern = rf"## {section_name}\n(.*?)(?=\n## |\n---|\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        return []
    section_text = match.group(1).strip()
    items = []
    for line in section_text.split('\n'):
        line = line.strip()
        if line.startswith('•') or line.startswith('-') or line.startswith('*'):
            item = re.sub(r'^[•\-\*]\s*', '', line)
            item = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', item)
            if item:
                items.append(item)
    return items

def parse_quick_wins(content):
    wins = []
    pattern = r'\*\*Quick Win #\d+\*\*.*?\n\*\*What:\*\* ([^\n]+)\n.*?\*\*Action:\*\* ([^\n]+)'
    matches = re.findall(pattern, content, re.DOTALL)
    for i, (what, action) in enumerate(matches, 1):
        wins.append({'title': f'Quick Win #{i}', 'what': what.strip(), 'action': action.strip()})
    pattern2 = r'\*\*Opportunity #\d+\*\*.*?\n\*\*What:\*\* ([^\n]+)\n.*?\*\*Action:\*\* ([^\n]+)'
    matches2 = re.findall(pattern2, content, re.DOTALL)
    for i, (what, action) in enumerate(matches2, len(wins) + 1):
        wins.append({'title': f'Opportunity #{i - len(matches)}', 'what': what.strip(), 'action': action.strip()})
    return wins

def get_actions_count():
    if not ACTIONS_LOG.exists():
        return 0
    try:
        with open(ACTIONS_LOG, 'r') as f:
            data = json.load(f)
        current_week = datetime.now().strftime("%Y-W%W")
        return sum(1 for a in data.get("actions", []) if a.get("week") == current_week)
    except:
        return 0

@app.route('/')
def dashboard():
    now = datetime.now()
    week_start = (now - timedelta(days=now.weekday())).strftime('%B %d')
    week_end = now.strftime('%B %d, %Y')

    data = {
        'now': now.strftime('%H:%M'),
        'week_start': week_start,
        'week_end': week_end,
        'outreach_triggers': [],
        'buying_signals': [],
        'competitor_activity': [],
        'target_accounts': [],
        'content_opps': [],
        'trends': [],
        'takeaways': [],
        'quick_wins': [],
        'outreach_count': 0,
        'signals_count': 0,
        'competitor_count': 0,
        'actions_count': get_actions_count()
    }

    weekly_file = get_latest_weekly()
    if weekly_file:
        content = weekly_file.read_text()
        data['outreach_triggers'] = parse_section(content, 'Immediate Outreach Triggers')
        data['buying_signals'] = parse_section(content, 'Buying Signals Detected')
        data['competitor_activity'] = parse_section(content, 'Competitor Activity')
        data['target_accounts'] = parse_section(content, 'Target Account Intel')
        data['content_opps'] = parse_section(content, 'Content Opportunities Identified')
        data['trends'] = parse_section(content, 'Trends to Watch')
        data['takeaways'] = parse_section(content, 'Key Takeaways')
        data['outreach_count'] = len(data['outreach_triggers'])
        data['signals_count'] = len(data['buying_signals'])
        data['competitor_count'] = len(data['competitor_activity'])

    daily_file = get_latest_daily()
    if daily_file:
        content = daily_file.read_text()
        data['quick_wins'] = parse_quick_wins(content)

    return render_template_string(HTML_TEMPLATE, **data)

# For PythonAnywhere - they look for 'app'
# For local testing
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)
