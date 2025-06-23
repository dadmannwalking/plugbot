import base64
import hashlib
import os

def get_auth_url(client_id, redirect_uri):
    code_verifier = base64.urlsafe_b64encode(os.urandom(40).decode("utf-8").rstrip("="))
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).decode("utf-8").rstrip("=")
    return f"https://twitter.com/i/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope=tweet.write&state=random_string&code_challenge={code_challenge}&code_challenge_method=S256"