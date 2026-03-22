# Contributing to Claude Skills & Apps

Thanks for your interest in contributing! This guide covers everything you need to know.

## Branch Model

This repository uses a two-branch workflow:

- **`dev`** — active development branch. All PRs must target this branch.
- **`main`** — stable releases only. Periodically updated from `dev`.

**PRs targeting `main` will be automatically closed.** Always branch from and target `dev`.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/<you>/claude-skills-and-apps.git`
3. Add upstream: `git remote add upstream https://github.com/smartrus/claude-skills-and-apps.git`
4. Create a feature branch from `dev`: `git checkout dev && git checkout -b feat/my-skill`

## What You Can Contribute

### Skills

A skill is a self-contained prompt module that gives Claude specialized expertise. To add one:

1. Scaffold it: `./scripts/new-skill.sh <domain> <skill-name>`
2. Edit the generated `SKILL.md` — fill in the frontmatter and prompt content
3. Optionally add `scripts/`, `references/`, or `assets/`
4. Run `./scripts/lint.sh` to validate

**Skill requirements:**

- `SKILL.md` with valid YAML frontmatter (name, description, version, author, tags, triggers)
- Production-ready content — no placeholders, no "TODO" stubs
- Clear trigger phrases so the skill activates correctly
- If including scripts: use Python stdlib only (zero external dependencies), include `--help`, handle errors gracefully

### Apps

An app is a standalone tool, dashboard, or automation. To add one:

1. Scaffold it: `./scripts/new-app.sh <category> <app-name>`
2. Write the source code in `src/`
3. Document setup and usage in `README.md`
4. Add tests if applicable

**App requirements:**

- `README.md` with clear setup instructions, dependencies, and usage examples
- Working code — the app must actually run
- Pin dependency versions if using external packages
- Include a screenshot or demo if it has a UI

## Quality Standards

All contributions are checked by CI. Before submitting:

- [ ] `SKILL.md` or `README.md` has valid YAML frontmatter
- [ ] No broken internal links
- [ ] No secrets, credentials, or API keys in any file
- [ ] Scripts are executable and include error handling
- [ ] Lint passes: `./scripts/lint.sh`

## Commit Messages

Use conventional commit format:

```
feat(engineering): add pr-review skill
fix(data): correct SQL dialect detection in query-writer
docs: update contributing guide
chore: add linting for app frontmatter
```

Format: `<type>(<scope>): <description>`

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

## Pull Request Process

1. Fill out the PR template completely
2. Ensure CI checks pass (quality gate, lint, security scan)
3. One approval required from a maintainer
4. Squash-and-merge is preferred for clean history

## What Gets Rejected

- Generic advice dressed up as a skill (must provide specific, actionable expertise)
- Placeholder or stub code
- Duplicate skills that overlap significantly with existing ones
- Content that promotes unethical practices
- Skills with proprietary or copyrighted content
- Apps with hardcoded secrets or credentials

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful, constructive, and collaborative.

## Questions?

Open a [Discussion](https://github.com/smartrus/claude-skills-and-apps/discussions) or file an issue. We're happy to help!
