"""Run this ONCE, interactively, on a machine with a real browser --
NOT on the headless VM. Separate from authorize_once.py (Gmail) on
purpose: Gmail was already consented to once, and re-running that flow
just to add Drive scope would mean redoing a manual step that's already
done. This is a genuinely new, additional consent -- but reuses the SAME
Google Cloud OAuth client Gmail already uses (just enable the Drive API
on that same Cloud project first; no new OAuth client needed).

    python authorize_drive_once.py

You can point this at a COPY of the same client secret file Gmail uses
(same Client ID/secret work for any API enabled on that Cloud project) --
just save it as .drive_api_client_secret.json instead of
.gmail_api_client_secret.json, or literally copy the existing file to
that name.

Opens a browser for you to sign in as tedassistent@gmail.com and grant
Drive access, then writes .drive_api_token.json next to this file. Copy
that one file (only) to the same path on the VM afterward.
"""
from google_auth_oauthlib.flow import InstalledAppFlow

from google_client import DRIVE_CLIENT_SECRET_PATH, DRIVE_SCOPES, DRIVE_TOKEN_PATH


def main():
    if not DRIVE_CLIENT_SECRET_PATH.exists():
        raise FileNotFoundError(
            f"{DRIVE_CLIENT_SECRET_PATH} not found -- copy your existing "
            "Gmail OAuth client secret to this filename (same Cloud "
            "project/client works), after enabling the Drive API on "
            "that project in the Cloud Console."
        )
    flow = InstalledAppFlow.from_client_secrets_file(str(DRIVE_CLIENT_SECRET_PATH), DRIVE_SCOPES)
    creds = flow.run_local_server(port=0)
    DRIVE_TOKEN_PATH.write_text(creds.to_json())
    print(f"Saved Drive API token to {DRIVE_TOKEN_PATH}")


if __name__ == "__main__":
    main()
