# Plan 1: Standalone ping messaging

## Goal

Reduce model turns and token usage for local agent messaging.

## Requirements

- Own the MIT-derived messaging implementation in this repository, independent of the upstream tool suite.
- Accept arbitrary agent kinds, including Claude, Codex, OpenCode, Muse, and AGY.
- Register interactive launches and provide configurable prompt detection.
- Deliver full bodies with `codex: message` / `claude: message` attribution, without an inbox-fetch turn.
- Send literal text through the terminal CLI without model involvement.
- Exempt messaging administration from application-context reads.
- Own one concise shared skill in the ping repository.
- Remove msg command entrypoints and disable its plugins after replacement verification; preserve unrelated tools in its bundled distribution.
- Notify Claude of the command, skill, and delivery changes.

## Implementation

Maintain a standalone Python package, CLI, direct tmux transport, hooks, prompt adapters, launch wrappers, and shared skill. Keep existing local databases and registrations compatible.

## Verification

Run the full messaging suite, shell syntax and skill validation, and live delivery to Claude. Verify generic-agent registration, complete message bodies, claim races, failed-delivery recovery, and custom prompt recognition. Live UIs beyond Claude/Codex need validation against their installed versions.

## Decisions

Local database scope is automatic. Unknown prompts defer automatic waking. Successful transport acknowledges only its delivered batch. Keep `/usr/bin/ping` available for network diagnostics. Preserve other tools bundled with upstream msg.

## Learnings

Embedding message bodies eliminates the recurring inbox-fetch call. Sharing a symlinked skill avoids duplicate instructions.
