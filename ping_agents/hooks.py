"""Hook commands for msg inter-agent communication.

Provides SessionStart and SessionEnd hooks that register and
retire the agent's pane, and Stop and UserPromptSubmit hooks
that check for unread messages and inject notifications into
the agent's context. Used by both Claude Code and Codex CLI.

Both hooks use the same claim protocol as the watcher
to prevent double-notification.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

import click

from .models import _new_uuid
from . import cli as msg_cli, notifications, sessions
from .store import MsgStore


def _find_self_agent(store: MsgStore) -> object | None:
    """Find the agent registered for this pane."""
    pane_id = os.environ.get("TMUX_PANE")
    if not pane_id:
        return None
    tmux_socket = os.environ.get("TMUX", "").split(",", 1)[0] or None

    try:
        cmd = ["tmux"]
        if tmux_socket:
            cmd += ["-S", tmux_socket]
        cmd += ["display-message", "-t", pane_id, "-p", "#{session_name}"]
        result = subprocess.run(
            cmd,
            capture_output=True, text=True, timeout=5,
        )
        tmux_session = result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    if not tmux_session:
        return None

    matches = [
        agent for agent in store.list_agents(tmux_session, tmux_socket)
        if agent.pane_id == pane_id and agent.tmux_socket == tmux_socket
    ]
    return matches[0] if len(matches) == 1 else None


def _read_hook_input() -> dict:
    try:
        return json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        return {}


def _check_and_notify(
    hook_event: str,
) -> None:
    """Common logic for both Stop and UserPromptSubmit.

    Checks the DB for unread messages, claims deliveries,
    and outputs a JSON response.
    """
    try:
        store = MsgStore(msg_cli._get_db_path())
    except Exception:
        _approve()
        return

    me = _find_self_agent(store)
    if not me:
        _approve()
        return

    # Claim deliveries (same protocol as watcher)
    claimer_id = f"hook-{hook_event}-{_new_uuid()[:8]}"
    claimed = store.claim_pending_deliveries(
        claimer_id, recipient_id=me.session_id,
    )
    if not claimed:
        _approve()
        return

    notification = notifications.format_deliveries(claimed)

    # Output with additionalContext
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": hook_event,
            "additionalContext": notification,
        }
    }), flush=True)
    store.mark_read(
        me.session_id, delivery_ids=[item["id"] for item in claimed],
    )
    for item in claimed:
        store.mark_notified(item["id"], claimer_id)


def _approve() -> None:
    """Complete the hook without emitting a client-specific response."""
    pass


@click.group()
def cli() -> None:
    """ping-hook: Hook commands for msg notifications."""
    pass


@cli.command("session-start")
@click.option("--agent", "kind", required=True, help="Agent kind to register.")
def session_start(kind: str) -> None:
    """SessionStart hook — register this pane."""
    cwd = _read_hook_input().get("cwd")
    try:
        sessions.register_pane(MsgStore(msg_cli._get_db_path()), kind, cwd=cwd)
    except Exception as exc:
        # Never block the agent; stdout would also enter its context.
        print(f"ping: registration skipped: {exc}", file=sys.stderr)


@cli.command("session-end")
def session_end() -> None:
    """SessionEnd hook — retire this pane's registration."""
    hook_input = _read_hook_input()
    # /clear starts a new session in the same pane; keep its registration.
    if hook_input.get("reason") == "clear":
        return
    try:
        store = MsgStore(msg_cli._get_db_path())
        me = _find_self_agent(store)
        if me:
            store.retire_agent(me.session_id)
    except Exception as exc:
        # Unread messages keep the registration for the pane's next session.
        print(f"ping: unregister skipped: {exc}", file=sys.stderr)


@cli.command()
def stop() -> None:
    """Stop hook — check inbox when agent stops."""
    _check_and_notify("Stop")


@cli.command("prompt-submit")
def prompt_submit() -> None:
    """UserPromptSubmit hook — check inbox on user input."""
    _check_and_notify("UserPromptSubmit")


def main() -> None:
    """Entry point for msg-hook CLI."""
    cli()


if __name__ == "__main__":
    main()
