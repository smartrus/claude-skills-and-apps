# Health Coach — Detailed Setup Guide

## Prerequisites

- Python 3.8+ (for the sync server and data scripts)
- A modern web browser (Chrome, Firefox, Safari, Edge)
- Optional: An AI agent platform for automated check-ins

## Step 1: Dashboard Setup

The simplest way to get started is with the dashboard alone:

```bash
cd apps/tools/health-coach
python3 scripts/health_server.py --port 8777
```

Open http://localhost:8777 in your browser. On first launch, you'll see the onboarding flow to set your goals.

## Step 2: Configure Your Habits

The dashboard tracks 16 default habits across nutrition, exercise, and lifestyle. You can toggle them directly in the browser. In standalone mode, the dashboard saves progress to the browser's localStorage.

When running with the sync server (`health_server.py`), AI agents write to `data/health_data.json` via the `/checkin` API. The dashboard automatically merges server data on load, so agent check-ins appear alongside your manual toggles. You can also view the raw JSON directly via the `/data` endpoint in your browser.

To customize which habits are tracked, edit `skill/SKILL.md` and update the habit ID mappings.

## Step 3: AI Agent Integration (Optional)

If you want automated reminders and natural-language check-ins:

### Using Claude Code / Cowork

1. Copy the skill:
```bash
cp -r skill/ ~/.claude/skills/health-tracker/
```

2. The agent will automatically parse health-related messages and update the data file.

### Using Other Platforms

Adapt `skill/SKILL.md` to your agent platform's skill format. The core logic is the same: parse natural language, map to habit IDs, update the JSON file.

## Step 4: Cron Reminders (Optional)

Edit `crons/health-reminders.yaml`:

1. Replace `YOUR_TIMEZONE` with your timezone (e.g., `America/New_York`)
2. Adjust the schedule times to match your daily routine
3. Deploy to your scheduling system:

### macOS (launchd)

Create a plist file in `~/Library/LaunchAgents/` for each reminder, or use a single script that reads the YAML and sends notifications.

### Linux (crontab)

```bash
# Example: morning reminder at 6:30 AM
30 6 * * * /path/to/send-reminder.sh "Morning kickoff"
```

### Agent Platform

Most AI agent platforms support built-in cron scheduling. Refer to your platform's documentation for setup instructions.

## Data Format

The `health_data.json` file uses this structure:

```json
{
  "2026-03-22": {
    "habits": {
      "n1": true,
      "n2": true,
      "e1": true
    },
    "water": 6,
    "notes": "Had salmon for lunch, morning walk 40 min"
  }
}
```

Each day is keyed by date (YYYY-MM-DD) and contains a habits object, water count, and optional notes.

## Troubleshooting

**Dashboard shows no data:** Make sure `data/health_data.json` exists and contains valid JSON. The server creates it automatically on first request.

**Server won't start:** Check that port 8777 is available. Use `--port` to choose a different port.

**Habits not saving:** Ensure the data directory is writable. Check browser console for errors if using the dashboard directly.
