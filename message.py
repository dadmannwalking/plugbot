from discord import Message
import json

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