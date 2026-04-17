import io
import base64

import pyotp
import qrcode

from .config import settings


def make_qr_base64(data: str) -> str:
    img = qrcode.make(data)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def build_totp_data(email: str) -> dict:
    secret = pyotp.random_base32()
    totp = pyotp.TOTP(secret)

    provisioning_uri = totp.provisioning_uri(
        name=email,
        issuer_name=settings.issuer_name,
    )

    qr_code_base64 = make_qr_base64(provisioning_uri)

    return {
        "secret": secret,
        "provisioning_uri": provisioning_uri,
        "qr_code_base64": qr_code_base64,
    }


def verify_totp_code(secret: str, otp_code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(otp_code)