from pathlib import Path
from typing import List, Optional
import json

class ServiceConfig:
    def __init__(
        self, 
        enabled: bool,
        username: Optional[str] = None,
        password: Optional[str] = None):
        self.enabled = enabled
        self.username = username
        self.password = password

    def json(self) -> dict:
        obj = {}
        obj["enabled"] = self.enabled

        if username:
            obj["username"] = self.username

        if password:
            obj["password"] = self.password

        return obj

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
        obj = {}
        obj["configuration_role"] = self.configuration_role
        obj["watched_channels"] = self.watched_channels
        obj["permitted_users"] = self.permitted_users
        obj["keywords"] = self.keywords
        obj["twitter"] = self.twitter.json() if self.twitter else None
        obj["bluesky"] = self.bluesky.json() if self.bluesky else None
        obj["facebook"] = self.facebook.json() if self.facebook else None
        obj["reddit"] = self.reddit.json() if self.reddit else None
        obj["instagram"] = self.instagram.json() if self.instagram else None
        return obj

script_dir = Path(__file__).parent
file_path = script_dir / "config.json"

def get_config(guild_id: int) -> Config:
    with open(file_path, "r") as file:
        data = json.load(file)
        config_json = data.get(str(guild_id), {})
        twitter_config = config_json.get("twitter", {})
        bluesky_config = config_json.get("bluesky", {})
        facebook_config = config_json.get("facebook", {})
        reddit_config = config_json.get("reddit", {})
        instagram_config = config_json.get("instagram", {})

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
