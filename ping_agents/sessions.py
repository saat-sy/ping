"""Register agent launches and send literal messages from terminals."""

import os
import signal
import subprocess
from pathlib import Path

import click

from ping_agents import cli, models


def register_pane(store, kind: str, pid: int | None = None, cwd: str | None = None) -> None:
    """Register this tmux pane, keeping the name of an existing registration."""
    pane = cli._detect_tmux_pane()
    if not pane:
        return
    cli._prune_closed_panes(store)
    current = cli._get_self_agent(store)
    root = Path(cli._get_repo_root(cwd)).name
    name = os.environ.get("MSG_AGENT_NAME", f"{root}-{kind}")
    if current:
        if current.agent_kind.value != kind:
            raise click.ClickException("pane is registered for another agent kind")
        name = current.name
    try:
        store.register_agent(
            name, pane, cli._detect_tmux_session(pane),
            models.AgentKind(kind), cli._detect_tmux_socket(pane),
            display_addr=cli._detect_display_addr(pane),
            pid=pid, cwd=cwd or os.getcwd(),
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


def launch(store, kind: str, command: tuple[str, ...]) -> None:
    """Run the agent registered in this pane, then unregister it on exit."""
    if not command:
        raise click.ClickException("provide the agent executable after --")
    register_pane(store, kind, pid=os.getpid())
    # Ctrl-C belongs to the agent; a handler (unlike SIG_IGN) resets on exec.
    signal.signal(signal.SIGINT, lambda *_: None)
    try:
        code = subprocess.call(command)
    except FileNotFoundError as exc:
        code = 127
        click.echo(f"ping: {exc}", err=True)
    me = cli._get_self_agent(store) if cli._detect_tmux_pane() else None
    if me:
        try:
            store.retire_agent(me.session_id)
        except ValueError:
            pass  # Unread messages keep the registration for the pane's next session.
    raise SystemExit(128 - code if code < 0 else code)


def say(ctx, target: str, body: str, sender: str | None) -> None:
    store = ctx.obj["store"]
    session = cli._detect_tmux_session()
    socket = cli._detect_tmux_socket()
    if sender:
        agent = store.get_agent_by_name(sender, session, socket)
        if not agent:
            raise click.ClickException(f"sender '{sender}' is not registered")
        os.environ["TMUX_PANE"] = agent.pane_id
    elif not cli._get_self_agent(store):
        raise click.ClickException("use --from NAME when sending from a terminal pane")
    ctx.invoke(cli.send, to=target, body=body)
