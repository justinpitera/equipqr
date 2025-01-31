"""
api/routes/auth.py - API route for user authentication.

Date: December 9, 2024

Authors:
    Justin N. Pitera (justinpitera@gmail.com)
"""

# Standard
import secrets, smtplib, random, datetime
from urllib.parse import urlparse
from typing import LiteralString

# Third-party
from redis.asyncio import Redis
from starlette.responses import JSONResponse, RedirectResponse, Response
from starlette.requests import Request
from tortoise.exceptions import OperationalError, DoesNotExist
from pydantic import BaseModel, EmailStr, ValidationError
from itsdangerous import URLSafeTimedSerializer
from loguru import logger
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Local
from src import API_CONFIG, RedisClient
from src.models import CrewMember

# Protobufs
from src.protos.requests.v1.requests_pb2 import (
    LoginRequest,
    LoginResponse
)

# Initialization
SUCCESS_MESSAGE_REGISTER: str = "Please check your email to continue."
SUCCESS_MESSAGE_VALIDATE: str = "User successfully registered."
BASE_URL: str = API_CONFIG["api"]["domain"] + ":" + str(API_CONFIG["api"]["port"])
TOKEN_SERIALIZER: URLSafeTimedSerializer = URLSafeTimedSerializer(API_CONFIG["auth"]["jwt"]["secret"])


async def set_token(request: Request) -> RedirectResponse:
    """Sets the access token in cookies for existing users and redirects home."""
    TOTP_CLIENT: Redis = await RedisClient.get_client(db=2)
    token = request.query_params.get("token")
    if not token or not (email_data := await TOTP_CLIENT.get(name=token)):
        return RedirectResponse(url=f"{BASE_URL}/", status_code=302)

    # Decode email_data only if necessary
    email: str = email_data if isinstance(email_data, str) else email_data.decode()

    await TOTP_CLIENT.delete(token)

    try:
        # Fetch the user; raise an error if the user doesn't exist
        found_crew_member: CrewMember = await CrewMember.get(email=email)
        logger.info(f"Logged in user: {email}")
    except DoesNotExist:
        logger.error(f"User with email {email} does not exist.")
        return RedirectResponse(url=f"{BASE_URL}/error", status_code=404)
    except OperationalError as e:
        logger.error(f"Database error: {str(e)}")
        return RedirectResponse(url=f"{BASE_URL}/", status_code=500)

    access_token: str = TOKEN_SERIALIZER.dumps(obj=secrets.token_urlsafe(nbytes=32))
    await TOTP_CLIENT.set(name=access_token, value=email, ex=3600)

    secure_flag = urlparse(API_CONFIG["api"]["domain"]).scheme == "https"
    parsed_domain = urlparse(API_CONFIG["api"]["domain"]).hostname
    response: RedirectResponse = RedirectResponse(url=f"{BASE_URL}/", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=secure_flag, samesite="strict", domain=parsed_domain)
    response.set_cookie(key="auth", value="true", httponly=False, secure=secure_flag, samesite="strict", domain=parsed_domain)
    response.set_cookie(key="role", value=found_crew_member.position.value, httponly=False, secure=secure_flag, samesite="strict", domain=parsed_domain)
    response.set_cookie(key="language", value=found_crew_member.language_preference.lower(), httponly=False, secure=secure_flag, samesite="strict", domain=parsed_domain)
    return response


