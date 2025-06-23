# Discord Message to Social Media Bot

This is a Python-based Discord bot that watches specified Discord channels for messages and auto-posts those messages to given social media accounts (e.g., Twitter, Facebook, etc.).

## Configuration

Configuration of the bot is handled via Discord commands as well as the `config.json` file. The many fields that can be configured within `config.json` include the following:

- prefix (default: `!pb`) -> the prefix used for issuing commands to the bot
- configuration_role (default: `admin`) -> the role a user must have to use a "protected" prefix command
- watched_channels -> a list of int values, each matching the id of a given channel to monitor for updates

In addition to the above fields, each social media service that plugbot can push updates to exists as an object in the `config.json` file, denoted by the service's name. Each of these objects have differing fields depending on what information is required and are detailed below.

### Twitter
Twitter requires the following properties to be configured:
- enabled -> a boolean value indicating if this service is enabled

```json
{
    "enabled": false
}
```

### Bluesky
Bluesky requires the following properties to be configured:
- enabled -> a boolean value indicating if this service is enabled

```json
{
    "enabled": false
}
```

### Facebook
Facebook requires the following properties to be configured:
- enabled -> a boolean value indicating if this service is enabled

```json
{
    "enabled": false
}
```

### Reddit
Reddit requires the following properties to be configured:
- enabled -> a boolean value indicating if this service is enabled

```json
{
    "enabled": false
}
```

### Instagram
Instagram requires the following properties to be configured:
- enabled -> a boolean value indicating if this service is enabled

```json
{
    "enabled": false
}
```

