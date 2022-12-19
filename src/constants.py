import os
from types import SimpleNamespace


DB = SimpleNamespace(
    name=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASS"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
)

EMAIL = SimpleNamespace(
    host=os.getenv("EMAIL_HOST"),
    username=os.getenv("EMAIL_USERNAME"),
    password=os.getenv("EMAIL_PASSWORD"),
    port=os.getenv("EMAIL_PORT"),
)