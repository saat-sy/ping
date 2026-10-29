# Plan 1: Standalone ping messaging

## Goal

Reduce model turns and token usage for local agent messaging.

## Requirements

- Own the MIT-derived messaging implementation in this repository, independent of the upstream tool suite.
- Accept arbitrary agent kinds, including Claude, Codex, OpenCode, Muse, and AGY.
- Register sessions at startup and unregister them on exit by default after install, and provide configurable prompt detection.
- Deliver full bodies with `codex: message` / `claude: message` attribution, without an inbox-fetch turn.
- Send literal text through the terminal CLI without model involvement.
- Exempt messaging administration from application-context reads.
- Own one concise shared skill in the ping repository.
- Remove msg command entrypoints and disable its plugins after replacement verification; preserve unrelated tools in its bundled distribution.
- Notify Claude of the command, skill, and delivery changes.

## Implementation

Maintain a standalone Python package, CLI, direct tmux transport, hooks, prompt adapters, launch wrappers, and shared skill. Ship Claude and Codex plugins that wire the lifecycle and delivery hooks and the skill; agents whose hooks cannot see their pane, like Codex's shared background server, register through `ping launch` or Codex's `--no-daemon`. The launcher stays the agent's parent and unregisters it on exit. Retire agents whose tmux pane has closed. Keep one database per tmux session at `~/.ping/<session name>/msg.db`.

## Verification

Run the full messaging suite, shell syntax and skill validation, and live delivery to Claude. Verify generic-agent registration, complete message bodies, claim races, failed-delivery recovery, and custom prompt recognition. Live UIs beyond Claude/Codex need validation against their installed versions.

## Decisions

Database scope is the tmux session, so agents in different tmux sessions stay apart. Unknown prompts defer automatic waking. Successful transport acknowledges only its delivered batch. Keep `/usr/bin/ping` available for network diagnostics. Preserve other tools bundled with upstream msg.

## Learnings

Embedding message bodies eliminates the recurring inbox-fetch call. Sharing a symlinked skill avoids duplicate instructions.
