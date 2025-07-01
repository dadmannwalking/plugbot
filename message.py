from discord import Message
import json
import re

def json_from(message: Message):
    attachments = []
    embeds = []
    mentions = []
    role_mentions = []
    channel_mentions = []

    for attachment in message.attachments:
        attachment_payload = []
        attachment_payload["id"] = attachment.id
        attachment_payload["filename"] = attachment.filename
        attachment_payload["content_type"] = attachment.content_type
        attachment_payload["size"] = attachment.size
        attachment_payload["url"] = attachment.url
        attachment_payload["proxy_url"] = attachment.proxy_url
        attachment_payload["height"] = attachment.height
        attachment_payload["width"] = attachment.width
        attachment_payload["description"] = attachment.description
        attachments.append(attachment_payload)

    for embed in message.embeds:
        if embed:
            embed_payload = {}
            embed_payload["url"] = embed.url
            embed_payload["description"] = embed.description
            embed_payload["title"] = embed.title
            embed_payload["author"] = embed.author.name
            embed_payload["image_url"] = embed.image.url
            embed_payload["thumbnail_url"] = embed.thumbnail.url
            embed_payload["footer_text"] = embed.footer.text
            embed_payload["footer_icon_url"] = embed.footer.icon_url
            embed_payload["video_url"] = embed.video.url
            embeds.append(embed_payload)

    for mention in message.mentions:
        mention_payload = {}
        mention_payload["id"] = mention.id
        mention_payload["name"] = mention.name
        mention_payload["discriminator"] = mention.discriminator
        mention_payload["display_name"] = mention.display_name
        mention_payload["global_name"] = mention.global_name
        mention_payload["bot"] = mention.bot
        mention_payload["mention"] = mention.mention
        mentions.append(mention_payload)

    for mention in message.role_mentions:
        mention_payload = {}
        mention_payload["id"] = mention.id
        mention_payload["name"] = mention.name
        mention_payload["mention"] = mention.mention
        mention_payload["position"] = mention.position
        mention_payload["mentionable"] = mention.mentionable
        mention_payload["hoist"] = mention.hoist
        mention_payload["managed"] = mention.managed
        role_mentions.append(mention_payload)

    for mention in message.channel_mentions:
        mention_payload = {}
        mention_payload["id"] = mention.id
        mention_payload["name"] = mention.name
        mention_payload["mention"] = mention.mention
        mention_payload["created_at"] = str(mention.created_at)
        mention_payload["guild"] = mention.guild.id
        mention_payload["category"] = mention.category.id
        channel_mentions.append(mention_payload)
    
    payload = {}
    payload["content"] = message.content
    payload["author"] = message.author.name
    payload["channel_id"] = message.channel.id
    payload["guild_id"] = message.guild.id
    payload["id"] = message.id
    payload["type"] = message.type.name
    payload["attachments"] = attachments
    payload["embeds"] = embeds
    payload["mentions"] = mentions
    payload["role_mentions"] = role_mentions
    payload["channel_mentions"] = channel_mentions

    return json.dumps(payload)

def title_from(data: dict) -> str:
    post_title = "Untitled Post"
    embeds = data.get("embeds", [])
    content = data.get("content", "")

    # --- Twitch Stream Detected ---
    if embeds and "twitch.tv" in (embeds[0].get("url") or ""):
        # Extract user from 'author' field if possible
        embed_author = embeds[0].get("author", "")
        user = embed_author.replace(" is live on Twitch", "").strip() if "is live on Twitch" in embed_author else embed_author
        
        # Fallback to parsing from content if needed
        if not user and "**" in content:
            user = content.split("**")[1]

        if user:
            post_title = f"{user} is live!"

    # --- YouTube Video Detected ---
    elif embeds and "youtu" in (embeds[0].get("url") or ""):
        embed_author = embeds[0].get("author", "")
        if "published a new video" in embed_author:
            user = embed_author.split(" published a new video")[0].strip()
            post_title = f"{user} uploaded a video!"
    
    # --- Fallback for plain content detection ---
    elif "just posted a new video" in content:
        # Example: "**ThatOneGuyJames** just posted a new video!"
        user = content.split("**")[1] if "**" in content else "Unknown"
        post_title = f"{user} uploaded a video!"

    return post_title

def description_from(data: dict) -> str:
    embeds = data.get("embeds", [])
    
    if embeds and embeds[0].get("title"):
        return embeds[0]["title"]

    return ""

def url_from(data: dict) -> str:
    url_pattern = re.compile(r"https?://[^\s)>\]]+")
    
    embeds = data.get("embeds", [])
    content = data.get("content", "")
    url = ""

    # Check embeds first
    if embeds and embeds[0].get("url"):
        url = embeds[0]["url"]

    # If no URL from embeds, search content
    if not url:
        match = url_pattern.search(content)
        if match:
            url = match.group(0)

    return url

def thumbnail_url_from(data: dict) -> str:
    embeds = data.get("embeds", [])
    content = data.get("content", "")
    img_url = ""

    if embeds:
        embed = embeds[0]
        url = embed.get("url", "") or ""
        
        # Step 1: image_url
        if embed.get("image_url"):
            img_url = embed["image_url"]

        # Step 2: thumbnail_url
        elif embed.get("thumbnail_url"):
            img_url = embed["thumbnail_url"]

        # Step 3: Construct YouTube thumbnail from URL
        elif embed.get("url") and "youtu" in embed["url"]:
            match = youtube_pattern.search(embed["url"])
            if match:
                video_id = match.group(1)
                img_url = f"https://i.ytimg.com/vi/{video_id}/maxresdefault.jpg"
        
        # Step 4: Construct Twitch thumbnail from URL
        elif "twitch.tv" in url:
            # Extract username from URL
            match = re.search(r"twitch\.tv/([\w\d_]+)", url)
            if match:
                username = match.group(1).lower()
                img_url = f"https://static-cdn.jtvnw.net/previews-ttv/live_user_{username}-880x496.jpg"

    return img_url

def handle(message: Message):
    data = json.loads(json_from(message=message))
    title = title_from(data=data)
    description = description_from(data=data)
    url = url_from(data=data)
    thumbnail = thumbnail_url_from(data=data)

    return title, description, url, thumbnail
