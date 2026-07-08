import os
import json
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/documents"
]

def get_credentials(credentials_path="credentials.json", token_path="token.json"):
    """
    Gets valid user credentials from storage or environment variables.
    If nothing is available, or they are expired, it triggers the OAuth flow.
    """
    creds = None
    
    # First, check if the token is provided via environment variables (e.g., in Railway)
    token_b64 = os.environ.get("GOOGLE_TOKEN_B64")
    if token_b64:
        try:
            token_json = base64.b64decode(token_b64).decode('utf-8')
            token_info = json.loads(token_json)
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except Exception as e:
            print(f"Failed to parse GOOGLE_TOKEN_B64: {e}")

    # Fall back to token.json if no valid creds from env var
    if not creds and os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check for credentials via env var
            creds_b64 = os.environ.get("GOOGLE_CREDENTIALS_B64")
            if creds_b64:
                creds_json = base64.b64decode(creds_b64).decode('utf-8')
                client_config = json.loads(creds_json)
                flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            else:
                if not os.path.exists(credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file '{credentials_path}' not found and GOOGLE_CREDENTIALS_B64 not set. "
                        "Please configure them to authenticate."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                
            # This requires a local browser to complete the flow.
            # In a cloud environment like Railway, this will hang. Users must generate token.json locally first.
            print("Starting local browser for authentication. (This will fail in a headless cloud environment).")
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run (only if not running in cloud where filesystem is ephemeral)
        # But we'll try to save it anyway for local usage.
        try:
            with open(token_path, "w") as token:
                token.write(creds.to_json())
        except Exception:
            pass
            
    return creds
