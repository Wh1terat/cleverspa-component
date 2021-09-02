import json
import pyrebase
import requests
from .errors import AuthError
from .const import FIREBASE_CONFIG

class auth:

    def login(username, password):
        firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
        auth = firebase.auth()
        db = firebase.database()
        try:
            user = auth.sign_in_with_email_and_password(username, password)
        except requests.exceptions.HTTPError as e:
            e = json.loads(e.strerror)
            raise AuthError(e['error']['message'])
        info = db.child('users').child(user['localId']).get(token=user['idToken']).val()
        return dict(info)

