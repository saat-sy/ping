# ping

Direct messages between coding agents running in tmux.

A fork of **msg** from [claude-code-tools](https://github.com/pchalasani/claude-code-tools) by Prasad Chalasani, split into a standalone package.

Claude Code, Codex, and other terminal agents can send each other messages by name. The recipient sees the full message, attributed to its sender, without spending a turn fetching an inbox:

```
[ping: peer messages]
codex: auth module refactor is done, tests pass
```

## How it works

- Each agent registers its tmux pane under a name. The Claude and Codex plugins do this automatically when a session starts, and remove the registration when it exits.
- `ping send` stores the message in a SQLite database. Each tmux session has its own database at `~/.ping/<session name>/msg.db`, so agents in different tmux sessions never see each other.
- A background watcher delivers messages. If the recipient is idle at an empty prompt, the watcher pastes the message into its pane. If it is busy or the user is typing, the agent's `Stop` or `UserPromptSubmit` hook adds the message to its context instead.

## Requirements

- Python 3.11+
- tmux
- [uv](https://docs.astral.sh/uv/) (to install)

## Install

```sh
uv tool install git+https://github.com/saat-sy/ping
```

Then install the plugin for each agent you use:

```sh
claude plugin marketplace add saat-sy/ping && claude plugin install ping@ping
codex plugin marketplace add saat-sy/ping && codex plugin add ping@ping
```

`ping-hook` must be on the `PATH` of non-interactive shells. In Codex, open `/hooks` once and trust ping's hooks.

Codex runs hooks in a shared background server that cannot see the session's tmux pane. Start it with `codex --no-daemon`, or through `ping launch`.

## Usage

Start two agents in panes of the same tmux session. They register as `REPO-KIND`, such as `myapp-claude` and `myapp-codex`:

```sh
ping list                                  # registered agents in this tmux session
ping send myapp-codex "review auth.py"     # send as the agent in this pane
ping send myapp-claude,myapp-codex "sync"  # send to several agents
ping say myapp-codex "hi" --from myapp-claude  # send from a plain terminal
ping inbox                                 # read unread messages by hand
```

Agents learn these commands from the bundled [skill](skills/ping/SKILL.md), which the plugins install.

To run an agent without a plugin, use the launcher. It registers the pane, runs the agent, and unregisters it on exit:

```sh
ping launch --agent opencode -- opencode
```

Panes that close without unregistering are cleaned up on the next `ping list` or `ping send`. Run `ping --help` for the full command list.

## Configuration

| Setting | Default | Purpose |
|---|---|---|
| `MSG_AGENT_NAME` | `REPO-KIND` | Agent name for this pane. Set it when running two agents of the same kind. |
| `MSG_DB_DIR` | `~/.ping` | Root directory for the per-session databases. |
| `PING_CONFIG` | `~/.config/ping/agents.toml` | Prompt patterns for agents other than Claude and Codex. See [adapters](docs/adapters.md). |

## Limitations

- Automatic delivery needs a recognized empty prompt. Claude and Codex are supported out of the box. Other agents may need an [adapter](docs/adapters.md). Until then, messages wait for a hook or `ping inbox`.
- Renaming a tmux session moves it to a new database. Agents already running stay registered in the old one until they restart.
- This `ping` shadows the system `ping` on your `PATH`. Use `/usr/bin/ping` for network diagnostics.

## Development

```sh
uv sync
uv run pytest
```

## License

[MIT](LICENSE), as in the original msg.
