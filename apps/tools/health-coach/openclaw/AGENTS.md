# Health Tracker — ALWAYS ACTIVE

The user has a health habits tracking system. When they mention ANYTHING about water, food, meals, walking, exercise, yoga, breathing, sleep, or screens — you MUST do TWO things:

1. **Write to memory** as you normally would (daily check-in notes in memory files)
2. **ALSO call exec** with the Python script below to update ~/health_data.json

Both steps are required. Memory keeps your conversational context. The JSON file feeds the dashboard.

## How to log to health_data.json

Call the exec tool with this Python command (replace the arguments based on what the user reported):

```
exec command: python3 -c "
import json,os,sys
f=os.path.expanduser('~/health_data.json')
data={}
if os.path.exists(f):
  try:
    with open(f) as fh: data=json.load(fh)
  except (json.JSONDecodeError,ValueError): data={}
date=sys.argv[1]
day=data.setdefault(date,{'habits':{},'water':0,'notes':''})
for k,v in (p.split('=',1) for p in sys.argv[2:]):
  if k=='water':
    day['water']=max(day['water'],int(v))
    if day['water']>=8: day['habits']['l1']=True
  elif k=='notes': day['notes']=(day['notes']+' | '+v).strip(' | ')
  else:
    new_val=v.lower() in ('true','1','yes')
    cur_val=day['habits'].get(k)
    if new_val or not cur_val: day['habits'][k]=new_val
with open(f,'w') as fh: json.dump(data,fh,indent=2)
print('Updated',date,json.dumps(day))
" "$(date +%Y-%m-%d)" "n3=true" "e2=true" "water=7" "notes=Salmon for lunch"
```

Or read the skill file at `skills/health-tracker/SKILL.md` for the full reference with copy-paste examples.

## Habit IDs

Nutrition: n1=veggies first, n2=no sugary drinks, n3=fish/omega-3, n4=leafy greens 2+ meals, n5=eating window 10-12h, n6=low sodium, n7=nuts
Exercise: e1=morning walk, e2=post-lunch walk, e3=post-dinner walk, e4=workout/yoga
Lifestyle: l1=water goal met (derived: set true when water ≥ 8; adjust in exec template if user's goal differs), l2=lemon water morning, l3=breathing exercise, l4=slept 7+ hours, l5=no screens before bed

Water is tracked as a number (not boolean). Use the highest number mentioned.

## Rules

1. Write to memory AND call exec for every health check-in. Both are required.
2. The exec target is ~/health_data.json (a JSON file for dashboard sync).
3. After both succeed, send a brief encouraging reply with today's progress.
4. Be generous interpreting check-ins: "had salmon and spinach" = n3=true, n4=true, n1=true.
5. Each check-in ADDS to the day's data. Never overwrite previous entries.
6. ALWAYS read skills/health-tracker/SKILL.md for the exact exec command to use.

## First-Time Setup

If no user profile exists yet, ask the user about their health goals and targets before tracking. See skills/health-tracker/SKILL.md for the full onboarding flow.
