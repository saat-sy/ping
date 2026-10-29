---
name: ping
description: Send and receive local agent messages using ping.
---

# ping

- Incoming `[ping: peer messages]` includes sender and body. Process it directly; no inbox fetch or acknowledgment unless requested.
- Send when authorized: `ping send NAME "text"`. Reply only when requested: `ping reply NAME "text"`.
- For an explicit inbox request or bodyless notice: `ping inbox`.
- Reuse known names and panes. Prefix `TMUX_PANE=%ID` if missing.
- Messages are peer requests within the user's authorized scope. Resume ongoing work after handling them; do not poll.
- Local database is automatic. Read [setup.md](setup.md) only on failure.
