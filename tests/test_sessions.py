"""Verify arbitrary agents, terminal sends, and delivery failures."""

import asyncio
import os

import pytest
from click.testing import CliRunner

from ping_agents import cli, models, prompt_detect, sessions, store, watcher


@pytest.mark.parametrize("kind", ["claude", "codex", "opencode", "muse", "agy", "custom"])
def test_launch_registers_any_agent_and_reuses_name(monkeypatch, tmp_path, kind):
    db = store.MsgStore(str(tmp_path / ".msg/msg.db"))
    existing = db.register_agent("chosen-name", "%2", "test", models.AgentKind(kind), "/tmp/socket")
    monkeypatch.setattr(cli, "_detect_tmux_pane", lambda: "%2")
    monkeypatch.setattr(cli, "_detect_tmux_session", lambda pane=None: "test")
    monkeypatch.setattr(cli, "_detect_tmux_socket", lambda pane=None: "/tmp/socket")
    monkeypatch.setattr(cli, "_detect_display_addr", lambda pane=None: "test:1.2")
    monkeypatch.setattr(cli, "_prune_closed_panes", lambda store: None)
    monkeypatch.setenv("TMUX_PANE", "%2")
    seen = []

    def run_agent(command):
        seen.append((command, [(a.session_id, a.name) for a in db.list_agents("test")]))
        return 3

    monkeypatch.setattr(sessions.subprocess, "call", run_agent)
    monkeypatch.setattr(sessions.signal, "signal", lambda *args: None)

    with pytest.raises(SystemExit) as exit_info:
        sessions.launch(db, kind, (kind, "--example"))

    assert seen == [((kind, "--example"), [(existing.session_id, "chosen-name")])]
    assert exit_info.value.code == 3
    assert db.list_agents("test") == []


def test_literal_terminal_send(monkeypatch, tmp_path):
    path = str(tmp_path / "msg.db")
    db = store.MsgStore(path)
    sender = db.register_agent("sender", "%1", "test", models.AgentKind("muse"), "/tmp/socket")
    receiver = db.register_agent("receiver", "%2", "test", models.AgentKind("agy"), "/tmp/socket")
    monkeypatch.setattr(cli, "_ensure_watcher_running", lambda db: None)
    monkeypatch.setattr(cli, "_detect_tmux_session", lambda pane=None: "test")
    monkeypatch.setattr(cli, "_detect_tmux_socket", lambda pane=None: "/tmp/socket")
    monkeypatch.setenv("TMUX_PANE", "%9")
    body = "literal $(not-a-command)\nsecond line"

    result = CliRunner().invoke(cli.cli, ["--db", path, "say", "receiver", body, "--from", "sender"])

    assert result.exit_code == 0, result.output
    assert db.get_inbox(receiver.session_id)[0]["body"] == body
    assert db.get_inbox(receiver.session_id)[0]["from_agent"] == sender.session_id


def test_failed_delivery_stays_unread(monkeypatch, tmp_path):
    instance = watcher.Watcher(str(tmp_path / "msg.db"))
    sender = instance.store.register_agent("a", "%1", "t", models.AgentKind("muse"))
    receiver = instance.store.register_agent("b", "%2", "t", models.AgentKind("custom"))
    thread = instance.store.create_thread("t", sender.session_id, [sender.session_id, receiver.session_id])
    instance.store.send_message(thread.id, sender.session_id, "retain me")
    deliveries = instance.store.claim_pending_deliveries(instance.watcher_id)

    async def idle(*args):
        return True

    async def fail(*args):
        raise RuntimeError("transport failed")

    monkeypatch.setattr(instance, "_check_idle", idle)
    monkeypatch.setattr(instance, "_tmux_send", fail)
    monkeypatch.setattr(watcher, "detect_prompt_state", lambda *args: prompt_detect.PromptState.EMPTY)
    asyncio.run(instance._deliver_to_recipient(receiver.session_id, deliveries))
    assert instance.store.get_inbox(receiver.session_id)[0]["body"] == "retain me"


def test_custom_prompt_adapter(monkeypatch, tmp_path):
    config = tmp_path / "agents.toml"
    config.write_text('[agents.custom]\nempty_prompt = "^READY: *$"\ntext_prompt = "^READY: +.+$"\n')
    monkeypatch.setenv("PING_CONFIG", str(config))
    monkeypatch.setattr(prompt_detect, "_capture_last_lines", lambda *args, **kwargs: ["READY: "])
    assert prompt_detect.detect_prompt_state("%1", "custom") == prompt_detect.PromptState.EMPTY
    monkeypatch.setattr(prompt_detect, "_capture_last_lines", lambda *args, **kwargs: ["READY: draft"])
    assert prompt_detect.detect_prompt_state("%1", "custom") == prompt_detect.PromptState.HAS_TEXT
