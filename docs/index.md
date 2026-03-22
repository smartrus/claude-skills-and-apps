# Claude Skills & Apps

A curated collection of production-ready skills and apps for Claude Code, Cowork, and compatible AI tools.

## Getting Started

Browse the [Skill Catalog](skills.md) or [App Catalog](apps.md) to find what you need, or create your own using the scaffolding scripts.

### Use a Skill

```bash
# Copy a skill into your Claude Code project
cp -r skills/engineering/pr-review ~/.claude/commands/
```

### Create a New Skill

```bash
./scripts/new-skill.sh engineering my-new-skill
```

### Create a New App

```bash
./scripts/new-app.sh dashboards my-dashboard
```

## Repository Structure

```
claude-skills-and-apps/
├── skills/           # Reusable prompt modules by domain
│   ├── engineering/
│   ├── marketing/
│   ├── product/
│   ├── operations/
│   ├── data/
│   └── design/
├── apps/             # Standalone tools and dashboards
│   ├── dashboards/
│   ├── tools/
│   └── automations/
├── scripts/          # Scaffolding and validation tools
└── docs/             # This documentation site
```

## Contributing

We welcome contributions! See the [Contributing Guide](contributing.md) for details.
