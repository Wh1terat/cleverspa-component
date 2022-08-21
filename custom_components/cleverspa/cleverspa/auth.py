import requests
from .errors import AuthError
from .const import GOOGLE_AUTH_URL, GOOGLE_AUTH_KEY, FIREBASE_DB


class auth:
    def login(email, password):
        try:
            user = requests.post(
                GOOGLE_AUTH_URL,
                params={"key": GOOGLE_AUTH_KEY},
                json={"email": email, "password": password, "returnSecureToken": True},
            ).json()
        except requests.exceptions.HTTPError as e:
            e = e.response.json()
            raise AuthError(e["error"]["message"])
        try:
            info = requests.get(
                f"{FIREBASE_DB}/users/{user['localId']}.json",
                params={"auth": user["idToken"]},
            ).json()
        except requests.exceptions.HTTPError as e:
            e = e.response.json()
            raise AuthError(e["error"]["message"])
        return dict(info)