async def auth_user(request: Request) -> Response:
    """
    Handles user registration or login.
    """
    try:
        body: bytes= await request.body()
        auth_user_request: LoginRequest = LoginRequest()
        auth_user_request.ParseFromString(body)

        # Check if the user already exists
        existing_user: CrewMember | None = await CrewMember.get(email=auth_user_request.email)

        # User exists; proceed with sending the access token email
        logger.info(f"Sending access token email to existing user: {existing_user.email}")

        # Generate a secure random token and store it in Redis
        random_token: str = secrets.token_urlsafe(nbytes=32)
        TOTP_CLIENT: Redis = await RedisClient.get_client(db=2)
        await TOTP_CLIENT.set(name=random_token, value=existing_user.email, ex=600)  # Expires in 10 minutes

        await _send_magic_link(email=existing_user.email, random_token=random_token)
        response: LoginResponse = LoginResponse(
            message="Login success"
        )
        return Response(content=response.SerializeToString(), status_code=200)

    except ValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        return Response(
            content=LoginResponse(message="Validation error occurred").SerializeToString(),
            status_code=400,
        )
    except DoesNotExist as e:
        logger.error(f"Does not exist error: {str(e)}")
        return Response(
            content=LoginResponse(message="User does not exist.").SerializeToString(),
            status_code=400,
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return Response(
            content=LoginResponse(message="Unexpected error occurred").SerializeToString(),
            status_code=500,
        )


async def _send_magic_link(email: str, random_token: str) -> None:
    
    """
    Sends an email with a button to set the access token in the user's cookies.
    """
    ALLOWED_DOMAINS: list[str] = API_CONFIG["auth"]["magic"]["allowed_domains"]
    
    # Extract the domain from the email address
    email_domain: str = email.split(sep='@')[-1]
    
    if email_domain not in ALLOWED_DOMAINS:
        logger.warning(f"Email domain '{email_domain}' is restricted.")
        raise ValueError("The email domain is not allowed to receive magic links.")
    
    SUBJECT_LINES: list[str] = [
        "Your Aviator Account Awaits – Streamline Equipment Reporting Today",
        "Quick! Your Aviator Account is Ready to Transform Ground Operations",
        "Empower Your Workflow with Aviator – Get Started Now",
        "Aviator Access: Your Solution for Seamless Issue Reporting",
        "Your Aviator Account is Ready – Simplify Ground Equipment Checks",
        "Set Up Aviator and Become a Ground Operations Hero",
        "Aviator: The Key to Efficient Equipment Maintenance",
        "Your Aviator Account is Waiting – Start Scanning with Ease",
        "Aviator Awaits: Simplify, Scan, and Report with Confidence",
        "Don't Keep Aviator Waiting – Streamline Maintenance Today",
        "Unlock Aviator Access – A Smarter Way to Report and Resolve Issues",
        "Your Exclusive Invitation to Aviator’s Advanced Reporting Tools",
        "Aviator: Turning Ground Equipment Checks into a Breeze",
        "Aviator Setup – Enhance Ground Crew Efficiency in Minutes",
        "Your Aviator Account is Ready – Let's Get Ground Equipment Right"
    ]

    # Link to the new endpoint where the access token will be set
    SET_TOKEN_LINK: str = f"{BASE_URL}{"/api" if API_CONFIG["api"]["mode"] == "production" else ""}/set-token?token={random_token}"
    
    # Email content
    user_message: LiteralString = (
        "Click the button below to securely access your Aviator account."
    )
    
    body: str = (
        f"<html><body style='font-family: Segoe UI, Tahoma, sans-serif; background-color: #121212; color: #e0e0e0; padding: 40px; margin: 0;'>"
        f"<div style='max-width: 600px; margin: auto; background-color: #1e1e1e; border-radius: 8px; overflow: hidden; box-shadow: 0 0 15px rgba(0, 0, 0, 0.3);'>"
        f"<div style='padding: 20px; text-align: center; border-bottom: 1px solid #333;'>"
        f"<h2 style='margin: 0; color: #ffffff;'>Aviator</h2></div>"
        f"<div style='padding: 30px; text-align: center;'>"
        f"<p style='font-size: 15px; line-height: 1.6; margin-bottom: 20px;'>{user_message}</p>"
        f"<a href='{SET_TOKEN_LINK}' style='background-color: #0078D7; color: #ffffff; padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 14px;'>"
        f"Access Aviator</a>"
        f"<p style='margin-top: 30px; font-size: 13px; color: #b3b3b3;'>If you did not request this email, please ignore it.</p></div>"
        f"<div style='padding: 15px; background-color: #161616; text-align: center; font-size: 11px; color: #666;'>"
        f"© {datetime.date.today().year} Aviator<br>All rights reserved.</div></div></body></html>"
    )
    
    msg: MIMEMultipart = MIMEMultipart(_subtype="related")
    msg["Subject"] = random.choice(seq=SUBJECT_LINES)
    msg["From"] = f"no-reply@{API_CONFIG['smtp']['domain']}"
    msg["To"] = email
    msg.attach(payload=MIMEText(_text=body, _subtype="html"))
    
    try:
        with smtplib.SMTP(host=API_CONFIG["smtp"]["host"], port=API_CONFIG["smtp"]["port"]) as server:
            _ = server.starttls()
            _ = server.login(user=API_CONFIG["smtp"]["username"], password=API_CONFIG["smtp"]["password"])
            _ = server.send_message(msg)
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication failed: {str(e)}")
        raise RuntimeError("Authentication with the SMTP server failed")
    except smtplib.SMTPConnectError as e:
        logger.error(f"Failed to connect to the SMTP server: {str(e)}")
        raise RuntimeError("Unable to connect to the SMTP server")
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {str(e)}")
        raise RuntimeError("An error occurred while sending the email")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise RuntimeError("An unexpected error occurred while sending the email")
