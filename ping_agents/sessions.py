"""Register agent launches and send literal messages from terminals."""

import os
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
    root = Path(store.db_path).parent.parent.name
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
    if not command:
        raise click.ClickException("provide the agent executable after --")
    register_pane(store, kind, pid=os.getpid())
    os.execvpe(command[0], command, os.environ.copy())


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
