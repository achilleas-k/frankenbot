import asyncio
import sys
from typing import List, Any, Dict, Optional
from urllib.parse import urljoin
import json
import requests
import websockets


APIVER = 6
APIURL = f"https://discordapp.com/api/v{APIVER}"


commands = {
    "message": "Test the connection by sending a message (param: message)",
    "create-role": "Create a role (param: role name)",
    "add-role": "Add a role to a user (params: username, rolename)",
    "help": "This help message",
}


def usage():
    cmdstr = "  " + "\n  ".join(name + "\n\t" + desc
                                for name, desc in commands.items())
    print(f"USAGE: {sys.argv[0]} <command> [params]...\n\n"
          "Available Commands\n"
          f"{cmdstr}"
          )


def die(msg: Optional[Any] = 1):
    sys.exit(msg)


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


def send_message(message: str, token: str, server_id: int):
    channels = get_channels(server_id, token)

    chan_id = ""
    for chan in channels:
        if chan["name"] == "general":
            chan_id = chan["id"]
            break
    else:
        die("No channel with name 'general'")

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


def create_role(name: str, token: str, server_id: int):
    url = urljoin(APIURL, f"guilds/{server_id}/roles")
    headers = {"Authorization": f"Bot {token}"}
    data = {
        "name": name,
    }
    resp = requests.post(url, json=data, headers=headers)
    print(resp)
    print(resp.json())


def get_user_by_name(username: str, token: str, server_id: int) -> Dict[str, Any]:
    # note: Usernames are not unique; this function is bad
    url = urljoin(APIURL, f"guilds/{server_id}/members")
    headers = {"Authorization": f"Bot {token}"}
    resp = requests.get(url, headers=headers)
    for member in resp.json():
        if username == member["user"]["username"]:
            return member["user"]
    die(f"No user with name '{username}'")


def get_role_by_name(rolename: str, token: str, server_id: int) -> Dict[str, Any]:
    # note: Usernames are not unique; this function is bad
    url = urljoin(APIURL, f"guilds/{server_id}/roles")
    headers = {"Authorization": f"Bot {token}"}
    resp = requests.get(url, headers=headers)
    for role in resp.json():
        if rolename == role["name"]:
            return role
    die(f"No role with name '{rolename}'")


def add_role(username: str, rolename: str, token: str, server_id: int):
    user = get_user_by_name(username, token, server_id)
    role = get_role_by_name(rolename, token, server_id)

    user_id = user["id"]
    role_id = role["id"]
    url = urljoin(APIURL, f"guilds/{server_id}/members/{user_id}/roles/{role_id}")
    headers = {"Authorization": f"Bot {token}"}
    resp = requests.put(url, headers=headers)
    print(resp)


def main():

    if len(sys.argv) < 2:
        die(usage())

    command = sys.argv[1]
    if command not in commands or command == "help":
        die(usage())

    args = sys.argv[2:]

    secrets = read_secrets()

    # the following is used to log in to the gateway, which is required to do
    # at least once before sending a message
    # https://discordapp.com/developers/docs/resources/channel#create-message
    # asyncio.get_event_loop().run_until_complete(connect(secrets["bot_token"]))

    token = secrets["bot_token"]
    server_id = secrets["server_id"]

    if command == "message":
        if len(args) != 1:
            die(usage())
        send_message(args[0], token, server_id)
    elif command == "create-role":
        if len(args) != 1:
            die(usage())
        create_role(args[0], token, server_id)
    elif command == "add-role":
        if len(args) != 2:
            die(usage())
        username, rolename = args
        add_role(username, rolename, token, server_id)


if __name__ == "__main__":
    main()
