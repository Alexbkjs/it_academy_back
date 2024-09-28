import hmac
import hashlib
import urllib.parse
import json
from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from dotenv import load_dotenv  # For loading environment variables from .env file
import os  # For accessing environment variables

# Load environment variables from .env file
load_dotenv()


def validate_init_data(init_data_raw: str, bot_token: str) -> dict:
    """
    Validate the initial data received from the client.
    """
    # Parse initDataRaw into a dictionary
    params = dict(x.split("=", 1) for x in init_data_raw.split("&"))

    # Decode the 'user' field from URL encoding
    params["user"] = urllib.parse.unquote(params.get("user", ""))

    # Extract and decode user data
    user_data_str = params.get("user", "")
    try:
        user_data_str = urllib.parse.unquote(
            user_data_str
        )  # URL-decode the user data string
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid user data format")

    # Create the data_check_string for HMAC validation
    data_check_string = "\n".join(
        f"{key}={value}" for key, value in sorted(params.items()) if key != "hash"
    )

    # Create the secret key with HMAC
    secret_key = hmac.new(
        "WebAppData".encode(), bot_token.encode(), hashlib.sha256
    ).digest()

    # Generate the HMAC hash for validation
    calculated_hash = hmac.new(
        key=secret_key, msg=data_check_string.encode(), digestmod=hashlib.sha256
    ).hexdigest()

    # Compare the calculated hash with the provided hash
    if calculated_hash != params.get("hash", ""):
        raise HTTPException(status_code=400, detail="Invalid hash")

    # Uncomment if needed to validate auth_date for outdated data
    # current_time = int(time.time())
    # if current_time - int(params["auth_date"]) > 86400:  # Check if it's older than 24 hours
    #     raise HTTPException(status_code=400, detail="Outdated data")

    # Everything is good otherwise!
    return params


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exclude all paths starting with /docs and /openapi.json from the authorization check
        if (
            request.url.path.startswith("/docs")
            or request.url.path == "/openapi.json"
            or request.url.path == "/health"
            or request.url.path == "/favicon.ico"
        ):
            # Directly proceed without checking authorization
            return await call_next(request)

        # Extract Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("tma "):
            raise HTTPException(
                status_code=400,
                detail="Authorization header missing or improperly formatted",
            )

        # Extract initDataRaw from the header (after "tma ")
        init_data_raw = auth_header[len("tma ") :]

        # Access environment variables using os.getenv
        bot_token = os.getenv(
            "BOT_TOKEN"
        )  # Retrieve the bot token from environment variables
        # Validate the initial data (replace `bot_token` with your actual bot token or configuration)
        params = validate_init_data(init_data_raw, bot_token)

        # Add validated params to the request state for later use
        request.state.validated_params = params

        # Continue processing the request
        response = await call_next(request)
        return response
