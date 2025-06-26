In `discord.py`, a `discord.Message` can include embeds — and each embed is a `discord.Embed` object. However, if you're **reading** embeds from a message (i.e., `message.embeds[0]`), you're actually working with a `discord.embeds.Embed` object populated from Discord data — a bit different from what you use when *creating* an embed.

---

## ✅ Common Properties on `discord.Embed` (incoming from a message)

Here are the main attributes you can access:

| Attribute            | Type                     | Description                   |
| -------------------- | ------------------------ | ----------------------------- |
| `.title`             | `str` or `None`          | The title text of the embed   |
| `.description`       | `str` or `None`          | The main body content         |
| `.url`               | `str` or `None`          | URL attached to the title     |
| `.color` / `.colour` | `discord.Color` or `int` | The embed strip color         |
| `.timestamp`         | `datetime` or `None`     | Timestamp shown in the footer |

---

## 👤 Author Information

| Property           | Description                |
| ------------------ | -------------------------- |
| `.author.name`     | Name in the author section |
| `.author.url`      | Optional URL               |
| `.author.icon_url` | Icon next to name          |

---

## 🖼️ Media

| Property           | Description                           |
| ------------------ | ------------------------------------- |
| `.image.url`       | Large image shown below fields        |
| `.thumbnail.url`   | Smaller image in the top-right corner |
| `.footer.text`     | Footer text                           |
| `.footer.icon_url` | Footer icon                           |
| `.video.url`       | Video URL (if attached — read-only)   |

---

## 📦 Fields

* `.fields` → A list of field objects (`discord.embeds.EmbedField`)
* Each field has:

  * `.name`
  * `.value`
  * `.inline`

---

## 🧪 Example: Read Embed Info from a Message

```python
@bot.event
async def on_message(message):
    if message.embeds:
        embed = message.embeds[0]
        print("Title:", embed.title)
        print("Description:", embed.description)
        print("URL:", embed.url)
        print("Image URL:", embed.image.url if embed.image else "No image")
        print("Footer:", embed.footer.text if embed.footer else "No footer")

    await bot.process_commands(message)
```

---

Let me know if you want to:

* Clone/copy embeds
* Modify an existing embed
* Convert embeds to JSON

I can help with all of those.
