from typing import Any, Generator
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

    def activities(self) -> Generator[dict[str, Any]]:
        endpoint = "https://teamapi.coros.com/activity/query"
        query = {"size": 100, "pageNumber": 1}

        while 1:
            resp = self.session.get(endpoint, params=query)
            resp.raise_for_status()
            data = resp.json()["data"]
            yield from data["dataList"]
            if data["totalPage"] <= query["pageNumber"]:
                break
            query["pageNumber"] += 1

    def activity_detail(self, label_id: str, sport_type: int) -> dict[str, Any]:
        endpoint = "https://teamapi.coros.com/activity/query"
        query = {"size": 100, "pageNumber": 1}

        # NB: yes, this a POST for whatever reason
        resp = self.session.post(endpoint, params=query)
        resp.raise_for_status()
        return resp.json()["data"]
