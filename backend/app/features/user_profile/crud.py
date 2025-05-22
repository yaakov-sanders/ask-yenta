from app.core.db import save_to_db
from app.features.letta_logic.letta_logic import create_block
from app.features.users.models import User


async def get_or_create_user_block_ids(user: User) -> tuple[str, str]:
    if user.profile_block_id:
        profile_block_id = user.profile_block_id
    else:
        profile_block = await create_block("human", f"Profile: {user.full_name}")
        profile_block_id = profile_block.id
        user.profile_block_id = profile_block_id

        await save_to_db(user)
    if user.yenta_block_id:
        yenta_block_id = user.yenta_block_id
    else:
        yenta_block = await create_block(
            "persona",
            "You are Yenta — a warm, witty, and perceptive AI who remembers everything about the user and helps them understand themselves and others better. You speak like a nosy best friend with good intentions and great instincts. Be smart, honest, and a little cheeky.",
        )
        yenta_block_id = yenta_block.id
        user.yenta_block_id = yenta_block_id
        await save_to_db(user)

    return profile_block_id, yenta_block_id
