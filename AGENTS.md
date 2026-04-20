# OpenCode Config Sync - Agent Instructions

## Project Overview

**What**: A CLI tool to sync OpenCode configuration files across multiple machines using a private GitHub repository.

**Why**: Users need to maintain consistent OpenCode settings (config, custom skills) across different development machines without manual copying.

**Target Users**: OpenCode users with multiple machines who want automated config synchronization.

## Critical Context

- **Language**: Python 3.8+ (user is most familiar with Python)
- **Distribution**: Designed for `uvx` execution (no local installation required)
- **Authentication**: SSH keys only (user already has SSH setup)
- **UI Language**: All user-facing text must be in English
- **Conflict Strategy**: Interactive manual resolution (prompt user to choose)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Machine                         │
│                                                              │
│  ┌──────────────┐         ┌─────────────────┐              │
│  │ OpenCode     │         │ Config Sync     │              │
│  │ Config Files │◄────────│ Tool (Python)   │              │
│  └──────────────┘         └────────┬────────┘              │
│                                    │                         │
│                                    │ Git Operations          │
│                                    │ (GitPython)             │
│                                    ▼                         │
│                           ┌─────────────────┐               │
│                           │ Local Git Repo  │               │
│                           │ (~/.config/     │               │
│                           │  opencode-sync/ │               │
│                           │  repo/)         │               │
│                           └────────┬────────┘               │
└────────────────────────────────────┼──────────────────────────┘
                                     │
                                     │ SSH (git@github.com)
                                     │
                          ┌──────────▼──────────┐
                          │  GitHub Private     │
                          │  Repository         │
                          │  (opencode-config)  │
                          └─────────────────────┘
```

## Project Structure

```
configsync/
├── AGENTS.md                    # This file
├── README.md                    # User documentation
├── LICENSE                      # MIT License
├── pyproject.toml              # Project config, dependencies, entry points
├── .gitignore                  # Python/IDE ignores
├── src/
│   └── opencode_sync/
│       ├── __init__.py         # Package init, version
│       ├── __main__.py         # Entry point for `python -m opencode_sync`
│       ├── cli.py              # CLI interface (Click), command routing
│       ├── core.py             # Core sync logic, main orchestration
│       ├── git_ops.py          # Git operations wrapper (GitPython)
│       ├── conflict.py         # Conflict detection and resolution UI
│       ├── config.py           # Tool configuration management
│       ├── github.py           # GitHub repo creation (gh CLI detection)
│       └── utils.py            # Helpers (path expansion, logging, etc.)
└── tests/
    ├── __init__.py
    ├── test_core.py
    ├── test_git_ops.py
    └── test_config.py
```

## Tech Stack & Dependencies

**Core Dependencies** (declared in `pyproject.toml`):
- `gitpython>=3.1.0` - Git operations
- `click>=8.0.0` - CLI framework (modern, better than argparse)
- `rich>=13.0.0` - Beautiful terminal output (tables, colors, prompts)

**Why these choices**:
- GitPython: Most mature Python Git library, handles SSH automatically
- Click: Cleaner syntax than argparse, better help generation
- Rich: Makes CLI output professional and readable

**Standard library usage**:
- `pathlib` - Path manipulation
- `json` - Config file handling
- `subprocess` - For `gh` CLI detection
- `shutil` - File operations

## Synced Files (Default)

```
~/.config/opencode/opencode.json       # Main OpenCode config
~/.agents/skills/                      # Custom skills directory
~/.agents/.skill-lock.json            # Skills lock file
```

**Important**: Tool config stored separately at `~/.config/opencode-sync/config.json` to avoid circular sync.

## Commands Reference

### Core Commands (Phase 1 - MVP)

```bash
# Initialize sync (first time setup)
opencode-sync init
ocs init

# Initialize with existing repo
opencode-sync init --repo git@github.com:user/opencode-config.git
ocs init --repo URL

# Push local config to remote (auto-pulls first)
opencode-sync push
ocs push

