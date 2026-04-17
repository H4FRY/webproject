from fastapi import HTTPException
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode

from repositories.user_repository import UserRepository
from core.totp import build_totp_data, make_qr_base64
import pyotp


class GithubService:
    def __init__(self, session):
        self.repo = UserRepository(session)

    async def handle_callback(self, github_id: str, github_login: str, github_email: str):
        db_user = await self.repo.get_by_github_id(github_id)

        if db_user is None:
            existing_email_user = await self.repo.get_by_email(github_email)

            if existing_email_user:
                existing_email_user.github_id = github_id
                existing_email_user.github_login = github_login
                existing_email_user.github_email = github_email
                await self.repo.commit()
                db_user = existing_email_user
            else:
                unique_login = await self.repo.generate_unique_login(github_login)
                totp_data = build_totp_data(github_email)

                db_user = await self.repo.create_user(
                    login=unique_login,
                    email=github_email,
                    password_hash=None,
                    github_id=github_id,
                    github_login=github_login,
                    github_email=github_email,
                    totp_secret=totp_data["secret"],
                    is_2fa_enabled=False,
                )

                params = urlencode({
                    "email": db_user.email,
                    "qr": totp_data["qr_code_base64"],
                    "otpauth": totp_data["provisioning_uri"],
                })

                return RedirectResponse(
                    url=f"http://localhost:5173/register/confirm-2fa?{params}"
                )

        if not db_user.is_2fa_enabled:
            if not db_user.totp_secret:
                totp_data = build_totp_data(db_user.email)
                db_user.totp_secret = totp_data["secret"]
                await self.repo.commit()
            else:
                totp = pyotp.TOTP(db_user.totp_secret)
                provisioning_uri = totp.provisioning_uri(
                    name=db_user.email,
                    issuer_name="POAIBOT",
                )
                totp_data = {
                    "secret": db_user.totp_secret,
                    "provisioning_uri": provisioning_uri,
                    "qr_code_base64": make_qr_base64(provisioning_uri),
                }

            params = urlencode({
                "email": db_user.email,
                "qr": totp_data["qr_code_base64"],
                "otpauth": totp_data["provisioning_uri"],
            })

            return RedirectResponse(
                url=f"http://localhost:5173/register/confirm-2fa?{params}"
            )

        params = urlencode({"email": db_user.email})
        return RedirectResponse(
            url=f"http://localhost:5173/login/verify-2fa?{params}"
        )