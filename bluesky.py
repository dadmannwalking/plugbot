from dotenv import load_dotenv
import os
from atproto import AsyncClient, models
import asyncio
import httpx

bluesky_username = os.getenv('BLUESKY_USERNAME')
bluesky_password = os.getenv('BLUESKY_PASSWORD')

client = AsyncClient()

async def login(ctx):
    username = f"{bluesky_username}.bsky.social"
    try:
        await asyncio.wait_for(client.login(username, bluesky_password), 5)
        return True
    except asyncio.TimeoutError:
        await client.session.close()
        await ctx.reply("Sorry, timed out authorizing Bluesky!")
        return False

async def test(ctx, msg):
    if await login(ctx):
        title = "dadmannwalking published a new video on YouTube"
        description = "StoneVania VOD | Chilled Out Interior Decoration | dadmannwalking on #twitch"
        url = "https://youtu.be/JqBYhpD_8Pg"
        thumbnail = "https://i.ytimg.com/vi/qXWTOAuR4tw/maxresdefault.jpg"

        await create_post(title, description, url, thumbnail, ctx)
        # await client.send_post(text=f"bluesky test [{msg}]")
        await ctx.reply("test message was sent!")

async def create_post(title, description, url, thumbnail, ctx):
    if await login(ctx):
        plaintext = f"{title}\n{description}\n{url}"
        start = plaintext.find(url)
        end = start + len(url)

        # Create facet to embed url properly
        facet = models.AppBskyRichtextFacet.Main(
            index=models.AppBskyRichtextFacet.ByteSlice(
                byte_start=start, byte_end=end
            ),
            features=[models.AppBskyRichtextFacet.Link(uri=url)]
        )

        # Download the thumbmnail from the url and upload to atproto blob
        response = httpx.get(thumbnail)
        blob = await client.com.atproto.repo.upload_blob(response.content)

        # Create embed to include in message
        external_embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                uri=url,
                title=title,
                description=description,
                thumb=blob.blob
            )
        )

        await client.send_post(text=plaintext, facets=[facet], embed=external_embed)
        # await client.send_post(text=message)