# Pull remote config to local
opencode-sync pull
ocs pull

# Show sync status
opencode-sync status
ocs status

# Show diff between local and remote
opencode-sync diff
ocs diff
```

### Entry Points Configuration

In `pyproject.toml`:
```toml
[project.scripts]
opencode-sync = "opencode_sync.cli:main"
ocs = "opencode_sync.cli:main"
```

Both commands point to the same function, allowing users to use either name.

## User Workflows

### First Machine Setup

```bash
# User runs init
ocs init

# Tool checks:
# 1. Is `gh` CLI installed and authenticated?
#    - YES: Auto-create private repo `opencode-config`
#    - NO: Show instructions (see GitHub Integration section)
# 2. Clone/init local git repo at ~/.config/opencode-sync/repo/
# 3. Copy current OpenCode config files to repo
# 4. Commit and push to GitHub
# 5. Save tool config with repo URL
```

### Second Machine Setup

```bash
# User runs init with repo URL
ocs init --repo git@github.com:username/opencode-config.git

# Tool:
# 1. Clone repo to ~/.config/opencode-sync/repo/
# 2. Copy files from repo to OpenCode config locations
# 3. Save tool config with repo URL
```

### Daily Usage

```bash
# Before making changes
ocs pull

# After editing opencode.json or skills
ocs push  # Auto-pulls first, checks for conflicts
```

### Shell Integration (Optional)

User can add to `.zshrc`:
```bash
# Alias for convenience
alias ocs='uvx opencode-sync'

# Auto-pull before launching OpenCode
function opencode() {
    ocs pull --quiet 2>/dev/null || true
    command opencode "$@"
}
```

## GitHub Integration

### Auto-Creation (Preferred)

If `gh` CLI is installed and authenticated:
```bash
gh repo create opencode-config --private --source=. --push
```

### Manual Creation (Fallback)

If `gh` not available, show user:
```
GitHub CLI not found. Please choose:

[1] Install GitHub CLI (Recommended)
    macOS:  brew install gh
    Linux:  See https://cli.github.com/
    Then:   gh auth login
    Finally: Run 'ocs init' again

[2] Create repository manually
    1. Go to https://github.com/new
    2. Repository name: opencode-config
    3. Visibility: Private ✓
    4. Do NOT initialize with README
    5. Click "Create repository"
    6. Copy the SSH URL (git@github.com:...)
    7. Run: ocs init --repo <SSH_URL>

[3] Cancel
```

## Conflict Resolution

### Detection

Conflicts occur when:
- Local and remote both modified since last sync
- Git merge fails (different changes to same file)

### Resolution Flow

```python
# Pseudo-code for conflict handling
if detect_conflict():
    show_conflict_info()  # timestamps, file names
    choice = prompt_user([
        "1. Keep local (push and overwrite remote)",
        "2. Use remote (discard local changes)", 
        "3. Show diff",
        "4. Backup local and use remote",
        "5. Cancel"
    ])
    
    if choice == 1:
        git_push_force()
    elif choice == 2:
        git_reset_hard_origin()
    elif choice == 3:
        show_diff()
        # Loop back to prompt
    elif choice == 4:
        backup_local()  # to ~/.config/opencode/backups/
        git_reset_hard_origin()
    else:
        abort()
