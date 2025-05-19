import os
from typing import Literal
from letta_client import AsyncLetta
from letta_client.types.llm_config import LlmConfig
from letta_client.types.agent_state import AgentState
from letta_client.types.block import Block
from letta_client.types.letta_message_union import LettaMessageUnion
from letta_client.types.letta_response import LettaResponse

BLOCK_TYPES = Literal['profile']
LETTA_URL = os.getenv("LETTA_URL", "http://localhost:8283")
OLLAMA_MODEL = "llama3.2:latest"
OLLAMA_EMBEDDING = "ollama/mxbai-embed-large:latest"
ollama_config = LlmConfig(
    model=OLLAMA_MODEL,
    model_endpoint_type='ollama',
    context_window=10000
)


def get_letta_client():
    return AsyncLetta(base_url=LETTA_URL)


async def get_block_by_id(block_id: str) -> Block:
    client = get_letta_client()
    block = await client.blocks.retrieve(block_id)
    return block


async def create_block(label: BLOCK_TYPES, value: str) -> Block:
    client = get_letta_client()
    block = await client.blocks.create(value=value, label=label)
    return block


async def create_agent(identity_ids: list[str], block_ids: list[str] | None = None) -> AgentState:
    client = get_letta_client()
    kwargs = {}
    if block_ids:
        kwargs['block_ids'] = block_ids
    agent = await client.agents.create(identity_ids=identity_ids, llm_config=ollama_config, model="ollama/llama3.2:latest",embedding="ollama/mxbai-embed-large:latest", **kwargs)
    return agent


async def get_agents(identity_id: str) -> list[AgentState]:
    client = get_letta_client()
    agents = await client.agents.list(identity_id=identity_id)
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
