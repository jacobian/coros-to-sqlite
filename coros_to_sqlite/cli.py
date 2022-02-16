import hashlib
import json
from pathlib import Path
from typer import Option, Argument, Typer
from .coros import CorosClient
import sqlite_utils

cli = Typer()


@cli.command()
def auth(
    email: str = Option(..., prompt=True),
    password: str = Option(..., prompt=True, hide_input=True),
    auth: Path = Option(
        Path("auth.json"),
        "-a",
        file_okay=True,
        dir_okay=False,
        help="path to save auth data to",
    ),
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
    auth: Path = Option(
        Path("auth.json"),
        "-a",
        file_okay=True,
        dir_okay=False,
        exists=True,
        help="path to read auth data from (create with `coros-to-sqlite auth`)",
    ),
):

    db = sqlite_utils.Database(database)

    auth_data = json.loads(auth.read_text())["coros"]
    coros = CorosClient(
        email=auth_data["email"], password_md5=auth_data["password_md5"]
    )
    activities = coros.activities()
    db["activities"].upsert_all(activities, pk="labelId", alter=True)
