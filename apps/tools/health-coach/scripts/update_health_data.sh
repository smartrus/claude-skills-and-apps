#!/bin/bash
# update_health_data.sh — Update the health habits JSON data file
#
# Usage:
#   ./update_health_data.sh <date> <habit_id> <value>
#
# Examples:
#   ./update_health_data.sh 2026-03-22 n1 true       # Mark "veggies first" as done
#   ./update_health_data.sh 2026-03-22 water 6        # Set water count to 6
#   ./update_health_data.sh 2026-03-22 notes "Salmon bowl for lunch"
#
# Override default data file location:
#   HEALTH_DATA_FILE=/path/to/data.json ./update_health_data.sh ...

set -euo pipefail

DATA_FILE="${HEALTH_DATA_FILE:-$(dirname "$0")/../data/health_data.json}"
DATA_DIR="$(dirname "$DATA_FILE")"

# Validate arguments
if [ $# -lt 3 ]; then
  echo "Usage: $0 <date> <habit_id> <value>"
  echo "  date:     YYYY-MM-DD format"
  echo "  habit_id: n1-n7, e1-e4, l1-l5, water, or notes"
  echo "  value:    true/false for habits, number for water, text for notes"
  exit 1
fi

DATE="$1"
HABIT_ID="$2"
VALUE="$3"

# Validate date format
if ! [[ "$DATE" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
  echo "Error: Date must be in YYYY-MM-DD format. Got: $DATE"
  exit 1
fi

# Create data directory and file if they don't exist
mkdir -p "$DATA_DIR"
if [ ! -f "$DATA_FILE" ]; then
  echo '{}' > "$DATA_FILE"
fi

# Update the JSON file using Python (stdlib only, no dependencies)
# Pass values via sys.argv to prevent code injection
python3 - "$DATE" "$HABIT_ID" "$VALUE" "$DATA_FILE" << 'PYEOF'
import json
import sys
import os

date, habit_id, value, data_file = sys.argv[1:5]

try:
    with open(data_file, "r") as f:
        data = json.load(f)
except json.JSONDecodeError:
    # Backup corrupted file before resetting
    backup_path = data_file + ".bak"
    try:
        os.replace(data_file, backup_path)
        print(f"Warning: Corrupted JSON backed up to {backup_path}")
    except OSError:
        pass
    data = {}
except FileNotFoundError:
    data = {}

# Initialize day entry if needed
if date not in data:
    data[date] = {"habits": {}, "water": 0, "notes": ""}

day = data[date]
for field in ("habits", "water", "notes"):
    if field not in day:
        day[field] = {} if field == "habits" else (0 if field == "water" else "")

# Update based on habit type
if habit_id == "water":
    try:
        new_water = int(value)
        day["water"] = max(day["water"], min(new_water, 20))
        print(f"Water updated to {day['water']}")
    except ValueError:
        print(f"Error: Water value must be a number. Got: {value}", file=sys.stderr)
        sys.exit(1)
elif habit_id == "notes":
    if day["notes"]:
        day["notes"] += " | " + value
    else:
        day["notes"] = value
    print(f"Note added: {value}")
else:
    is_true = value.lower() in ("true", "1", "yes", "done")
    day["habits"][habit_id] = is_true
    status = "done" if is_true else "not done"
    print(f"Habit {habit_id} set to {status}")

# Derive l1 from water count (l1 = met water goal)
water_goal = 8
day["habits"]["l1"] = day["water"] >= water_goal

# Write back
with open(data_file, "w") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Calculate today's progress — l1 is derived from water, included in count
all_habit_ids = [
    "n1", "n2", "n3", "n4", "n5", "n6", "n7",
    "e1", "e2", "e3", "e4",
    "l1", "l2", "l3", "l4", "l5"
]
done_count = sum(1 for h in all_habit_ids if day["habits"].get(h, False))
total = len(all_habit_ids)
progress = done_count / total * 100 if total > 0 else 0

print(f"Today's progress: {done_count}/{total} ({progress:.0f}%)")
PYEOF
