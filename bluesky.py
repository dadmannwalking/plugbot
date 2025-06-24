from dotenv import load_dotenv
import os
from atproto import Client, AsyncClient

bluesky_username = os.getenv('BLUESKY_USERNAME')
bluesky_password = os.getenv('BLUESKY_PASSWORD')

async def test(ctx, msg):
    client = AsyncClient()
    print(3)
    username = f"{bluesky_username}.bsky.social"
    await client.login(username, bluesky_password)
    print(4)
    await client.send_post(text=f"bluesky test [{msg}]")
    print(5)