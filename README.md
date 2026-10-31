# Claude skills

Personal skills for Claude Code.

## Install

Clone into the personal skills folder so Claude Code picks them up in every project:

```bash
git clone https://github.com/riseongamestudio/claude-skills.git ~/.claude/skills
```

If `~/.claude/skills` already exists, copy just the skill folders you want into it.

## Skills

| Skill | What it does |
|---|---|
| [chatgpt-image-assets](chatgpt-image-assets/SKILL.md) | Handles any image request by driving ChatGPT image generation in Claude's built-in browser: writes one prompt per asset, sends them after your OK, reviews the results (including real transparency and item counts on sprite sheets), downloads them with your OK, and files them into the project. |
