#!/usr/bin/env python3
"""
append_agents.py — Append the Health Tracker section to your OpenClaw AGENTS.md

This script adds the health tracker's always-on instructions to your
OpenClaw workspace's AGENTS.md file. Run it once after deploying the
health-coach agent.

Usage:
    python3 append_agents.py
    python3 append_agents.py /path/to/AGENTS.md   # custom path

The default path is /home/node/.openclaw/workspace/AGENTS.md (inside Docker).
To run inside the container:
    docker exec -i <container> python3 - < append_agents.py
"""
import sys
import os

# Default path — change if your OpenClaw workspace is elsewhere
DEFAULT_PATH = "/home/node/.openclaw/workspace/AGENTS.md"

target = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_PATH

HEALTH_TRACKER_SECTION = """

---

## Health Tracker — ALWAYS ACTIVE

The user has a health habits tracking system. When they mention ANYTHING about water, food, meals, walking, exercise, yoga, breathing, sleep, or screens — you MUST do TWO things:

1. **Write to memory** as you normally would (daily check-in notes in memory files)
2. **ALSO call exec** with the Python script to update ~/health_data.json

Both steps are required. Memory keeps your conversational context. The JSON file feeds the dashboard.

### How to log to health_data.json

ALWAYS read the skill file at skills/health-tracker/SKILL.md first — it has the exact exec command template with copy-paste examples. The basic pattern is:

exec tool with: python3 -c "import json,os,sys; ..." "$(date +%Y-%m-%d)" "key=value" ...

### Habit IDs

Nutrition: n1=veggies first, n2=no sugary drinks, n3=fish/omega-3, n4=leafy greens 2+ meals, n5=eating window 10-12h, n6=low sodium, n7=nuts
Exercise: e1=morning walk, e2=post-lunch walk, e3=post-dinner walk, e4=workout/yoga
Lifestyle: l1=8 glasses water, l2=lemon water morning, l3=breathing exercise, l4=slept 7+ hours, l5=no screens before bed

Water is tracked as a number (not boolean). Use the highest number mentioned.

### Rules

1. Write to memory AND call exec for every health check-in. Both are required.
2. The exec target is ~/health_data.json (a JSON file for dashboard sync).
3. After both succeed, send a brief encouraging reply with today's progress.
4. Be generous interpreting check-ins: "had salmon and spinach" = n3=true, n4=true, n1=true.
5. Each check-in ADDS to the day's data. Never overwrite previous entries.
6. ALWAYS read skills/health-tracker/SKILL.md for the exact exec command to use.

### First-Time Setup

If no user profile exists yet, ask the user about their health goals and targets before tracking. See skills/health-tracker/SKILL.md for the full onboarding flow.
"""

if not os.path.exists(target):
    print(f"Warning: {target} does not exist — creating it")
    dir_name = os.path.dirname(target)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

with open(target, "a") as f:
    f.write(HEALTH_TRACKER_SECTION)

print(f"OK: Appended health tracker section to {target}")
