import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./LoginPage.css";

function LoginPage() {
  const navigate = useNavigate();

  const [theme] = useState(() => {
    return localStorage.getItem("app-theme") || "dark";
  });

  const [form, setForm] = useState({
    email: "",
    password: "",
  });

  const [loading, setLoading] = useState(false);
  const [githubLoading, setGithubLoading] = useState(false);
  const [error, setError] = useState("");
  const [showPassword, setShowPassword] = useState(false);

  const [googleLoading, setGoogleLoading] = useState(false);

  function handleGoogleLogin() {
    setGoogleLoading(true);
    window.location.href = "http://localhost:8000/auth/google/login";
  }

  function handleChange(e) {
    setForm((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(form),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Ошибка входа");
        return;
      }

      if (data.requires_2fa) {
        navigate("/login/verify-2fa", {
          state: { email: data.email },
        });
        return;
      }

      navigate("/chat");
    } catch (err) {
      setError("Не удалось подключиться к серверу");
    } finally {
      setLoading(false);
    }
  }

  function handleGithubLogin() {
    setGithubLoading(true);
    window.location.href = "http://localhost:8000/auth/github/login";
  }

  return (
    <div className={`login-page ${theme}`}>
      <div className="login-brand">POAIBOT</div>

      <div className="login-card">
        <h1>Войти</h1>
        <p className="login-subtitle">
          Войдите в аккаунт или продолжите через GitHub
        </p>

        <button
          type="button"
          className="login-oauth-btn"
          onClick={handleGithubLogin}
          disabled={githubLoading}
        >
          <span className="login-github-icon">◎</span>
          {githubLoading ? "Переход..." : "Продолжить с GitHub"}
        </button>

        <button
          type="button"
          className="login-oauth-btn"
          onClick={handleGoogleLogin}
          disabled={googleLoading}
        >
          {googleLoading ? "Переход..." : "Продолжить с Google"}
        </button>

        <div className="login-divider">
          <span></span>
          <p>или</p>
          <span></span>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="login-field">
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

          <div className="login-field">
            <label htmlFor="password">Пароль</label>
            <div className="login-password-wrap">
              <input
                id="password"
                type={showPassword ? "text" : "password"}
                name="password"
                value={form.password}
                onChange={handleChange}
                placeholder="Введите пароль"
                autoComplete="current-password"
              />
              <button
                type="button"
                className="login-eye-btn"
                onClick={() => setShowPassword((prev) => !prev)}
              >
                {showPassword ? "Скрыть" : "Показать"}
              </button>
            </div>
          </div>

          <button type="submit" className="login-submit" disabled={loading}>
            {loading ? "Вход..." : "Продолжить"}
          </button>

          {error && <div className="login-alert error">{error}</div>}
        </form>

        <div className="login-links">
          <Link to="/register">Нет аккаунта?</Link>
          <Link to="/">Назад</Link>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;