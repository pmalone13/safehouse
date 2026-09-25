"""Run this ONCE, interactively, on a machine with a real browser --
NOT on the headless VM. Third independent consent (after Gmail, Drive),
same pattern: reuses the SAME Google Cloud OAuth client Gmail/Drive
already use -- just enable the "Photos Library API" on that same Cloud
project first (Paul did this 2026-09-25).

    python authorize_photos_once.py

Point this at a COPY of the same client secret file Gmail/Drive use
(same Client ID/secret work for any API enabled on that Cloud project) --
save it as .photos_api_client_secret.json, or literally copy the
existing file to that name.

Opens a browser for you to sign in as tedassistent@gmail.com and grant
Photos (readonly) access, then writes .photos_api_token.json next to
this file. Copy that one file (only) to the same path on the VM
afterward.

Scope is `photoslibrary.readonly` -- per Google's 2025 policy change,
this mostly only surfaces app-created content and items explicitly
shared with this account (e.g. an album Paul shares with
tedassistent@gmail.com via Google Photos' own sharing feature), not
Paul's whole library. Test with list_shared_albums() after copying the
token over -- don't assume it works until you've seen a real shared
album come back.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

from google_client import PHOTOS_CLIENT_SECRET_PATH, PHOTOS_SCOPES, PHOTOS_TOKEN_PATH


def main():
    if not PHOTOS_CLIENT_SECRET_PATH.exists():
        raise FileNotFoundError(
            f"{PHOTOS_CLIENT_SECRET_PATH} not found -- copy your existing "
            "Gmail/Drive OAuth client secret to this filename (same Cloud "
            "project/client works), after enabling the Photos Library API "
            "on that project in the Cloud Console."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(PHOTOS_CLIENT_SECRET_PATH), PHOTOS_SCOPES)
    creds = flow.run_local_server(port=0)
    PHOTOS_TOKEN_PATH.write_text(creds.to_json())
    print(f"Saved Photos API token to {PHOTOS_TOKEN_PATH}")


if __name__ == "__main__":
    main()
