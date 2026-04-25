import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./RegisterPage.css";

function RegisterPage() {
  const navigate = useNavigate();

  const [theme] = useState(() => {
    return localStorage.getItem("app-theme") || "dark";
  });

  const [form, setForm] = useState({
    login: "",
    email: "",
    password: "",
  });

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  function handleChange(e) {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage("");
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (!response.ok) {
        if (Array.isArray(data.detail)) {
          setError(data.detail.map((item) => item.msg).join(", "));
        } else {
          setError(data.detail || "Ошибка регистрации");
        }
        return;
      }

      setMessage("Аккаунт создан. Переход к подтверждению 2FA...");

      setTimeout(() => {
        navigate("/register/confirm-2fa", {
          state: {
            email: data.email,
            qrCodeBase64: data.qr_code_base64,
            otpauthUrl: data.otpauth_url,
          },
        });
      }, 700);
    } catch (err) {
      setError("Не удалось подключиться к серверу");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={`register-page ${theme}`}>
      <div className="register-brand">POAIBOT</div>

      <div className="register-card">
        <h1>Создайте аккаунт</h1>
        <p className="register-subtitle">
          Введите логин, email и пароль для регистрации
        </p>

        <form className="register-form" onSubmit={handleSubmit}>
          <div className="register-field">
            <label htmlFor="login">Логин</label>
            <input
              id="login"
              type="text"
              name="login"
              value={form.login}
              onChange={handleChange}
              placeholder="Введите логин"
              autoComplete="username"
            />
          </div>

          <div className="register-field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="Введите email"
              autoComplete="email"
            />
          </div>

          <div className="register-field">
            <label htmlFor="password">Пароль</label>
            <div className="register-password-wrap">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Введите пароль"
                autoComplete="new-password"
              />
              <button
                type="button"
                className="register-eye-btn"
                onClick={() => setShowPassword((prev) => !prev)}
              >
                {showPassword ? "Скрыть" : "Показать"}
              </button>
            </div>
          </div>

          <button type="submit" className="register-submit" disabled={loading}>
            {loading ? "Создание..." : "Продолжить"}
          </button>

          {message && <div className="register-alert success">{message}</div>}
          {error && <div className="register-alert error">{error}</div>}
        </form>

        <div className="register-links">
          <Link to="/login">Уже есть аккаунт?</Link>
          <Link to="/">Назад</Link>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;