"""Run this ONCE, interactively, on a machine with a real browser --
NOT on the headless VM (see google_client.py's docstring for why).

    python authorize_once.py

Opens a browser for you to sign in as tedassistent@gmail.com and grant
Gmail access, then writes .gmail_api_token.json next to this file. Copy
that one file (only) to the same path on the VM afterward -- the client
secret never needs to leave whichever machine you ran this on.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

from google_client import GMAIL_CLIENT_SECRET_PATH, GMAIL_SCOPES, GMAIL_TOKEN_PATH


def main():
    if not GMAIL_CLIENT_SECRET_PATH.exists():
        raise FileNotFoundError(
            f"{GMAIL_CLIENT_SECRET_PATH} not found -- download it from the "
            "Google Cloud Console (APIs & Services > Credentials > your "
            "Desktop app OAuth client > Download JSON) and place it there first."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(GMAIL_CLIENT_SECRET_PATH), GMAIL_SCOPES)
    creds = flow.run_local_server(port=0)
    GMAIL_TOKEN_PATH.write_text(creds.to_json())
    print(f"Saved Gmail API token to {GMAIL_TOKEN_PATH}")


if __name__ == "__main__":
    main()
