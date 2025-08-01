# Discord Message to Social Media Bot

This is a Python-based Discord bot that watches specified Discord channels for messages and auto-posts those messages to enabled and configured social media accounts.

## How plugbot Works

Plugbot monitors channels in your Discord server added by users with appropriate access (server mods) for any incoming messages from users specified by mods where the message contains key words and phrases specified by server mods. If plugbot finds a message that meets all of its criteria, plugbot will repost the message to all social media services enabled and configured by the server mods.

## Security

plugbot is designed with security in mind. To use plugbot's commands, a user in any given server must have a specific role chosen and assigned by the server owner. Otherwise, only the server owner can issue commands. For more information on this command, please refer to the General Commands section of this README.

## General Commands

`!pb_test` is a simple command to ensure that plugbot is functioning at a bare minimum. plugbot will simply reply to this command when used.

`!pb_role <role>` changes the role required to use plugbot's commands. By default, the role used is simply 'admin'. In all cases, the server owner can **always** use plugbot's commands. **Please note** that this role is case-sensitive and **MUST** be a role within your server.

`!pb_channels list` replies with a list of all currently monitored channels.

`!pb_channels add <channel>` subscribes a channel with the given ID or name to be monitored by plugbot. After subscribed, plugbot will repost any valid repostable messages to all enabled and configured services. **Please note** that when using a name with this command, it is not case-sensitive. Additionally, any identifiers or emojis included in the channel name will be stripped while searching for the channel.

`!pb_channels remove <channel>` removes a channel with the given ID or name from monitoring by plugbot. **Please note** that when using a name with this command, it is not case-sensitive. Additionally, any identifiers or emojis included in the channel name will be stripped while searching for the channel.

`!pb_filters list` replies with a list of all currently active key phrases.

`!pb_filters add <phrase>` adds the given phrase to the current list of key phrases. **Please note** that all added phrases are case-insensitive. Additionally, if keywords are provided, at least one match is required to be a valid repostable message, but if no keywords are provided, no messages will be filtered and all messages matching all other criteria will be reposted.

`!pb_filters remove <phrase>` removes thej given phrase from the current list of key phrases. **Please note** that all added phrases are case-insensitive.

`!pb_users list` replies with a list of all currently monitored users.

`!pb_users add <username/user id>` adds a user with the given username or user id to the list of currently monitored users, if not already present. **Please note** that username matching is case-insensitive and can use either username or display name, but the user must be a member of your guild.

`!pb_users remove <username/user id>` removes a user with the given username or user id from the list of currently monitored users, if present. **Please note** that username matching is case-insensitive and can use either username or display name, but the user must be a member of your guild.

`!pb_gethistory <limit>` iterates through the last num of messages and replies to the original message with data of any valid repostable messages in the channel it was called in (*this command ignores the monitored channel list*). Depending on the input, this command can take some time to complete, so when finished, plugbot will reply appropriately to let you know it's done. If no valid repostable messages according to the current parameters are found, plugbot replies as such.

## Configuration and Integration Commands

Configuration of the bot is handled via Discord commands. As support is added, you will be able to find the commands and information on them below:

### Twitter

Due to the restrictions of using the Twitter API, plugbot is unable to integrate with Twitter, at the current moment. Support is planned to come soon.

### Bluesky

plugbot supports reposting to Bluesky via API using your bot's username and an app password. Before integrating, please create your bot's Bluesky account and generate an app password for it. You will need both of these to continue.

`!pb_enablebluesky <username> <app-password>` is used to enable and configure or update your server's Bluesky integration. **Please note** that commands that contain sensitive information should be used only in sensitive channels. plugbot will delete the message after it is sent, but cannot guarantee that your username and password won't be captured by another bot or user if used improperly.

`!pb_testbluesky <message>` is used to test your Bluesky integration. It creates a text post containing the message you supply using your configured bot account.

### Facebook

plugbot does not currently support Facebook integration.

### Reddit

plugbot does not currently support Reddit integration.

### Instagram

plugbot does not currently support Instagram integration.

