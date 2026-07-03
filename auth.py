import requests
import json
import time
import os

CLIENT_ID = os.environ.get("CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "")
TOKEN_FILE = os.environ.get("TOKEN_FILE", "meli_token.json")
AUTH_URL = "https://api.mercadolibre.com/oauth/token"


def renovar_token():
    with open(TOKEN_FILE, "r") as f:
        token_data = json.load(f)
    resp = requests.post(AUTH_URL, data={
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": token_data["refresh_token"],
    })
    resp.raise_for_status()
    data = resp.json()
    token = {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_in": data["expires_in"],
        "created_at": int(time.time()),
    }
    # escreve num lugar gravável (a nuvem não deixa gravar em qualquer pasta)
    write_path = "/tmp/meli_token.json" if os.path.exists("/tmp") else TOKEN_FILE
    with open(write_path, "w") as f:
        json.dump(token, f, indent=2)
    return data["access_token"]


def get_token():
    caminho = "/tmp/meli_token.json" if os.path.exists("/tmp/meli_token.json") else TOKEN_FILE
    with open(caminho, "r") as f:
        token_data = json.load(f)
    expiracao = token_data["created_at"] + token_data["expires_in"] - 60
    if time.time() > expiracao:
        print("Token expirado, renovando...")
        return renovar_token()
    return token_data["access_token"]