```

### Backup Strategy

When overwriting local config:
- Create backup at `~/.config/opencode/backups/opencode.json.TIMESTAMP`
- Keep last 10 backups (configurable)
- Show backup location to user

## Configuration Management

### Tool Config Location

`~/.config/opencode-sync/config.json`

### Config Schema

```json
{
  "version": "1.0",
  "repo_url": "git@github.com:username/opencode-config.git",
  "sync_paths": [
    "~/.config/opencode/opencode.json",
    "~/.agents/skills/",
    "~/.agents/.skill-lock.json"
  ],
  "backup": {
    "enabled": true,
    "max_backups": 10,
    "location": "~/.config/opencode/backups/"
  },
  "git": {
    "user_name": "Auto-detected from git config",
    "user_email": "Auto-detected from git config"
  }
}
```

### Config Initialization

On first run:
1. Create `~/.config/opencode-sync/` directory
2. Auto-detect git user.name and user.email
3. Use default sync_paths
4. Save config

## Git Operations Details

### Repository Location

Local git repo: `~/.config/opencode-sync/repo/`

This is separate from OpenCode config to:
- Avoid polluting OpenCode config directory with `.git/`
- Allow clean file copying
- Simplify git operations

### Sync Process

**Push**:
```python
1. Copy files from OpenCode locations to repo/
2. git add .
3. git commit -m "Update config from {hostname} at {timestamp}"
4. git fetch origin
5. Check if remote has new commits
   - YES: Attempt merge, handle conflicts if any
   - NO: Proceed
6. git push origin main
```

**Pull**:
```python
1. git fetch origin
2. Check if local has uncommitted changes
   - YES: Stash or warn user
   - NO: Proceed
3. git pull origin main
4. Copy files from repo/ to OpenCode locations
5. Show what changed
```

### SSH Key Detection

Tool assumes SSH keys are already configured. If push/pull fails with auth error:
```
SSH authentication failed.

Please ensure:
1. You have an SSH key: ls ~/.ssh/id_*.pub
2. Your public key is added to GitHub:
   - Go to https://github.com/settings/keys
   - Click "New SSH key"
   - Paste contents of: cat ~/.ssh/id_ed25519.pub
3. Test connection: ssh -T git@github.com

