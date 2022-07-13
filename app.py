from os import environ
from typing import List

import jose.jwt as jwt
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_discord import DiscordOAuthClient, User
from httpx import AsyncClient
from uvicorn import run

app = FastAPI()

load_dotenv()

discord = DiscordOAuthClient(
    environ.get("DISCORD_CLIENT_ID"),
    environ.get("DISCORD_CLIENT_SECRET"),
    environ.get("BASE_URL") + "/callback",
    ("identify", "guilds", "email"),
)
ALLOWED_GUILD_ID = environ.get("DISCORD_GUILD_ID")
NOLT_SECRET = environ.get('NOLT_SECRET')
NOLT_URL = environ.get('NOLT_URL')


@app.get('/')
async def init():
    return RedirectResponse(discord.oauth_login_url)


@app.get(
    "/user",
    dependencies=[Depends(discord.requires_authorization)],
)
async def get_user(
        user: User = Depends(discord.user), guilds: List = Depends(discord.guilds)
):
    return {"user": user, "guilds": guilds}


@app.get('/callback')
async def callback(code: str):
    token, refresh_token = await discord.get_access_token(code)
    async with AsyncClient() as client:
        headers = {"Authorization": "Bearer " + token}
        user_request = await client.get(
            "http://localhost:8000/user", headers=headers
        )
        user_data = user_request.json()
    if ALLOWED_GUILD_ID not in [g["id"] for g in user_data["guilds"]]:
        raise HTTPException(
            status_code=403,
            detail="You are not a member of the permitted guild.  Please contact an administrator if you believe this "
                   "to be an error.",
        )
    user: User = User.parse_obj(user_data["user"])
    payload = {
        "id": user.id,
        "email": user.email,
        "name": user.username,
        "imageUrl": user.avatar_url,
    }
    web_token = jwt.encode(payload, NOLT_SECRET, algorithm="HS256")
    return RedirectResponse(
        url=f"{NOLT_URL}/sso/{web_token}"
    )


if __name__ == '__main__':
    run(app, host='0.0.0.0', port=8000)
