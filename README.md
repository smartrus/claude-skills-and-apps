# Claude Skills & Apps

A curated collection of production-ready skills and apps for Claude Code, Cowork, and compatible AI tools.

## What's Inside

This repository is organized into two top-level categories:

### Skills

Reusable prompt-based modules that give Claude specialized expertise in a domain. Each skill is a self-contained folder with a `SKILL.md` and optional supporting files.

| Domain | Description |
|---|---|
| `skills/engineering/` | Development workflows, code review, architecture, debugging |
| `skills/marketing/` | Content creation, SEO, campaigns, brand voice |
| `skills/product/` | Specs, roadmaps, sprint planning, research synthesis |
| `skills/operations/` | Process docs, runbooks, status reports, compliance |
| `skills/data/` | SQL, analysis, visualization, dashboards |
| `skills/design/` | UX copy, accessibility, design systems, critique |

### Apps

Standalone applications, dashboards, and tools built with Claude — ready to run or adapt.

| Category | Description |
|---|---|
| `apps/dashboards/` | Interactive HTML/React dashboards and reports |
| `apps/tools/` | CLI utilities, scripts, and automation tools |
| `apps/automations/` | Scheduled tasks, workflows, and integrations |

## Quick Start

**Use a skill** — copy a skill folder into your Claude Code project or Cowork session:

```bash
# Example: use the PR review skill
cp -r skills/engineering/pr-review ~/.claude/commands/
```

**Run an app** — follow the README inside each app folder for setup instructions.

**Create your own** — use the scaffolding script:

```bash
# Create a new skill
./scripts/new-skill.sh engineering my-new-skill

# Create a new app
./scripts/new-app.sh tools my-new-app
```

## Skill Structure

Every skill follows this structure:

```
skills/<domain>/<skill-name>/
├── SKILL.md              # Main skill definition (required)
├── scripts/              # Supporting scripts (optional)
│   └── *.py / *.sh
├── references/           # Frameworks, best practices (optional)
│   └── *.md
└── assets/               # Templates, examples (optional)
    └── *.*
```

The `SKILL.md` must include YAML frontmatter:

```yaml
---
name: Skill Name
description: One-line description of what this skill does
version: "1.0.0"
author: Your Name
tags: [domain, category, keywords]
triggers: [phrases, that, activate, this, skill]
tools_required: [Read, Write, Bash]  # optional
---
```

## App Structure

Every app follows this structure:

```
apps/<category>/<app-name>/
├── README.md             # Setup, usage, and configuration (required)
├── src/                  # Source code
│   └── *.*
├── assets/               # Static assets (optional)
│   └── *.*
└── tests/                # Tests (optional)
    └── *.*
```

## Contributing

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting.

Key rules:

- PRs must target the `dev` branch (PRs to `main` are auto-closed)
- Every skill needs a `SKILL.md` with valid YAML frontmatter
- Every app needs a `README.md` with setup instructions
- No placeholder code — submissions must be production-ready
- Run `./scripts/lint.sh` before submitting

## Development

```bash
# Clone the repo
git clone https://github.com/smartrus/claude-skills-and-apps.git
cd claude-skills-and-apps

# Create a feature branch from dev
git checkout dev
git checkout -b feat/my-new-skill

# Scaffold a new skill or app
./scripts/new-skill.sh <domain> <name>
./scripts/new-app.sh <category> <name>

# Validate your changes
./scripts/lint.sh

# Push and open a PR against dev
git push -u origin feat/my-new-skill
```

## License

MIT — see [LICENSE](LICENSE) for details.
