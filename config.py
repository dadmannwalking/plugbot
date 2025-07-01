from pathlib import Path
from typing import List, Optional
from discord import Message
import json
import base64

def taglog(msg: str):
    print(f"[CONFIG] {msg}", flush=True)

class ServiceConfig:
    def __init__(
        self, 
        enabled: bool,
        username: Optional[str] = None,
        password: Optional[str] = None):
        self.enabled = enabled
        self.username = username

        if password and password.strip():
            try:
                decoded_bytes = base64.b64decode(password.encode("utf-8"))
                self.password = decoded_bytes.decode("utf-8")
            except Exception as e:
                # Assume already plain text if decoding fails
                taglog(f"Password decode failed, using raw password: {e}")
                self.password = password
        else:
            self.password = None

    def json(self) -> dict:
        obj = {}
        obj["enabled"] = self.enabled

        if self.username:
            obj["username"] = self.username

        if self.password:
            # Ensure encoded password when we make json dict so it's always stored as
            # encoded string
            encoded = base64.b64encode(self.password.encode("utf-8")).decode("utf-8")
            obj["password"] = encoded

        return obj

    def enable(self, username, password):
        self.enabled = True
        self.password = password
        self.username = (
            username if username.endswith(".bsky.social")
            else f"{username}.bsky.social"
        )

class Config:
    def __init__(
        self,
        configuration_role: str = "admin",
        watched_channels: Optional[List[int]] = None,
        permitted_users: Optional[List[str]] = None,
        keywords: Optional[List[str]] = None,
        twitter: Optional[ServiceConfig] = None,
        bluesky: Optional[ServiceConfig] = None,
        facebook: Optional[ServiceConfig] = None,
        reddit: Optional[ServiceConfig] = None,
        instagram: Optional[ServiceConfig] = None):
        self.configuration_role = configuration_role
        self.watched_channels = watched_channels if watched_channels is not None else []
        self.permitted_users = permitted_users if permitted_users is not None else []
        self.keywords = keywords if keywords is not None else []
        self.twitter = twitter
        self.bluesky = bluesky
        self.facebook = facebook
        self.reddit = reddit
        self.instagram = instagram

    def json(self) -> dict:
        obj = {
            "configuration_role": self.configuration_role,
            "watched_channels": self.watched_channels,
            "permitted_users": self.permitted_users,
            "keywords": self.keywords
        }
        
        obj["twitter"] = self.twitter.json() if self.twitter else None
        obj["bluesky"] = self.bluesky.json() if self.bluesky else None
        obj["facebook"] = self.facebook.json() if self.facebook else None
        obj["reddit"] = self.reddit.json() if self.reddit else None
        obj["instagram"] = self.instagram.json() if self.instagram else None
        return obj

    # For some reason, commands.has_role() does not like the role being configured via json,
    # so this function will determine if a given user has authorization to use a protected
    # function
    def authorized(self, user, guild) -> bool:
        if guild.owner and user == guild.owner:
            return True

        for role in user.roles:
            if role.name == self.configuration_role:
                return True

        print(f"{user.name} is not authorized!")
        return False

    def confirm(self, message: Message) -> bool:
        if message.author.name == "plugbot":
            taglog("ignore messages from plugbot")
            return False

        if self.permitted_users != [] and message.author.name not in self.permitted_users:
            taglog(f"ignore messages from non-permitted user {message.author.name}")
            return False

        if message.channel.id not in self.watched_channels:
            taglog(f"ignore messages from unmonitored channel {message.channel.name}")
            return False

        return True

script_dir = Path(__file__).parent
file_path = script_dir / "config.json"

def get_config(guild_id: int) -> Config:
    with open(file_path, "r") as file:
        data = json.load(file)
        config_json = data.get(str(guild_id), {})
        twitter_config = config_json.get("twitter") or {}
        bluesky_config = config_json.get("bluesky") or {}
        facebook_config = config_json.get("facebook") or {}
        reddit_config = config_json.get("reddit") or {}
        instagram_config = config_json.get("instagram") or {}

        return Config(
            configuration_role=config_json.get("configuration_role", "admin"),
            watched_channels=config_json.get("watched_channels", []),
            permitted_users=config_json.get("permitted_users", []),
            keywords=config_json.get("keywords", []),
            twitter=ServiceConfig(
                enabled=twitter_config.get("enabled", False)
            ),
            bluesky=ServiceConfig(
                enabled=bluesky_config.get("enabled", False),
                username=bluesky_config.get("username", None),
                password=bluesky_config.get("password", None)
            ),
            facebook=ServiceConfig(
                enabled=facebook_config.get("enabled", False)
            ),
            reddit=ServiceConfig(
                enabled=reddit_config.get("enabled", False)
            ),
            instagram=ServiceConfig(
                enabled=instagram_config.get("enabled", False)
            )
        )

def set_config(config: Config, guild_id: int):
    # Get full config dictionary
    with open(file_path, "r") as file:
        data = json.load(file)
        data[str(guild_id)] = config.json()

        with open(file_path, "w") as file:
            json.dump(data, file, indent=4)
