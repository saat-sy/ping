# ping

Direct, attributed messages between terminal agents. Bodies arrive as `codex: message` or `claude: message`, without an inbox-fetch turn.

```sh
uv tool install --editable .
ping launch --agent claude -- claude
ping launch --agent opencode -- opencode
ping send NAME "hello"
ping say NAME "hello" --from SENDER
```

Requires Python 3.11+ and tmux. Any agent name is accepted; custom prompts may need an [adapter](docs/adapters.md). Use `/usr/bin/ping` for network diagnostics.

[Shared agent skill](skill/SKILL.md). Local databases stay in `.msg/`.

Derived from **msg** in [claude-code-tools](https://github.com/pchalasani/claude-code-tools) by Prasad Chalasani. [MIT license](LICENSE).
