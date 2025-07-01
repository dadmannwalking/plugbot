# Discord Message to Social Media Bot

This is a Python-based Discord bot that watches specified Discord channels for messages and auto-posts those messages to given social media accounts (e.g., Twitter, Facebook, etc.).

## Security

plugbot is designed with security in mind. To use plugbot's commands, a user in any given server must have a specific role chosen and assigned by the server owner. Otherwise, only the server owner can issue commands. For more information on this command, please refer to the General Commands section of this README.

## General Commands

`!pb_test` is a simple command to ensure that plugbot is functioning at a bare minimum. plugbot will simply reply to this command when used.

`!pb_role <role>` changes the role required to use plugbot's commands. By default, the role used is simply 'admin'. In all cases, the server owner can **always** use plugbot's commands. Please note that this role is case-sensitive and **MUST** be a role within your server.

`!pb_channels list` replies with a list of all currently monitored channel IDs.

`!pb_channels add <channel_id>` subscribes a channel with the given ID to be monitored by plugbot. After subscribed, plugbot will repost any valid repostable messages to all enabled and configured services.

`!pb_channels remove <channel_id>` removes a channel with the given ID from monitoring by plugbot.

`!pb_keywords list` replies with a list of all currently active keywords.

`!pb_keywords add <phrase>` adds the given phrase to the current list of keywords.

`!pb_keywords remove <phrase>` replies with a list of all currently active keywords.

`!pb_gethistory` replies to the original message with JSON representations of any valid repostable messages of the last 10 messages in the channel it was called in.

## Configuration and Integration Commands

Configuration of the bot is handled via Discord commands. As support is added, you will be able to find the commands and information on them below:

### Twitter

Due to the restrictions of using the Twitter API, plugbot is unable to integrate with Twitter, at the current moment. Support is planned to come soon.

### Bluesky

plugbot supports reposting to Bluesky via API using your bot's username and an app password. Before integrating, please create your bot's Bluesky account and generate an app password for it. You will need both of these to continue.

`!pb_enablebluesky <username> <app-password>` is used to enable and configure or update your server's Bluesky integration. Please note that commands that contain sensitive information should be used only in sensitive channels. plugbot will delete the message after it is sent, but cannot guarantee that your username and password won't be captured by another bot or user if used improperly.

`!pb_testbluesky <message>` is used to test your Bluesky integration. It creates a text post containing the message you supply using your configured bot account.

### Facebook

plugbot does not currently support Facebook integration.

### Reddit

plugbot does not currently support Reddit integration.

### Instagram

plugbot does not currently support Instagram integration.

