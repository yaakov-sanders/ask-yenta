def summarize_interaction(
    agent_state: "AgentState", speaker: str, message: str, insight: str
) -> bool:
    """Summarize what a participant's message reveals about the group interaction.
    
    Args:
        agent_state (AgentState): The current state of the agent containing memory blocks
        speaker (str): The name/identifier of the participant who sent the message
        message (str): The actual message content from the participant
        insight (str): The insight or revelation to be recorded about the interaction
        
    Returns:
        bool: True if the interaction was successfully summarized
    """
    current_value = str(agent_state.memory.get_block("interactions").value)
    new_value = current_value + "\n" + f"{speaker} revealed: {insight}"
    agent_state.memory.update_block_value(label="interactions", value=new_value)
    return True
