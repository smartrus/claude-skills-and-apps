---
name: "Health Coach"
description: "Agent-first health habits tracker — get reminders and check in via WhatsApp/Telegram, with a visual dashboard for progress"
version: "1.1.0"
author: "smartrus"
tags: [health, habits, tracking, wellness, agent, whatsapp, telegram, dashboard]
tech_stack: [HTML, CSS, JavaScript, Python]
---

# Health Coach

An agent-first health habits tracker. Deploy it on [OpenClaw](https://openclaw.dev) (recommended) or any agentic platform, connect it to WhatsApp, Telegram, or Slack, and track 16 daily habits through natural conversation. A visual dashboard shows your progress.

> **OpenClaw is the recommended and only tested platform.** The `openclaw/` directory contains the complete, ready-to-deploy configuration. See [docs/OPENCLAW.md](docs/OPENCLAW.md) for the full deployment guide.

## How It Works

```
+----------------+    +------------------+    +------------------+
|  WhatsApp /    |<-->|  Health Coach    |<-->|  Dashboard       |
|  Telegram /    |    |  Agent           |    |  (HTML + JSON)   |
|  Slack         |    |                  |    |                  |
+----------------+    |  agent/CLAUDE.md |    +------------------+
                      |  skill/SKILL.md  |
                      |  crons/*.yaml    |
                      +------------------+
```

1. The **agent** runs on your platform with `agent/CLAUDE.md` as its system prompt
2. **Cron reminders** nudge you throughout the day via your messaging app
3. You **reply in natural language** ("had salmon for lunch, drank 6 glasses of water")
4. The **health-tracker skill** parses your reply and writes to `health_data.json`
5. The **dashboard** reads that file and shows your progress visually

## Quick Start

### Option 1 — OpenClaw (recommended)

This is how the app is meant to be used. The `openclaw/` directory has everything you need.

```bash
# 1. Create the agent and set its system prompt
openclaw agents add health-coach
openclaw agents config set health-coach system_prompt "$(cat openclaw/AGENTS.md)"

# 2. Install the skill
cp -r openclaw/skills/health-tracker/ ~/.openclaw/skills/health-tracker/

# 3. Deploy cron reminders (edit YOUR_TIMEZONE first!)
cp openclaw/crons/health-reminders.yaml ~/.openclaw/crons/

# 4. Configure your messaging channel in ~/.openclaw/config.yaml
#    See agent/config.yaml for a full template

# 5. Start the dashboard (optional)
python3 scripts/health_server.py
```

For the complete walkthrough including Docker commands, data sync, and troubleshooting, see **[docs/OPENCLAW.md](docs/OPENCLAW.md)**.

### Option 2 — Other agentic platforms

The `agent/` directory contains platform-agnostic files. See `agent/config.yaml` for instructions on adapting to Claude Code or custom frameworks.

### Option 3 — Dashboard only (no agent)

If you just want the web dashboard without messaging integration:

```bash
cd apps/tools/health-coach
python3 scripts/health_server.py
# Open http://localhost:8777
```

## First-Time Setup

Whether you use the agent or the dashboard, the first interaction triggers an onboarding flow. The agent (or dashboard) will ask you to configure:

- Your health goals (weight management, heart health, blood sugar, general wellness, etc.)
- Target metrics (daily water intake, sleep hours, target weight)
- Your name (optional, for personalized greetings)

Your profile is stored in `data/user_profile.json` and can be updated anytime.

## Tracked Habits

### Nutrition (7 habits)

- Eat vegetables first at every meal
- No sugary drinks
- Eat fatty fish or omega-3
- Leafy greens at 2+ meals
- Keep eating window to 10-12 hours
- Limit sodium intake
- Handful of nuts daily

### Exercise (4 habits)

- Morning walk (30-45 min)
- Post-lunch walk (10-15 min)
- Post-dinner walk (10-15 min)
- Home workout or yoga session

### Lifestyle (5 habits)

- Meet daily water goal
- Morning water with lemon
- 5-min breathing exercise
- Sleep 7+ hours
- No screens 30 min before bed

## Project Structure

```
health-coach/
├── README.md                     # This file
├── openclaw/                     # ⭐ OpenClaw-specific deployment (recommended)
│   ├── AGENTS.md                 #    System prompt with exec commands
│   ├── skills/health-tracker/
│   │   └── SKILL.md              #    Parsing skill for OpenClaw exec tool
│   ├── crons/
│   │   └── health-reminders.yaml #    Cron config with Docker management
│   └── scripts/
│       ├── sync-health-data.sh   #    Pull/push data from server
│       ├── append_agents.py      #    Append health section to AGENTS.md
│       └── com.health-coach.sync.plist  # macOS LaunchAgent template
├── agent/                        # Platform-agnostic agent files
│   ├── CLAUDE.md                 #    Agent system prompt ("soul")
│   └── config.yaml               #    Channel bindings & platform config
├── skill/
│   └── SKILL.md                  # Health check-in parsing skill
├── crons/
│   └── health-reminders.yaml     # Daily reminder schedule
├── dashboard/
│   └── index.html                # Visual progress dashboard
├── scripts/
│   ├── health_server.py          # Local sync server
│   └── update_health_data.sh     # CLI tool to update habit data
├── data/
│   └── .gitkeep                  # health_data.json + user_profile.json (runtime)
└── docs/
    ├── SETUP.md                  # General setup guide
    └── OPENCLAW.md               # OpenClaw deployment guide
```

The `openclaw/` directory is the recommended deployment path — it contains everything needed to run on OpenClaw with Docker, including the system prompt, skill, cron config, and sync scripts. The `agent/` directory provides platform-agnostic equivalents for other frameworks. `skill/` provides the parsing logic, `crons/` provides the reminder schedule, and `dashboard/` provides the visual layer.

## API Reference

The sync server exposes these endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Serves the dashboard |
| GET | `/data` | Returns health_data.json |
| POST | `/data` | Overwrites health_data.json (for custom clients or server-side sync) |
| POST | `/checkin` | Individual habit update (from agents) |
| GET | `/health` | Health check |

> **Note:** The dashboard merges server data on load (agent check-ins via `/checkin`) and uses `localStorage` for interactive toggling. The `/data` endpoints are available for custom dashboards or API clients.

### POST /checkin example

```bash
curl -X POST http://localhost:8777/checkin \
  -H "Content-Type: application/json" \
  -d '{"date": "2026-03-22", "habit_id": "e1", "value": true}'
```

## Configuration

All configuration uses environment variables or command-line arguments:

| Variable | Default | Description |
|----------|---------|-------------|
| `HEALTH_DATA_FILE` | `./data/health_data.json` | Path to data file |
| `--port` | `8777` | Server port |
| `--dashboard-dir` | `./dashboard` | Dashboard directory |

## License

MIT — see [LICENSE](../../../LICENSE) for details.
