import base64
import time
from typing import Optional

import requests
from base import settings


class TokenManager:
    def __init__(self, client_id: str, client_secret: str, token_url: str, scope: Optional[str] = None) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.scope = scope
        self.access_token = None
        self.expiration_time = 0

    def get_token(self) -> str:
        current_time = time.time()
        if self.access_token and current_time < self.expiration_time:
            return self.access_token
        else:
            self._fetch_new_token()
            return self.access_token  # type: ignore

    def _fetch_new_token(self) -> None:
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = auth_string.encode("ascii")
        auth_base64 = base64.b64encode(auth_bytes).decode("ascii")

        headers = {"Authorization": f"Basic {auth_base64}", "Content-Type": "application/x-www-form-urlencoded"}

        data = {"grant_type": "client_credentials"}

        if self.scope:
            data["scope"] = self.scope

        response = requests.post(self.token_url, headers=headers, data=data)

        if response.status_code == 200:
            token_response = response.json()
            self.access_token = token_response.get("access_token")
            expires_in = token_response.get("expires_in", 3600)  # Default to 1 hour if not provided
            self.expiration_time = time.time() + expires_in - 60  # Subtract 60 seconds as a buffer
        else:
            error_message = (
                f"Failed to obtain access token. Status code: {response.status_code}, Error: {response.text}"
            )
            raise Exception(error_message)


def get_token_manager() -> TokenManager:
    return TokenManager(
        settings.MEDPLUM_CLIENT_ID, settings.MEDPLUM_CLIENT_SECRET, "https://api.medplum.dev.automated.co/oauth2/token"
    )
