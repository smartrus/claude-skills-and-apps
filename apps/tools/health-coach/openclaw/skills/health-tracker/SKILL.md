---
name: health-tracker
description: "Parse natural-language health check-ins and log them to ~/health_data.json for dashboard sync. Activate when the user mentions food, water, walking, exercise, yoga, breathing, sleep, or screens."
version: 1.1.0
---

# Health Tracker Skill (OpenClaw)

Parse health check-in messages and update ~/health_data.json via the exec tool.

## Exec Command Template

Use this exact pattern — replace the arguments based on what was reported:

```
python3 -c "
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
" "$(date +%Y-%m-%d)" "ARGS_HERE"
```

### Examples

Logged a salad with fish and a walk:
```
"$(date +%Y-%m-%d)" "n1=true" "n3=true" "n4=true" "e2=true" "water=4" "notes=Salmon spinach salad, post-lunch walk"
```

Morning check-in with water and walk:
```
"$(date +%Y-%m-%d)" "l2=true" "e1=true" "notes=Lemon water, 40 min morning walk"
```

Evening recap:
```
"$(date +%Y-%m-%d)" "e3=true" "l3=true" "l5=true" "water=8" "notes=Evening walk done, breathing exercise, no screens"
```

## Habit IDs

| ID | Habit | Common triggers |
|----|-------|----------------|
| n1 | Veggies first | "salad", "ate veggies", "greens first" |
| n2 | No sugary drinks | "just water", "black coffee" |
| n3 | Fish / omega-3 | "salmon", "tuna", "fish oil" |
| n4 | Leafy greens 2+ meals | "spinach", "kale", "arugula" |
| n5 | Eating window 10-12h | "stopped eating by 7" |
| n6 | Low sodium | "cooked at home", "no processed food" |
| n7 | Nuts | "almonds", "walnuts", "handful of nuts" |
| e1 | Morning walk | "morning walk", "walked before work" |
| e2 | Post-lunch walk | "walked after lunch" |
| e3 | Post-dinner walk | "evening walk" |
| e4 | Workout / yoga | "did yoga", "gym", "home workout" |
| l1 | Met water goal (8) | Infer from water count |
| l2 | Lemon water AM | "lemon water", "warm water this morning" |
| l3 | Breathing exercise | "breathing", "meditation" |
| l4 | Slept 7+ hours | "slept 8 hours", "good sleep" |
| l5 | No screens before bed | "no phone tonight" |

## Parsing Rules

- Be generous: "had salmon and spinach" = n3, n4, n1
- Negatives matter: "skipped breathing" = do NOT mark l3
- Each check-in ADDS — never overwrite previous entries
- Water is a number, not boolean — use the highest mentioned
- Infer walk type from time of day if not explicit

## Reply Format

- Max 4-5 lines (user is on their phone)
- Never show habit IDs
- Show today's progress fraction and percentage
- Be brief and encouraging
