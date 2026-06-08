from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from werkzeug.security import check_password_hash, generate_password_hash

# --- Web UI : HTTP Basic Auth ---

basic_auth = HTTPBasicAuth()

_USERS = {
    "admin": {"password": generate_password_hash("admin"), "role": "admin"},
    "user": {"password": generate_password_hash("user"), "role": "user"},
}


@basic_auth.verify_password
def verify_password(username: str, password: str):
    if username in _USERS and check_password_hash(_USERS[username]["password"], password):
        return username
    return None


@basic_auth.get_user_roles
def get_user_roles(username: str):
    return [_USERS[username]["role"]]


# --- API : HTTP Token Auth (Bearer) ---

token_auth = HTTPTokenAuth(scheme="Bearer")

_TOKENS = {
    "admin-secret-token": "admin",
    "user-secret-token": "user",
}


@token_auth.verify_token
def verify_token(token: str):
    return _TOKENS.get(token)


@token_auth.get_user_roles
def get_token_user_roles(username: str):
    return [_USERS[username]["role"]] if username in _USERS else []
