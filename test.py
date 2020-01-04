import asyncio
import sys
from typing import List, Any, Dict
from urllib.parse import urljoin
import json
import requests
import websockets


APIVER = 6
APIURL = f"https://discordapp.com/api/v{APIVER}"


def read_secrets() -> Dict[str, Any]:
    with open("secrets.json") as jf:
        secrets = json.load(jf)
    return secrets


async def connect(token: str) -> Any:
    url = urljoin(APIURL, f"gateway/bot")
    headers = {"Authorization": f"Bot {token}"}
    resp = requests.get(url, headers=headers)
    data = resp.json()
    gwurl = f"{data['url']}?v=6&encoding=json"

    async with websockets.connect(gwurl) as ws:
        hello = await ws.recv()
        print(hello)
        payload = {
            "op": 2,
            'd': {'token': token,
                  "properties": {
                      "$os": "linux",
                      "$browser": "franky",
                      "$device": "franky"}
                  }
        }
        await ws.send(json.dumps(payload))
        identresp = await ws.recv()
        print(identresp)


def get_channels(guild_id: int, token: str) -> List[Dict[str, Any]]:
    url = urljoin(APIURL, f"guilds/{guild_id}/channels")
    headers = {"Authorization": f"Bot {token}"}
    resp = requests.get(url, headers=headers)
    return resp.json()


def print_channels(channels: List[Dict[str, Any]]):
    chan_map: Dict[str, Any] = dict()
    for chan in channels:
        chan_map[chan["id"]] = chan

    for chan in chan_map.values():
        if chan["parent_id"] is not None:
            print(chan_map[chan["parent_id"]]["name"], end=": ")
        print(chan["name"])
        if "topic" in chan:
            topic = chan["topic"]
            print(f'\t"{topic}"')


def send_message(chan_id: str, message: str, token: str):
    url = urljoin(APIURL, f"channels/{chan_id}/messages")
    headers = {"Authorization": f"Bot {token}"}
    print(f"Sending message '{message}'")
    data = {
        "content": message,
    }
    resp = requests.post(url, json=data, headers=headers)
    print(resp)
    print(resp.json())
    return


def get_me(token: str) -> Dict[str, Any]:
    url = urljoin(APIURL, "users/@me/guilds")
    headers = {"Authorization": f"Bot {token}"}
    resp = requests.get(url, headers=headers)
    print(resp.json())
    return resp.json()


def main():
    secrets = read_secrets()

    # asyncio.get_event_loop().run_until_complete(connect(secrets["bot_token"]))

    channels = get_channels(secrets["server_id"], secrets["bot_token"])
    print_channels(channels)

    get_me(secrets["bot_token"])

    general_id = ""
    for chan in channels:
        if chan["name"] == "general":
            general_id = chan["id"]
            break
    else:
        print("No channel with name 'general'")
        sys.exit(1)

    message = "Test message"
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])

    send_message(general_id, message, secrets["bot_token"])


if __name__ == "__main__":
    main()
