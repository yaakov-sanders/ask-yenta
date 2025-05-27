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

BLOCK_TYPES = Literal["human", "persona"]
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
    identity_ids: list[str],
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
        tags=[chat_type],
        identity_ids=identity_ids,
        model="openai/gpt-4o-mini",
        embedding="openai/text-embedding-3-small",
        **kwargs,
    )
    return agent


async def get_agents(identity_id: str, chat_type: CHAT_TYPES) -> list[AgentState]:
    client = get_letta_client()
    agents = await client.agents.list(identity_id=identity_id, tags=[chat_type])
    return agents


async def get_agent_by_id(agent_id: str) -> AgentState:
    client = get_letta_client()
    agent = await client.agents.retrieve(agent_id)
    return agent


async def send_message_to_yenta(
    agent_id: str, sender_id: str, message: str
) -> LettaResponse:
    client = get_letta_client()
    response = await client.agents.messages.create(
        agent_id=agent_id,
        messages=[{"role": "user", "content": message, "sender_id": sender_id}],
    )
    return response


async def send_message_to_users_chat(
    agent_id: str,
    sender_id: str,
    message: str,
    recipients: list[str],
) -> LettaResponse:
    client = get_letta_client()
    response = await client.agents.messages.create(
        agent_id=agent_id,
        messages=[
            {
                "role": "user",
                "content": f"{sender_id}:{message}",
                "sender_id": sender_id,
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
