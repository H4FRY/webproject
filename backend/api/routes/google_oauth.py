from fastapi import APIRouter, Depends, HTTPException, Request

from api.deps import get_session
from core.oauth import oauth
from services.google_service import GoogleService

router = APIRouter()


@router.get("/auth/google/login")
async def google_login(request: Request):
    redirect_uri = "http://localhost:8000/auth/google/callback"
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback", name="google_callback")
async def google_callback(request: Request, session=Depends(get_session)):
    token = await oauth.google.authorize_access_token(request)

    resp = await oauth.google.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        token=token,
    )
    user_info = resp.json()

    google_id = user_info.get("sub")
    google_email = user_info.get("email")
    google_name = user_info.get("name")
    google_picture = user_info.get("picture")

    if not google_id or not google_email:
        raise HTTPException(
            status_code=400,
            detail="Google не вернул обязательные данные пользователя",
        )

    service = GoogleService(session)
    return await service.handle_callback(
        google_id=google_id,
        google_email=google_email.lower(),
        google_name=google_name,
        google_picture=google_picture,
    )