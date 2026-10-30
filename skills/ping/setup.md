# Setup

Sessions register only on request (`ping register`); the plugin unregisters Claude sessions, and Codex sessions started with `--no-daemon`, on exit. Launcher-based registration uses `ping launch --agent NAME -- EXECUTABLE [args]`. Set `MSG_AGENT_NAME` for multiple same-kind agents.

On failure, batch `ping list` and `tmux list-panes -a -F '#{pane_id} #{pane_current_command} #{pane_current_path}'`. Match the worktree and agent; never guess. Register only missing sessions with `TMUX_PANE=%ID ping register NAME --agent KIND --pane %ID`.

Reuse the resolved pane and names. Do not register or inspect sessions before a normal send.

Custom prompts use `~/.config/ping/agents.toml`; see the repository README. Unrecognized prompts wait for a hook or manual inbox check.
