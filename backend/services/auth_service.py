from fastapi import HTTPException

from repositories.user_repository import UserRepository
from core.security import hash_password, verify_password
from core.totp import build_totp_data, verify_totp_code


class AuthService:
    def __init__(self, session):
        self.repo = UserRepository(session)

    async def register(self, login: str, email: str, password: str):
        existing_user = await self.repo.get_by_email(email)
        if existing_user:
            raise HTTPException(status_code=400, detail="Такой email уже существует")

        totp_data = build_totp_data(email)
        hashed_password = hash_password(password)

        new_user = await self.repo.create_user(
            login=login,
            email=email,
            password_hash=hashed_password,
            totp_secret=totp_data["secret"],
            is_2fa_enabled=False,
        )

        return {
            "message": "Пользователь создан. Подтвердите 2FA-код",
            "id": new_user.id,
            "login": new_user.login,
            "email": new_user.email,
            "qr_code_base64": totp_data["qr_code_base64"],
            "otpauth_url": totp_data["provisioning_uri"],
        }

    async def confirm_register_2fa(self, email: str, otp_code: str):
        user = await self.repo.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        if not user.totp_secret:
            raise HTTPException(status_code=400, detail="2FA не настроен")

        if not verify_totp_code(user.totp_secret, otp_code):
            raise HTTPException(status_code=400, detail="Неверный код подтверждения")

        user.is_2fa_enabled = True
        await self.repo.commit()

        return {"message": "Регистрация завершена, 2FA успешно включен"}

    async def login(self, email: str, password: str):
        user = await self.repo.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=400, detail="Неверный email или пароль")

        if not user.password_hash:
            raise HTTPException(
                status_code=400,
                detail="Для этого аккаунта используйте вход через GitHub"
            )

        if not verify_password(password, user.password_hash):
            raise HTTPException(status_code=400, detail="Неверный email или пароль")

        if user.is_2fa_enabled:
            return {
                "requires_2fa": True,
                "email": user.email,
                "message": "Введите код из приложения-аутентификатора"
            }

        return {
            "requires_2fa": False,
            "message": "Вход выполнен успешно",
            "id": user.id,
            "login": user.login,
            "email": user.email,
        }

    async def verify_login_2fa(self, email: str, otp_code: str):
        user = await self.repo.get_by_email(email)
        if user is None:
            raise HTTPException(status_code=400, detail="Пользователь не найден")

        if not user.is_2fa_enabled or not user.totp_secret:
            raise HTTPException(status_code=400, detail="2FA не включен")

        if not verify_totp_code(user.totp_secret, otp_code):
            raise HTTPException(status_code=400, detail="Неверный одноразовый код")

        return {
            "message": "Вход выполнен успешно",
            "id": user.id,
            "login": user.login,
            "email": user.email,
        }