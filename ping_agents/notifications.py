"""Format complete peer messages for watcher and hook delivery."""

def format_deliveries(deliveries: list[dict]) -> str:
    return "[ping: peer messages]\n" + "\n".join(
        f'{item.get("sender_agent_kind", item["from_name"])}: {item["body"]}'
        for item in deliveries
    )
