from atproto import AsyncClient, models
import httpx

client = AsyncClient()

def taglog(msg):
    print(f"[BLUESKY] {msg}")

async def login(ctx, config):
    if config is None or config.username is None or config.password is None:
        await ctx.reply("Bluesky config is malformed")
        return False

    corrected_username = (
        config.username if config.username.endswith(".bsky.social")
        else f"{config.username}.bsky.social"
    )
    taglog(f"logging into bluesky [{corrected_username}]...")

    try:
        await client.login(corrected_username, config.password)
        taglog("Bluesky login successful.")
        return True
    except Exception as e:
        taglog(f"Bluesky login failed: {e}")
        await ctx.reply("Bluesky login failed.")
        return False

async def test(ctx, msg, config):
    if not await login(ctx, config):
        await ctx.reply("Bluesky login failed, cannot send test message.")
        return

    title = "dadmannwalking published a new video on YouTube"
    description = "StoneVania VOD | Chilled Out Interior Decoration | dadmannwalking on #twitch"
    url = "https://youtu.be/JqBYhpD_8Pg"
    thumbnail = "https://i.ytimg.com/vi/qXWTOAuR4tw/maxresdefault.jpg"

    await create_post(title, description, url, thumbnail, ctx, config, skip_login=True)
    await ctx.reply("test message was sent!")

async def create_post(title, description, url, thumbnail, ctx, config, skip_login=False):
    if not skip_login and not await login(ctx, config):
        await ctx.reply("Bluesky login failed, cannot create post.")
        return

    plaintext = f"{title}\n{description}\n{url}"
    start = plaintext.find(url)
    end = start + len(url)

    if start == -1:
        taglog("URL not found in plaintext.")
        await ctx.reply("Could not create post due to formatting issue.")
        return

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
        if response.status_code != 200:
            taglog(f"Failed to download thumbnail: {response.status_code}")
            await ctx.reply("Thumbnail download failed.")
            return
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