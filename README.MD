# POAIBOT

Веб-приложение с авторизацией, 2FA, OAuth через GitHub и Google, историей чатов и локальной LLM-моделью для ответов в стиле чат-ассистента.

## Возможности

- регистрация и вход по email/паролю
- двухфакторная аутентификация (TOTP)
- OAuth через GitHub
- OAuth через Google
- личные чаты с историей сообщений
- потоковый вывод ответа LLM
- кэширование через Redis
- PostgreSQL для хранения данных
- Docker и Docker Compose для запуска проекта

---

## Технологии

### Backend
- Python 3.10
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Redis
- Authlib
- PyOTP
- llama-cpp-python

### Frontend
- React
- Vite
- React Router
- React Markdown

---

## Версии

- Python: **3.10**
- Node.js: **20**
- React: версия из `frontend/package.json`
- PostgreSQL: **16**
- Redis: **7**

---

## Структура проекта

```text
webproject/
├── backend/
│   ├── alembic/
│   ├── api/
│   ├── bd/
│   ├── core/
│   ├── repositories/
│   ├── schemas/
│   ├── services/
│   ├── .env
│   ├── Dockerfile
│   └── main.py
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── README.md
```

## LLM-модель

Файл модели не хранится в git.
Перед запуском нужно скачать GGUF-модель вручную.

Вариант через Hugging Face CLI

``` bash
pip install -U "huggingface_hub[cli]"
```
При необходимости авторизоваться:
``` bash
huggingface-cli login
```
или 
``` bash
hf auth login
```
Создать папку для модели:
``` bash
mkdir -p backend/models
```
Пример:
``` bash
hf download bartowski/Qwen2.5-3B-Instruct-GGUF Qwen2.5-3B-Instruct-IQ4_XS.gguf --local-dir backend/models
```
или 
``` bash
huggingface-cli download bartowski/Qwen2.5-3B-Instruct-GGUF Qwen2.5-3B-Instruct-IQ4_XS.gguf --local-dir backend/models
```
и потом переименовать

``` bash
mv backend/models/Qwen2.5-3B-Instruct-IQ4_XS.gguf backend/models/model.gguf 
```

## 2. Создать файл .env

Создай файл backend/.env
Пример содержимого:
``` 
SESSION_SECRET_KEY=your_session_secret
CORS_ORIGINS=http://localhost:5173,http://localhost:5174

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_SCOPE=openid email profile

GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
GITHUB_SCOPE=read:user user:email

ISSUER_NAME=POAIBOT

JWT_SECRET_KEY=your_jwt_secret
JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

ACCESS_COOKIE_NAME=access_token
REFRESH_COOKIE_NAME=refresh_token

COOKIE_SECURE=False
COOKIE_SAMESITE=lax

DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
DB_NAME=webapp

REDIS_URL=redis://redis:6379/0
```
## Пояснение по переменным
### SESSION_SECRET_KEY

Секретный ключ для сессий. Его можно сгенерировать так:

``` bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```
### GOOGLE_CLIENT_ID и GOOGLE_CLIENT_SECRET

Получаются в Google Cloud Console при создании OAuth-приложения.

### GITHUB_CLIENT_ID и GITHUB_CLIENT_SECRET

Получаются в GitHub:
Settings -> Developer settings -> OAuth Apps

### JWT_SECRET_KEY
Секретный ключ для JWT. Его можно сгенерировать так:
``` bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```
## Значения, которые можно оставить без изменений

Обычно без изменений можно оставить:
```
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
GOOGLE_SCOPE=openid email profile
GITHUB_SCOPE=read:user user:email
ISSUER_NAME=POAIBOT
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30
COOKIE_SECURE=False
COOKIE_SAMESITE=lax 
REDIS_URL=redis://redis:6379/0
```
## Запуск через Docker

Из корня проекта выполни:
``` bash
docker compose up --build
```
После запуска будут доступны:

* Frontend: http://localhost:5173
* Backend: http://localhost:8000
* Swagger UI: http://localhost:8000/docs