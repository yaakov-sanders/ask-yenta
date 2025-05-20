import os
from typing import Literal
from letta_client import AsyncLetta
from letta_client.types.agent_state import AgentState
from letta_client.types.block import Block
from letta_client.types.letta_message_union import LettaMessageUnion
from letta_client.types.letta_response import LettaResponse

BLOCK_TYPES = Literal['human', 'persona']
LETTA_URL = os.getenv("LETTA_URL", "http://localhost:8283")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def get_letta_client():
    return AsyncLetta(base_url=LETTA_URL)


async def get_block_by_id(block_id: str) -> Block:
    client = get_letta_client()
    block = await client.blocks.retrieve(block_id)
    return block


async def create_block(label: BLOCK_TYPES, value: str) -> Block:
    client = get_letta_client()
    block = await client.blocks.create(value=value, label=label, is_template=True)
    return block


async def create_agent(identity_ids: list[str], block_ids: list[str] | None = None) -> AgentState:
    client = get_letta_client()
    kwargs = {}
    if block_ids:
        kwargs['block_ids'] = block_ids
    agent = await client.agents.create(
        tags=identity_ids, 
        model="openai/gpt-4o-mini",
        embedding="openai/text-embedding-3-small",
        **kwargs
    )
    return agent


async def get_agents(identity_id: str) -> list[AgentState]:
    client = get_letta_client()
    agents = await client.agents.list(tags=identity_id)
    return agents


async def get_agent_by_id(agent_id: str) -> AgentState:
    client = get_letta_client()
    agent = await client.agents.retrieve(agent_id)
    return agent


async def send_message(agent_id: str, message: str) -> LettaResponse:
    client = get_letta_client()
    response = await client.agents.messages.create(agent_id=agent_id, messages=[
        {
            "role": "user",
            "content": message
        }
    ])
    return response


async def get_messages(agent_id: str, limit: int = 10, message_id: str | None = None) -> list[LettaMessageUnion]:
    client = get_letta_client()
    messages = await client.agents.messages.list(agent_id=agent_id, limit=limit, before=message_id)
    return messages
