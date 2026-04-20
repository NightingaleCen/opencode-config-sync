# OpenCode Config Sync

Sync your OpenCode configuration across multiple machines using a private GitHub repository.

## Requirements

- Python 3.8+
- SSH key configured with GitHub (`ssh -T git@github.com`)
- GitHub CLI (optional, for automatic repo creation)

## Quick Start

### First Machine

```bash
# Install and initialize
uvx ocs init

# Or with existing repo
uvx ocs init --repo git@github.com:username/opencode-config.git
```

### Another Machine

```bash
uvx ocs init --repo git@github.com:username/opencode-config.git
```

### Daily Usage

```bash
# Pull latest config
uvx ocs pull

# Push your changes
uvx ocs push
```

## Commands

| Command | Description |
|---------|-------------|
| `ocs init` | Initialize sync with a new or existing repo |
| `ocs push` | Push local config to remote (pulls first if remote changed) |
| `ocs pull` | Pull remote config to local |
| `ocs status` | Show sync status |
| `ocs diff` | Show differences between local and remote |

## What Gets Synced

- `~/.config/opencode/opencode.json` - Main OpenCode config
- `~/.agents/skills/` - Custom skills
- `~/.agents/.skill-lock.json` - Skills lock file

## Installation Options

### Recommended: uvx (no install)

```bash
uvx ocs --help
```

### Shell Alias

Add to your `.zshrc`:
```bash
alias ocs='uvx --from opencode-config-sync ocs'
```

## License

MIT