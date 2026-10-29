# Agent adapters

Registration, sending, and inbox access accept any agent kind. Automatic terminal delivery requires an idle, recognized empty prompt. Claude/Codex have dedicated detection; other agents use standalone `❯`, `›`, or `>` prompts. Live OpenCode, Muse, and AGY UIs need validation against their installed versions.

Configure custom prompts in `~/.config/ping/agents.toml` (or `PING_CONFIG`):

```toml
[agents.custom]
empty_prompt = '^READY: *$'
text_prompt = '^READY: +.+$'
```

Match the actual input line. Unrecognized prompts defer delivery; `ping inbox` provides manual recovery. Successful transport marks only its delivered batch read, without proving the model acted on it. Failed transport leaves messages recoverable.

Hook-capable hosts pass JSON containing `cwd` on stdin. `ping-hook session-start --agent KIND` registers the pane at startup and `ping-hook session-end` unregisters it on exit, except for a `clear` reason. `ping-hook prompt-submit` and `ping-hook stop` deliver messages through structured `hookSpecificOutput.additionalContext` responses; notifications already contain full bodies. The Claude and Codex plugins wire these hooks; see `hooks/`. Hooks find the agent through `TMUX_PANE`, so hosts that run hooks outside the agent's pane, like Codex's shared background server, need the launcher or Codex's `--no-daemon`.

`ping launch --agent KIND -- EXECUTABLE [args]` registers the pane, runs the agent, and unregisters it on exit. Hosts without the plugin also link `skills/ping/` into their skill directory. Set `MSG_AGENT_NAME` when using multiple agents of one kind.
