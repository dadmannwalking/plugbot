Discord doesn’t expose a user’s time zone directly through its API. Here are the realistic options you have when building a bot:

---

### 1. **Discord API Limitations**

* The official Discord API does **not** include a `timezone` field for users.
* All you can normally get about a user is their username, discriminator (or global name), avatar, ID, and things like roles/nitro status if in a guild.
* Even the `/profile` endpoints don’t expose timezone information.

---

### 2. **Workarounds**

Since you can’t pull it automatically, the only ways are indirect:

* **Ask Users to Set It**
  You could build a `/settimezone` command in your bot. Users run something like:

  ```
  /settimezone timezone: America/New_York
  ```

  Then you save that info in your database. From there, you can calculate their local time whenever needed.

* **Infer from Activity / Locale (Not Reliable)**

  * Discord’s client locale (e.g. `en-US`, `en-GB`) is available only for the user running slash commands (via interactions). This gives you their **language/region**, but not always their actual time zone.
  * Activity timestamps (like when they send a message) can’t reliably reveal time zone, since you don’t know when their “local midnight” is.

* **Integrate With External Accounts**
  If your bot integrates with something like Google Calendar, Outlook, or another service where users already have a time zone set, you could use that (with their permission).

---

### 3. **Best Practice**

The most common pattern is:

1. Provide a `/settimezone` or `/profile` command.
2. Store the time zone in your bot’s database (e.g. `pytz` or `zoneinfo` identifiers like `America/Chicago`).
3. Use that whenever you need to show local times, schedule events, etc.

This way, your bot isn’t guessing — it’s user-declared and consistent.

---

👉 Do you want me to sketch out a simple example of a `/settimezone` + `/mytime` slash command in Python (discord.py or nextcord) so your bot can handle this?
