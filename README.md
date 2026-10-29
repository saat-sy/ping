# ping

Direct, attributed messages between terminal agents. Bodies arrive as `codex: message` or `claude: message`, without an inbox-fetch turn.

## Install

```sh
uv tool install git+https://github.com/saat-sy/ping
claude plugin marketplace add saat-sy/ping && claude plugin install ping@ping
codex plugin marketplace add saat-sy/ping && codex plugin add ping@ping
```

Requires Python 3.11+ and tmux, with `ping-hook` on the non-interactive shell's `PATH`. In Codex, open `/hooks` once and trust ping's hooks.

The plugins register each Claude and Codex session in its tmux pane at startup, unregister it on exit, deliver messages, and install the [shared skill](skills/ping/SKILL.md). Panes that close without an exit hook are unregistered on the next `ping list` or `ping send`. Set `MSG_AGENT_NAME` to name a session; the default is `REPO-KIND`.

Agents without plugin hooks register through the launcher:

```sh
ping launch --agent opencode -- opencode
```

## Use

```sh
ping send NAME "hello"
ping say NAME "hello" --from SENDER
```

Any agent name is accepted; custom prompts may need an [adapter](docs/adapters.md). Local databases stay in `.msg/`. Use `/usr/bin/ping` for network diagnostics.

Derived from **msg** in [claude-code-tools](https://github.com/pchalasani/claude-code-tools) by Prasad Chalasani. [MIT license](LICENSE).
