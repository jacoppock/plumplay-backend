from typing import Any

from .settings import *  # noqa: F401, F403

DEBUG = False

DATABASES: dict[str, Any] = {  # type: ignore
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "plumplay-db",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": 5436,
    }
}
