import requests

X_ACCOUNT_TOKEN = "eyJhbGciOiJFUzI1NiIsImtpZCI6InByb2QtYWNjb3VudC0yMDI2MDIyNCJ9.eyJlbWFpbFZlcmlmaWVkIjp0cnVlLCJlbmFibGVNZmEiOmZhbHNlLCJleHAiOjE3ODY2MDg2MDUsImlhdCI6MTc4NjYwNzcwNSwiaXNzIjoiYWNjIiwia2V5IjoiNDc4NTQ3Iiwia2V5X2hhc2giOiJkMGUxODg0NGUwYzM2ODA3Iiwic2lkIjoiNmE3ZDcwYmE2YzZiMDNmYzIzNTcifQ.NvNyBdXZbjy5zUWpEhNzYQ9nFroOX6RmQUS0ib7kLzzK8s-oo6Wb5prtulkuYtItW2bW1aMNhGn2EcLBeDYiYA"
CH_SESSION_COOKIE = "eyJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJzZXMiLCJleHAiOjE3ODkxMjYzMTcsImlhdCI6MTc4NjUzNDMxNywia2V5IjoiMS02OTY3YjAxMmNkOTM4MDg2YmI1ZiJ9.MDJAlfW4SKw9-CyiNbG31cWezVfRG_hbAvRzOWM5KIk"
CH_VEIL_ID = "f9f806fe-d17a-4719-be71-486749c5b61e"

def send_test_message(text, CHANNEL_ID , GROUP_ID):

    URL = f"https://api.channel.works/desk/channels/{CHANNEL_ID}/groups/{GROUP_ID}/messages"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://channel.works",
        "referer": "https://channel.works/",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
        ),
        "x-account": X_ACCOUNT_TOKEN,
    }

    cookies = {
        "ch-session-1": CH_SESSION_COOKIE,
        "x-account": X_ACCOUNT_TOKEN,
        "ch-veil-id": CH_VEIL_ID,
    }

    payload = {
        "requestId": "desk-web-test-script",
        "blocks": [
            {"type": "text", "value": text}
        ],
        "buttons": None,
        "form": None,
        "webPage": None,
        "files": None,
        "customPayload": None,
    }

    resp = requests.post(URL, headers=headers, cookies=cookies, json=payload)
    return resp

def get_message(CHANNEL_ID , GROUP_ID):
    URL1 = f"https://api.channel.works/desk/channels/{CHANNEL_ID}/groups/{GROUP_ID}/messages?sortOrder=desc&limit=1&logFolded=false"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "origin": "https://channel.works",
        "referer": "https://channel.works/",
        "user-agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"
        ),
        "x-account": X_ACCOUNT_TOKEN,
    }


    cookies = {
        "ch-session-1": CH_SESSION_COOKIE,
        "x-account": X_ACCOUNT_TOKEN,
        "ch-veil-id": CH_VEIL_ID,
    }

    payload = {
        "sortOrder" : "desc",
        "limit" : "1",
        "logFolded" : "false"
    }
    resp = requests.get(URL1 , headers=headers , cookies=cookies , json=payload)
    #print(resp.json())
    text = resp.json()
    message = text["messages"][0]["plainText"]

    return message
if __name__ == "__main__":
    r = get_message(240996,576454)
    print(r)