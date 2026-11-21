"""Small, deterministic command parser for the first AURA mission."""

import re


def parse_mission(command: str) -> str | None:
    """Recognize requests to find or tag the red object."""
    normalized = command.lower().strip()
    normalized = re.sub(r"^aura[\s,.:;!?]*", "", normalized)
    words = set(re.findall(r"[a-z]+", normalized))
    if "tag" in words and "red" in words and ({"object", "target"} & words):
        return "tag_red"
    if "find" in words and "red" in words and ({"object", "target"} & words):
        return "find_red"
    return None
