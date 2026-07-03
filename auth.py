import requests
import json
import time
import os

TOKEN_FILE = "/tmp/meli_token.json"  # local gravável na nuvem
AUTH_URL = "https://api.mercadolibre.com/oauth/token"

CLIENT_ID = os.environ.get("CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("REFRESH_TOKEN", "")


def garantir_token_file():
    """Se o token ainda não existe (ex: servidor acabou de reiniciar),
    recria a partir do REFRESH_TOKEN guardado nas variáveis."""
    if os.path.exists(TOKEN_FILE):
        return
    token = {
        "access_token": "",
        "refresh_token": REFRESH_TOKEN,
        "expires_in": 21600,
        "created_at": 0,  # 0 = força renovar na primeira vez
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f, indent=2)


def salvar_token(data):
    token = {
        "access_token": data["access_token"],
        "refresh_token": data["refresh_token"],
        "expires_in": data["expires_in"],
        "created_at": int(time.time()),
    }
    with open(TOKEN_FILE, "w") as f:
        json.dump(token, f, indent=2)


def renovar_token():
    garantir_token_file()
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
    salvar_token(data)
    return data["access_token"]


def get_token():
    garantir_token_file()
    with open(TOKEN_FILE, "r") as f:
        token_data = json.load(f)

    expiracao = token_data["created_at"] + token_data["expires_in"] - 60
    if time.time() > expiracao:
        print("Token expirado, renovando...")
        return renovar_token()

    return token_data["access_token"]
