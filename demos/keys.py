"""Find an API key without ever writing it into code.

Order: environment variable, then Colab Secrets (the key icon in Colab's left sidebar).
"""
import os


def get_key(name: str) -> str | None:
    if os.environ.get(name):
        return os.environ[name]
    try:  # running inside Google Colab?
        from google.colab import userdata  # type: ignore
        value = userdata.get(name)
        if value:
            os.environ[name] = value
            return value
    except Exception:
        pass
    return None


def require_key(name: str, where: str) -> str:
    key = get_key(name)
    if not key:
        raise SystemExit(
            f"\n{name} not found.\n"
            f"  • Colab: click the key icon (Secrets) in the left sidebar, add {name}, "
            f"toggle 'Notebook access' on.\n"
            f"  • Laptop: set an environment variable, e.g.  export {name}=...\n"
            f"  Get a key at: {where}\n")
    return key
