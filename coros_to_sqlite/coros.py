import requests


class CorosClient:
    def __init__(self, email: str, password_md5: str):
        self._email = email
        self._password = password_md5
        self.session = requests.Session()
        self.authorize()

    def authorize(self):
        response = self.session.post(
            "https://teamapi.coros.com/account/login",
            json={
                "account": self._email,
                "accountType": 2,
                "pwd": self._password,
            },
        )
        response.raise_for_status()
        self.session.headers["accessToken"] = response.json()["data"]["accessToken"]
