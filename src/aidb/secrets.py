import keyring


def load_connection_url() -> str | None:
    return keyring.get_password("aidb", "connection_url")


def store_connection_url(url: str) -> None:
    keyring.set_password("aidb", "connection_url", url)
