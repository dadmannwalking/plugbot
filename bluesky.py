from dotenv import load_dotenv
import os
from atproto import AsyncClient, models
import asyncio
import httpx

username = None
password = None

client = AsyncClient()

def taglog(msg):
    print(f"[BLUESKY] {msg}")

async def login(ctx):
    corrected_username = f"{username}.bsky.social"
    try:
        taglog(f"logging into bluesky [{corrected_username}]...")
        await asyncio.wait_for(client.login(corrected_username, password), 5)
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
        taglog(f"created facet [{facet}]")

        # Download the thumbmnail from the url and upload to atproto blob
        async with httpx.AsyncClient() as client_http:
            response = await client_http.get(thumbnail)
            taglog(f"received image with response [{response}]")
            
        blob = await client.com.atproto.repo.upload_blob(response.content)
        taglog(f"got blob [{blob.blob}]")
        
        # Create embed to include in message
        taglog(f"creating embed with {url}, {title}, and {description}")
        external_embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                uri=url,
                title=title,
                description=description or "",
                thumb=blob.blob
            )
        )
        taglog(f"created external embed [{external_embed}]")
        
        await client.send_post(text=plaintext, facets=[facet], embed=external_embed)