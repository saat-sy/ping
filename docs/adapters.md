# Agent adapters

Registration, sending, and inbox access accept any agent kind. Automatic terminal delivery requires an idle, recognized empty prompt. Claude/Codex have dedicated detection; other agents use standalone `❯`, `›`, or `>` prompts. Live OpenCode, Muse, and AGY UIs need validation against their installed versions.

Configure custom prompts in `~/.config/ping/agents.toml` (or `PING_CONFIG`):

```toml
[agents.custom]
empty_prompt = '^READY: *$'
text_prompt = '^READY: +.+$'
```

Match the actual input line. Unrecognized prompts defer delivery; `ping inbox` provides manual recovery. Successful transport marks only its delivered batch read, without proving the model acted on it. Failed transport leaves messages recoverable.

Hook-capable hosts can run `ping-hook prompt-submit` or `ping-hook stop` with JSON containing `cwd` on stdin. They must support structured `hookSpecificOutput.additionalContext` responses. Notifications already contain full bodies.

Link the repository's `skill/` directory into your agent's skill directory. For automatic registration, launch through `ping launch --agent KIND -- EXECUTABLE [args]`; set `MSG_AGENT_NAME` when using multiple agents of one kind.
