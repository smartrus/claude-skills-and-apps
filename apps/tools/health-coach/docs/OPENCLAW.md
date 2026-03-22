# OpenClaw Deployment Guide

This guide walks you through deploying the Health Coach on [OpenClaw](https://openclaw.dev) — the recommended and only tested agentic platform for this app.

## Prerequisites

- A running OpenClaw instance (local or remote server with Docker)
- At least one messaging channel connected (WhatsApp, Telegram, or Slack)
- SSH access to your server (if running remotely)

## Architecture

```
┌──────────────┐    ┌───────────────────┐    ┌──────────────────┐
│  You on       │◄──►│  OpenClaw Agent    │◄──►│  Dashboard       │
│  Telegram /   │    │  "health-coach"    │    │  (HTML + JSON)   │
│  WhatsApp     │    │                   │    │                  │
└──────────────┘    │  • AGENTS.md      │    │  Reads from:     │
                    │  • Cron reminders  │    │  health_data.json│
                    │  • health-tracker  │    │                  │
                    │    skill           │    │                  │
                    └───────────────────┘    └──────────────────┘
```

OpenClaw runs on your server. Cron jobs fire at scheduled times, sending you reminders through your messaging app. When you reply, the health-tracker skill parses your response and writes check-in data to `health_data.json`. The dashboard reads that file for visualization.

## File Structure

```
openclaw/
├── AGENTS.md                          # System prompt — always-on health tracking
├── skills/
│   └── health-tracker/
│       └── SKILL.md                   # Parsing skill with exec command template
├── crons/
│   └── health-reminders.yaml          # 8 daily reminders + weekly summary
└── scripts/
    ├── sync-health-data.sh            # Pull/push data between server and local
    ├── append_agents.py               # Append health section to existing AGENTS.md
    └── com.health-coach.sync.plist    # macOS LaunchAgent for nightly sync
```

## Step-by-Step Deployment

### Step 1: Create the Health Coach Agent

```bash
# Add a dedicated agent for health tracking
openclaw agents add health-coach

# Set the system prompt from AGENTS.md
openclaw agents config set health-coach system_prompt "$(cat openclaw/AGENTS.md)"
```

### Step 2: Configure Channel Bindings

Edit your OpenClaw config to route a messaging channel to the health-coach agent. Open `~/.openclaw/config.yaml` and add:

```yaml
agents:
  health-coach:
    model: claude-sonnet-4-6  # or your preferred model
    bindings:
      # Uncomment the channels you use:
      # - channel: telegram
      #   peer: your_chat_or_bot_id
      # - channel: whatsapp
      #   peer: your_whatsapp_contact
      # - channel: slack
      #   channel: "#health-tracking"
```

See `agent/config.yaml` for a full template with all options.

### Step 3: Install the Health-Tracker Skill

```bash
# Copy the skill into OpenClaw's skill directory
cp -r openclaw/skills/health-tracker/ ~/.openclaw/skills/health-tracker/
```

Verify it's loaded:

```bash
# If running in Docker:
CONTAINER=$(docker ps --filter name=openclaw-gateway -q)
docker exec $CONTAINER ls /home/node/.openclaw/skills/health-tracker/
```

### Step 4: Deploy Cron Reminders

First, edit `openclaw/crons/health-reminders.yaml` and replace `YOUR_TIMEZONE` with your IANA timezone (e.g., `Europe/Rome`, `America/New_York`, `Asia/Tokyo`).

```bash
# Copy to OpenClaw's cron directory
cp openclaw/crons/health-reminders.yaml ~/.openclaw/crons/

# If running in Docker:
docker cp openclaw/crons/health-reminders.yaml $CONTAINER:/home/node/.openclaw/crons/
```

Verify crons are loaded:

```bash
docker exec $CONTAINER node dist/index.js cron list
```

### Step 5: Append to AGENTS.md (if you have existing agents)

If your OpenClaw instance already has an `AGENTS.md` with other agent instructions, use the append script instead of overwriting:

```bash
# Option A: Run directly inside the container
docker exec -i $CONTAINER python3 - < openclaw/scripts/append_agents.py

# Option B: Copy and run
docker cp openclaw/scripts/append_agents.py $CONTAINER:/tmp/
docker exec $CONTAINER python3 /tmp/append_agents.py
```

If this is a fresh OpenClaw instance, you can copy `AGENTS.md` directly:

```bash
docker cp openclaw/AGENTS.md $CONTAINER:/home/node/.openclaw/workspace/AGENTS.md
```

### Step 6: Set Up Data Sync (optional)

If you want to pull `health_data.json` to your local machine for the dashboard:

1. **Edit the sync script** — open `openclaw/scripts/sync-health-data.sh` and set:
   - `YOUR_SERVER_IP` — your server's IP address
   - `YOUR_SSH_KEY` — path to your SSH private key
   - `LOCAL_FILE` — where to save the data locally

2. **Test it:**
   ```bash
   chmod +x openclaw/scripts/sync-health-data.sh
   ./openclaw/scripts/sync-health-data.sh
   ```

3. **Automate with macOS LaunchAgent** (macOS only):
   ```bash
   # Edit the plist — update the script path
   nano openclaw/scripts/com.health-coach.sync.plist

   # Install the LaunchAgent
   cp openclaw/scripts/com.health-coach.sync.plist ~/Library/LaunchAgents/
   launchctl load ~/Library/LaunchAgents/com.health-coach.sync.plist

   # Test it
   launchctl start com.health-coach.sync
   ```

   For Linux, use a crontab entry instead:
   ```bash
   # Run nightly at 22:30
   30 22 * * * /path/to/sync-health-data.sh >> /path/to/sync.log 2>&1
   ```

### Step 7: Start the Dashboard

```bash
cd apps/tools/health-coach
python3 scripts/health_server.py
# Open http://localhost:8777
```

The dashboard reads `data/health_data.json`. If you set up sync in Step 6, it will have your latest data from the server.

## Managing Your Deployment

### View and manage cron jobs

```bash
CONTAINER=$(docker ps --filter name=openclaw-gateway -q)

# List all cron jobs
docker exec $CONTAINER node dist/index.js cron list

# Disable a specific reminder
docker exec $CONTAINER node dist/index.js cron edit <job-id> --disable

# Re-enable it
docker exec $CONTAINER node dist/index.js cron edit <job-id> --enable
```

### Check health data

```bash
# View current data inside the container
docker exec $CONTAINER cat /home/node/health_data.json | python3 -m json.tool

# Pull to local
./openclaw/scripts/sync-health-data.sh
```

### Push data back to server

```bash
# If you edited data locally (e.g., fixed an entry)
./openclaw/scripts/sync-health-data.sh --push
```

### Update the skill or crons

```bash
# After editing SKILL.md or health-reminders.yaml:
docker cp openclaw/skills/health-tracker/SKILL.md \
  $CONTAINER:/home/node/.openclaw/skills/health-tracker/SKILL.md

docker cp openclaw/crons/health-reminders.yaml \
  $CONTAINER:/home/node/.openclaw/crons/health-reminders.yaml

# Restart to pick up changes
docker restart $CONTAINER
```

## Troubleshooting

**Agent not responding to check-ins:**
- Verify the skill is installed: `docker exec $CONTAINER ls ~/.openclaw/skills/health-tracker/`
- Check AGENTS.md includes the health tracker section
- Check container logs: `docker logs $CONTAINER --tail 50`

**Cron reminders not firing:**
- Verify timezone is set correctly in `health-reminders.yaml`
- Check cron status: `docker exec $CONTAINER node dist/index.js cron list`
- Check container time: `docker exec $CONTAINER date`

**Sync script failing:**
- Test SSH connectivity: `ssh -i ~/.ssh/YOUR_KEY root@YOUR_SERVER_IP "echo ok"`
- Verify container is running: `ssh root@YOUR_SERVER_IP "docker ps --filter name=openclaw-gateway"`
- Check that `health_data.json` exists inside the container

**Dashboard shows no data:**
- Run the sync script manually: `./openclaw/scripts/sync-health-data.sh`
- Check the local data file: `cat data/health_data.json | python3 -m json.tool`
- Verify the server path matches: `HEALTH_DATA_FILE=./data/health_data.json python3 scripts/health_server.py`
