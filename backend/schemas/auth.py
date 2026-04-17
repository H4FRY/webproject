from pydantic import BaseModel, field_validator

from core.validators import (
    LOGIN_REGEX,
    EMAIL_REGEX,
    PASSWORD_UPPER_REGEX,
    PASSWORD_LOWER_REGEX,
    PASSWORD_DIGIT_REGEX,
    PASSWORD_SPECIAL_REGEX,
)


class RegisterRequest(BaseModel):
    login: str
    email: str
    password: str

    @field_validator("login")
    @classmethod
    def validate_login(cls, value: str) -> str:
        if not LOGIN_REGEX.fullmatch(value):
            raise ValueError("Логин: длина 3–32, только латиница, цифры, '.', '_', '-'")
        return value

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_REGEX.fullmatch(value):
            raise ValueError("Некорректный email")
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Пароль должен содержать минимум 8 символов")
        if not PASSWORD_UPPER_REGEX.search(value):
            raise ValueError("Пароль должен содержать хотя бы 1 заглавную букву")
        if not PASSWORD_LOWER_REGEX.search(value):
            raise ValueError("Пароль должен содержать хотя бы 1 строчную букву")
        if not PASSWORD_DIGIT_REGEX.search(value):
            raise ValueError("Пароль должен содержать хотя бы 1 цифру")
        if not PASSWORD_SPECIAL_REGEX.search(value):
            raise ValueError("Пароль должен содержать хотя бы 1 спецсимвол")
        return value


class RegisterConfirm2FARequest(BaseModel):
    email: str
    otp_code: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return value.lower()


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return value.lower()


class Verify2FARequest(BaseModel):
    email: str
    otp_code: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return value.lower()