from dotenv import load_dotenv
import os
import base64
import hashlib
import urllib.parse

twitter_client_id = os.getenv('TWITTER_CLIENT_ID')

def get_twitter_auth_url():
    random_bytes = os.urandom(32)
    code_verifier = base64.urlsafe_b64encode(random_bytes).decode('ascii').rstrip('=')
    hashed = hashlib.sha256(code_verifier.encode('ascii')).digest()
    code_challenge = base64.urlsafe_b64encode(hashed).decode('ascii').rstrip('=')

    base_url = "https://twitter.com/i/oauth2/authorize"
    scope = "tweet.write"
    params = {
        "response_type": "code",
        "client_id": twitter_client_id,
        "redirect_uri": twitter.get("redirect_uri",""),
        "scope": scope,
        "state": "random_string",  # TODO: make this a real CSRF-safe random string
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }
    
    # Why does ChatGPT suggest returning the code_verifier here??
    # full_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    # return full_url, code_verifier
    return f"{base_url}?{urllib.parse.urlencode(params)}"