For help: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
```

## Error Handling

### Common Errors

1. **No git config**: Prompt user to set `git config --global user.name/email`
2. **SSH auth failure**: Show SSH setup instructions
3. **Network error**: Suggest checking internet connection
4. **Repo not found**: Verify repo URL, check if repo exists
5. **Merge conflict**: Enter conflict resolution flow
6. **No OpenCode config found**: Warn user, offer to create empty config

### Logging

- Log file: `~/.config/opencode-sync/sync.log`
- Log level: INFO by default, DEBUG with `--verbose` flag
- Log rotation: Keep last 5 log files, max 1MB each

## Implementation Phases

### Phase 1: MVP (Current Goal)

**Scope**: Basic sync functionality with manual commands

**Features**:
- ✅ `init` command (with gh CLI auto-creation)
- ✅ `push` command (with auto-pull and conflict detection)
- ✅ `pull` command
- ✅ `status` command
- ✅ `diff` command
- ✅ Interactive conflict resolution
- ✅ SSH authentication
- ✅ Config management
- ✅ Rich terminal UI

**Deliverables**:
- Working Python package
- `pyproject.toml` with correct entry points
- Basic tests
- README with usage instructions
- This AGENTS.md file

### Phase 2: Automation (Future)

**Scope**: Reduce manual intervention

**Options**:
- **Option A**: Cron-based periodic sync
  - `ocs install-cron` - Set up cron job to run `ocs pull` every 5 minutes
  - No daemon process needed
  - Simple and reliable
  
- **Option B**: File watcher (requires pip install)
  - Watch OpenCode config files for changes
  - Auto-push after 30-second debounce
  - Requires long-running process
  - Not compatible with `uvx` (needs `pip install` or `pipx install`)

**Recommendation**: Start with Option A (cron) for simplicity.

### Phase 3: OpenCode Integration (Future)

**Goal**: Seamless integration with OpenCode itself

**Options**:

1. **OpenCode Startup Hook**
   - Investigate OpenCode's plugin/hook system
   - Auto-pull config on OpenCode startup
   - Requires OpenCode API/plugin support

2. **OpenCode Plugin**
   - Full-featured plugin with UI
   - In-app sync status and controls
   - Requires learning OpenCode plugin development

3. **OpenCode Config Integration**
   - Add sync settings to `opencode.json`
   - OpenCode natively handles sync
   - Requires OpenCode core changes (unlikely)

**Next Steps**:
- Research OpenCode plugin documentation
- Check if OpenCode has startup hooks
- Engage with OpenCode community for best approach

## Development Guidelines

### Code Style

- Follow PEP 8
- Use type hints for all functions
- Docstrings for all public functions (Google style)
- Max line length: 100 characters

### Testing

- Use `pytest` for testing
- Mock git operations in tests (don't hit real GitHub)
- Test conflict resolution logic thoroughly
- Test path expansion (~/ handling)

### Git Commit Messages

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Example: `feat: add interactive conflict resolution`

### Release Process

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. (Future) Publish to PyPI: `python -m build && twine upload dist/*`

## Key Design Decisions

### Why Python over Shell/Go/TypeScript?

- **Python**: User is most familiar, rich ecosystem, GitPython is mature
- **Shell**: Too fragile for complex logic, poor error handling
- **Go**: User doesn't know Go, overkill for this tool
- **TypeScript**: Would align with OpenCode, but adds Node.js dependency

### Why uvx over pip install?

- **uvx**: Zero installation, always latest version, no environment pollution
- **pip install**: Requires manual updates, can conflict with system Python
- **Trade-off**: Can't run long-lived processes (no daemon mode in Phase 1)

### Why SSH over HTTPS?

- **SSH**: User already has keys, no token management, more secure
- **HTTPS**: Requires Personal Access Token, token rotation hassle
- **Trade-off**: Users must set up SSH keys (but most devs already have)

### Why Interactive Conflict Resolution?

- **Interactive**: User has full control, no data loss risk
- **Auto-resolve**: Could lose important changes, dangerous
- **Trade-off**: Requires user attention, not fully automated

### Why Separate Git Repo Location?

- **Separate** (`~/.config/opencode-sync/repo/`): Clean, no `.git/` pollution
- **In-place**: Would put `.git/` in `~/.config/opencode/`, messy
- **Trade-off**: Extra file copying, but cleaner architecture

## Common Pitfalls for Agents

### Path Handling

❌ **Wrong**: `os.path.join("~/.config", "opencode")`
✅ **Right**: `Path("~/.config/opencode").expanduser()`

Always use `pathlib.Path` and call `.expanduser()` for `~/` paths.

### Git Operations

❌ **Wrong**: `subprocess.run(["git", "push"])`
✅ **Right**: `repo.remote("origin").push()`

Use GitPython's API, not subprocess. It handles SSH keys automatically.

### Config File Paths

❌ **Wrong**: Hardcode `/Users/username/.config/`
✅ **Right**: Use `Path.home() / ".config"`

Never hardcode home directory paths.

### Error Messages

❌ **Wrong**: `print("Error: something failed")`
✅ **Right**: Use Rich console with proper formatting and actionable instructions

Always provide context and next steps in error messages.

### Testing Git Operations

❌ **Wrong**: Test against real GitHub repo
✅ **Right**: Mock GitPython objects or use temporary local repos

Never hit external services in tests.

## Quick Start for Agents

When working on this project:

1. **Read this file first** - Don't guess the architecture
2. **Check existing code** - Follow established patterns
3. **Test locally** - Use `python -m opencode_sync` for testing
4. **Use type hints** - Makes code self-documenting
5. **Handle errors gracefully** - Show helpful messages with Rich
6. **Update this file** - If architecture changes, update AGENTS.md

## Resources

- GitPython docs: https://gitpython.readthedocs.io/
- Click docs: https://click.palletsprojects.com/
- Rich docs: https://rich.readthedocs.io/
- GitHub CLI: https://cli.github.com/
- OpenCode docs: https://opencode.ai/docs

## Questions for User (If Needed)

Before implementing, confirm:
- [ ] Default repo name `opencode-config` is acceptable
- [ ] Backup location `~/.config/opencode/backups/` is acceptable
- [ ] Max 10 backups is reasonable
- [ ] Commit message format is clear enough

---

**Last Updated**: 2026-04-20
**Project Status**: Phase 1 (MVP) - Ready to implement
**Next Step**: Create `pyproject.toml` and basic project structure
