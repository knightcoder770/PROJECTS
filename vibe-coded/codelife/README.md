# ⚡ CodeLife — Your Personal Dev OS

A single-window web app that makes your coding life easier. Morning dashboard, session tracking, roadmap progress, goals — all in one dark terminal-aesthetic UI.

![Python](https://img.shields.io/badge/python-3.10+-blue)
![Flask](https://img.shields.io/badge/flask-3.0+-green)
![License](https://img.shields.io/badge/license-MIT-orange)
![Open Source](https://img.shields.io/badge/open%20source-yes-brightgreen)

---

## What it does

- **Morning Dashboard** — greeting, today's coding hours, streak, roadmap position
- **Session Logger** — log work sessions with project name, duration, notes
- **Weekly Activity Chart** — visualise your coding hours across the week
- **Goal Tracker** — set and tick off weekly goals
- **Roadmap Topics** — track which topics you've covered this week
- **DevTrack integration** — reads your existing DevTrack data directly
- **GitPush integration** — push to GitHub from inside CodeLife (Phase 3)
- **AI Brain** — AI-powered commit messages, summaries, README generator (Phase 3)

---

## Getting started

```bash
git clone https://github.com/yourusername/codelife.git
cd codelife
pip install -r requirements.txt
python main.py
```

Opens automatically at `http://127.0.0.1:5000`. First run shows the setup wizard.

---

## Setup wizard

On first run, CodeLife asks you:
1. Your name + GitHub username
2. Path to your DevTrack folder (optional)
3. Path to your GitPush folder (optional)
4. Which week/month of the AI engineering roadmap you're on

Everything is stored locally in `config.json` — never uploaded anywhere.

---

## Project structure

```
codelife/
├── main.py               Entry point — starts Flask + opens browser
├── app.py                Flask app factory
├── config_manager.py     Reads/writes config.json, connects to DevTrack
├── data_store.py         Sessions, streaks, goals, roadmap progress
├── routes/
│   ├── setup.py          Setup wizard routes
│   ├── dashboard.py      Main dashboard route
│   └── api.py            REST API for AJAX calls
├── templates/
│   ├── base.html         Sidebar layout
│   ├── setup.html        Setup wizard
│   └── dashboard.html    Morning dashboard
├── static/
│   ├── css/main.css      Dark terminal aesthetic
│   └── js/main.js        Utility JS
├── config.json           Auto-generated — your local settings (gitignored)
├── codelife_data.json    Auto-generated — your local data (gitignored)
└── requirements.txt
```

---

## Data stays local

`config.json` and `codelife_data.json` are gitignored. Your data never leaves your machine. CodeLife reads your existing DevTrack data directly from your filesystem — no sync, no cloud, no accounts.

---

## Roadmap (phases)

- [x] **Phase 1** — Setup wizard, morning dashboard, session logger, goals, topics
- [ ] **Phase 2** — Pomodoro session timer, study tracker module
- [ ] **Phase 3** — GitPush tab, AI Brain (Claude API), commit message generator
- [ ] **Phase 4** — End of day summary, DevTrack deep sync, LinkedIn post generator

---

## Contributing

Contributions welcome! Ideas for open source contributors:

- Dark/light theme toggle
- Export session data to CSV
- GitHub stats widget (commits today, PRs open)
- Calendar heatmap view (like GitHub contribution graph)
- Notification/reminder system
- Cross-platform installer (PyInstaller exe/dmg)
- More roadmap templates (web dev, data science, etc.)

Open an issue or submit a PR!

---

## License

MIT
