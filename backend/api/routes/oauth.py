from fastapi import APIRouter, Depends, HTTPException, Request

from api.deps import get_session
from core.oauth import oauth
from services.github_service import GithubService

router = APIRouter()


@router.get("/auth/github/login")
async def github_login(request: Request):
    redirect_uri = request.url_for("github_callback")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/auth/github/callback", name="github_callback")
async def github_callback(request: Request, session=Depends(get_session)):
    token = await oauth.github.authorize_access_token(request)

    resp = await oauth.github.get("user", token=token)
    github_user = resp.json()

    github_id = str(github_user["id"])
    github_login = github_user.get("login") or f"github_{github_id}"
    github_email = github_user.get("email")

    if not github_email:
        emails_resp = await oauth.github.get("user/emails", token=token)
        emails = emails_resp.json()
        primary_email = next((item["email"] for item in emails if item.get("primary")), None)
        github_email = primary_email or (emails[0]["email"] if emails else None)

    if not github_email:
        raise HTTPException(
            status_code=400,
            detail="GitHub не вернул email. Откройте доступ к email в GitHub."
        )

    github_email = github_email.lower()

    service = GithubService(session)
    return await service.handle_callback(github_id, github_login, github_email)