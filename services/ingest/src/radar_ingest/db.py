import os

import psycopg
from dotenv import find_dotenv, load_dotenv


def connect() -> psycopg.Connection:
    """Open a connection to the database named by DATABASE_URL.

    The variable comes from the environment (CI) or from the .env file in the
    repository root, which find_dotenv() locates by walking up from this file.
    """
    load_dotenv(find_dotenv())
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env in the repository root "
            "and fill in the Neon connection string."
        )
    return psycopg.connect(url)
