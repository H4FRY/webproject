class Settings:
    session_secret_key = "Qw8L7mYgT3rP0xK9nV2cA5uH1jD6sF4zB8wR2tN7"
    cors_origins = ["http://localhost:5173", "http://localhost:5174"]

    google_client_id = "gg"
    google_client_secret = "aa"
    google_scope = "openid email profile"

    github_client_id = "Ov23liQf2xLci0jwiHAc"
    github_client_secret = "e72c480191e6c0a2b29c520a1ed98f8f2adbe080"

    github_scope = "read:user user:email"
    issuer_name = "POAIBOT"

    jwt_secret_key = "1d2f4YJ2M3xI5QfQJ7f7v4HCFYHhP0A4WvDk0n2f7uZ5jS8QnCk7eL3pM9xTqAbC"
    jwt_algorithm = "HS256"

    access_token_expire_minutes = 15
    refresh_token_expire_days = 30

    access_cookie_name = "access_token"
    refresh_cookie_name = "refresh_token"

    cookie_secure = False
    cookie_samesite = "lax"

settings = Settings()


