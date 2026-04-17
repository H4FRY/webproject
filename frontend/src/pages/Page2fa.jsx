import { useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import "./Page2fa.css";

function Page2fa() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  const [theme] = useState(() => {
    return localStorage.getItem("app-theme") || "dark";
  });

  const email =
    location.state?.email || searchParams.get("email") || "";

  const qrCodeBase64 =
    location.state?.qrCodeBase64 || searchParams.get("qr") || "";

  const otpauthUrl =
    location.state?.otpauthUrl || searchParams.get("otpauth") || "";

  const [otpCode, setOtpCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    setLoading(true);

    try {
      const response = await fetch("http://127.0.0.1:8000/register/confirm-2fa", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          otp_code: otpCode,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Ошибка подтверждения 2FA");
        return;
      }

      setMessage("2FA успешно подключен");

      setTimeout(() => {
        navigate("/chat");
      }, 1000);
    } catch (err) {
      setError("Не удалось подтвердить 2FA");
    } finally {
      setLoading(false);
    }
  }

  if (!email || !qrCodeBase64) {
    return (
      <div className={`page2fa-page ${theme}`}>
        <div className="page2fa-brand">POAIBOT</div>

        <div className="page2fa-card">
          <h1>Нет данных для подтверждения</h1>
          <p className="page2fa-subtitle">
            Сначала завершите регистрацию или вход через GitHub
          </p>

          <div className="page2fa-links single">
            <Link to="/register">Назад к регистрации</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`page2fa-page ${theme}`}>
      <div className="page2fa-brand">POAIBOT</div>

      <div className="page2fa-card">
        <h1>Подключите 2FA</h1>
        <p className="page2fa-subtitle">
          Отсканируйте QR-код в приложении-аутентификаторе и введите 6-значный код
        </p>

        <div className="page2fa-qr-block">
          <img
            className="page2fa-qr-image"
            src={`data:image/png;base64,${qrCodeBase64}`}
            alt="QR code"
          />
        </div>

        {otpauthUrl && (
          <p className="page2fa-note">
            Если QR не сканируется, добавьте ключ вручную в приложение-аутентификатор.
          </p>
        )}

        <form className="page2fa-form" onSubmit={handleSubmit}>
          <div className="page2fa-field">
            <label htmlFor="otp_code">6-значный код</label>
            <input
              id="otp_code"
              type="text"
              name="otp_code"
              value={otpCode}
              onChange={(e) =>
                setOtpCode(e.target.value.replace(/\D/g, "").slice(0, 6))
              }
              placeholder="Введите код"
              autoComplete="one-time-code"
              maxLength={6}
            />
          </div>

          <button type="submit" className="page2fa-submit" disabled={loading}>
            {loading ? "Проверка..." : "Подтвердить 2FA"}
          </button>

          {message && <div className="page2fa-alert success">{message}</div>}
          {error && <div className="page2fa-alert error">{error}</div>}
        </form>

        <div className="page2fa-links">
          <Link to="/login">Назад</Link>
        </div>
      </div>

      <div className="page2fa-footer">
        <a href="/">Условия использования</a>
        <span>|</span>
        <a href="/">Политика конфиденциальности</a>
      </div>
    </div>
  );
}

export default Page2fa;