import asyncio
import os
from typing import Literal

from letta_client import AsyncLetta, CreateBlock
from letta_client.types import (
    AgentState,
    Block,
    Identity,
    IdentityType,
    LettaMessageUnion,
    LettaResponse,
)

BLOCK_TYPES = Literal["human", "persona", "interactions"]
CHAT_TYPES = Literal["yenta-chat", "users-chat"]
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


async def create_agent(
    user_ids: list[str],
    chat_type: CHAT_TYPES,
    block_ids: list[str] | None = None,
    memory_blocks: list[CreateBlock] | None = None,
    tools: list[str] | None = None,
) -> AgentState:
    client = get_letta_client()
    kwargs = {}
    if block_ids:
        kwargs["block_ids"] = block_ids
    if memory_blocks:
        kwargs["memory_blocks"] = memory_blocks
    if tools:
        kwargs["tools"] = tools
    agent = await client.agents.create(
        tags=[chat_type] + user_ids,
        model="openai/gpt-4o-mini",
        embedding="openai/text-embedding-3-small",
        **kwargs,
    )
    return agent


async def get_agents(user_id: str, chat_type: CHAT_TYPES) -> list[AgentState]:
    client = get_letta_client()
    agents = await client.agents.list(tags=[chat_type, user_id], match_all_tags=True)
    return agents


async def get_agent_by_id(agent_id: str) -> AgentState:
    client = get_letta_client()
    agent = await client.agents.retrieve(agent_id)
    return agent


async def send_message_to_yenta(
    current_user_id: str, agent_id: str, message: str, mentioned_ids: list[str]
) -> LettaResponse:
    client = get_letta_client()
    shared_agents = await client.agents.list(
        tags=[current_user_id] + mentioned_ids, match_all_tags=True
    )
    summary = []
    block_ids = []
    for agent in shared_agents:
        for block in agent.memory.blocks:
            if block.label == "interactions":
                summary.append(block.value)
                block_ids.append(block.id)

    await asyncio.gather(
        *[client.agents.blocks.attach(agent_id, block_id) for block_id in block_ids]
    )
    interactions_summary = "\n".join(summary)
    response = await client.agents.messages.create(
        agent_id=agent_id,
        messages=[
            {
                "role": "user",
                "content": message,
            }
        ],
    )
    await asyncio.gather(
        *[client.agents.blocks.detach(agent_id, block_id) for block_id in block_ids]
    )
    return response


async def send_message_to_users_chat(
    agent_id: str,
    sender_id: str,
    message: str,
) -> LettaResponse:
    client = get_letta_client()
    response = await client.agents.messages.create(
        agent_id=agent_id,
        messages=[
            {
                "role": "user",
                "content": f"{sender_id}:{message}",
            }
        ],
    )
    return response


async def get_messages(
    agent_id: str, limit: int = 10, message_id: str | None = None
) -> list[LettaMessageUnion]:
    client = get_letta_client()
    messages = await client.agents.messages.list(
        agent_id=agent_id, limit=limit, before=message_id
    )
    return messages


async def create_identity(
    internal_id: str, name: str | None, identity_type: IdentityType = "user"
) -> Identity:
    client = get_letta_client()
    identity = await client.identities.create(
        identifier_key=internal_id, name=name, identity_type=identity_type
    )
    return identity
