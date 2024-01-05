import random
import requests
import time
import json
import os
from dotenv import load_dotenv

load_dotenv()

BOT_ID = os.getenv("BOT_ID")
GROUP_ID = os.getenv("GROUP_ID")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GIPHY_API_KEY = os.getenv("GIPHY_API_KEY")
LAST_MESSAGE_ID = None


def send_message(text, attachments=None):
    """Send a message to the group using the bot."""
    post_url = "https://api.groupme.com/v3/bots/post"
    data = {"bot_id": BOT_ID, "text": text, "attachments": attachments or []}
    response = requests.post(post_url, json=data)
    return response.status_code == 202


def get_group_messages(since_id=None):
    """Retrieve recent messages from the group."""
    params = {"token": ACCESS_TOKEN}
    if since_id:
        params["since_id"] = since_id

    get_url = f"https://api.groupme.com/v3/groups/{GROUP_ID}/messages"
    response = requests.get(get_url, params=params)
    if response.status_code == 200:
        # this shows how to use the .get() method to get specifically the messages but there is more you can do (hint: sample.json)
        return response.json().get("response", {}).get("messages", [])
    return []


def get_group_members():
    """Retrieve members of the group."""
    params = {"token": ACCESS_TOKEN}
    get_url = f"https://api.groupme.com/v3/groups/{GROUP_ID}"
    response = requests.get(get_url, params=params)
    if response.status_code == 200:
        return response.json().get("response", {}).get("members", [])
    return []


def process_message(message):
    """Process and respond to a message."""
    global LAST_MESSAGE_ID

    current_message_id = int(message["id"])
    last_message_id = int(LAST_MESSAGE_ID) if LAST_MESSAGE_ID else 0
    if current_message_id > last_message_id:
        sender_id = message["sender_id"]
        members = get_group_members()
        text = message["text"].lower()

        if message["sender_id"] == "67348090" and "hey bot" in text:
            sender = next(
                (member for member in members if member["user_id"] == sender_id), None)
            if sender:
                first_name = sender["nickname"].split()[0]
                send_message(f"Hey, {first_name}!")

        if "good morning" in text:
            first_name = next(
                (member["nickname"].split()[0] for member in members if member["user_id"] == sender_id), None)
            if first_name:
                send_message(f"Good morning, {first_name}!")

        if "good night" in text:
            first_name = next(
                (member["nickname"].split()[0] for member in members if member["user_id"] == sender_id), None)
            if first_name:
                send_message(f"Good night, {first_name}!")
        
        if "what's the date" in text:
            date = time.strftime("%m/%d/%Y")
            send_message(f"The date is {date}.")
        
        if "show me a funny cat gif" in text:
            response = requests.get(
            "https://api.giphy.com/v1/gifs/search",
            params={
                "api_key": GIPHY_API_KEY,
                "q": "funny cat",
                "limit": 10
            }
        )

            if response.status_code == 200:
                gifs = response.json()['data']
                randomGif = random.choice(gifs)
                send_message(randomGif['url'])
            else:
                print("Failed to fetch GIFs")

        LAST_MESSAGE_ID = message["id"]


def get_latest_group_message():
    """Retrieve the most recent message from the group."""
    params = {"token": ACCESS_TOKEN,
              "limit": 1}

    get_url = f"https://api.groupme.com/v3/groups/{GROUP_ID}/messages"
    response = requests.get(get_url, params=params)
    if response.status_code == 200:
        messages = response.json().get("response", {}).get("messages", [])
        if messages:
            return messages[0]
    return None


def main():
    global LAST_MESSAGE_ID
    # this is an infinite loop that will try to read (potentially) new messages every 10 seconds, but you can change this to run only once or whatever you want
    while True:
        latest_message = get_latest_group_message()
        if latest_message:
            process_message(latest_message)
        time.sleep(10)


if __name__ == "__main__":
    main()
