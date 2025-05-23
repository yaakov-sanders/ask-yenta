def summarize_interaction(speaker: str, message: str, insight: str) -> bool:
    """Summarize what a participant’s message reveals about the group interaction."""
    memory.append(label="interactions", content=f"{speaker} revealed: {insight}")
    return True
