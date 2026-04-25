import { useState } from "react";
import {
  Link,
  useLocation,
  useNavigate,
  useSearchParams,
} from "react-router-dom";
import "./MfaPage.css";

function MfaPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  const [theme] = useState(() => {
    return localStorage.getItem("app-theme") || "dark";
  });

  const email =
    location.state?.email || searchParams.get("email") || "";

  const [otpCode, setOtpCode] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/login/verify-2fa", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          email,
          otp_code: otpCode,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Ошибка подтверждения");
        return;
      }

      navigate("/chat");
    } catch (err) {
      setError("Не удалось подключиться к серверу");
    } finally {
      setLoading(false);
    }
  }

  if (!email) {
    return (
      <div className={`mfa-page ${theme}`}>
        <div className="mfa-brand">POAIBOT</div>

        <div className="mfa-card">
          <h1>Нет данных для входа</h1>
          <p className="mfa-subtitle">
            Сначала выполните вход по email, паролю или через GitHub
          </p>

          <div className="mfa-links single">
            <Link to="/login">Назад ко входу</Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`mfa-page ${theme}`}>
      <div className="mfa-brand">POAIBOT</div>

      <div className="mfa-card">
        <h1>Подтвердите личность</h1>
        <p className="mfa-subtitle">
          Введите одноразовый 6-значный код из приложения-аутентификатора
        </p>

        <form className="mfa-form" onSubmit={handleSubmit}>
          <div className="mfa-field">
            <label htmlFor="otp_code">Одноразовый код</label>
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

          <button type="submit" className="mfa-submit" disabled={loading}>
            {loading ? "Проверка..." : "Продолжить"}
          </button>

          {error && <div className="mfa-alert error">{error}</div>}
        </form>

        <div className="mfa-links">
          <Link to="/login">Назад</Link>
        </div>
      </div>

      <div className="mfa-footer">
        <a href="/">Условия использования</a>
        <span>|</span>
        <a href="/">Политика конфиденциальности</a>
      </div>
    </div>
  );
}

export default MfaPage;