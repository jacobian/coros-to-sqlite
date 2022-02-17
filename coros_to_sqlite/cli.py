import hashlib
import json
from pathlib import Path
import sqlite_utils
from rich.progress import track
from typer import Argument, Option, Typer
from .coros import CorosClient

cli = Typer()

AUTH_OPTION = Option(
    Path("auth.json"),
    "-a",
    file_okay=True,
    dir_okay=False,
    help="path to save auth data to",
)


@cli.command()
def auth(
    email: str = Option(..., prompt=True),
    password: str = Option(..., prompt=True, hide_input=True),
    auth: Path = AUTH_OPTION,
):
    auth_data = json.loads(auth.read_text()) if auth.exists() else {}
    auth_data["coros"] = {
        "email": email,
        "password_md5": hashlib.md5(password.encode("utf-8")).hexdigest(),
    }
    auth.write_text(json.dumps(auth_data, indent=2))


@cli.command()
def activities(
    database: Path = Argument(Path("coros.db"), file_okay=True, dir_okay=False),
    auth: Path = AUTH_OPTION,
):

    db = sqlite_utils.Database(database)

    auth_data = json.loads(auth.read_text())["coros"]
    coros = CorosClient(
        email=auth_data["email"], password_md5=auth_data["password_md5"]
    )

    activities = list(coros.activities())
    for activity in track(activities, total=len(activities)):
        detail = coros.activity_detail(activity)

        # What to store? The API is rather a mess: the list view returns a different
        # set of fields from the detail view. So merge them. Update from the "summary"
        # field to hoist those fields up in to proper columns.
        record = dict(activity)
        record.update(detail["summary"])

        # Now copy over some dicts to store as JSON fields. Avoid storing
        # `frequencyList` which is a point-by-point recording of the activity. I
        # do want that data but I'm not sure a massive JSON field is exactly
        # what I want here. We also want to "hoist" the summary field up into
        # the top level, so that those fields get proper columns.
        record["deviceList"] = detail["deviceList"]
        record["lapList"] = detail["lapList"]
        record["pauseList"] = detail["pauseList"]
        record["weather"] = detail.get("weather", None)
        record["zoneList"] = detail["zoneList"]

        # Not super efficiant to do this one at a time but whatever.
        db["activities"].upsert(record, pk="labelId", alter=True)
