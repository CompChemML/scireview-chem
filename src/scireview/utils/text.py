def lines_to_list(value: str) -> list[str]:
    """Return non-empty, trimmed lines while preserving their order and wording."""
    return [line.strip() for line in value.splitlines() if line.strip()]

