import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./WelcomePage.css";

const phrases = [
  {
    title: "Создай заявку",
    subtitle: "на согласование проекта",
  },

  {
    title: "Подготовь ответ",
    subtitle: "для клиента за пару секунд",
  },
  {
    title: "Собери текст",
    subtitle: "для отчёта или письма",
  },
  {
    title: "Сформируй запрос",
    subtitle: "без лишних действий",
  },
  {
    title: "Начни работу",
    subtitle: "в удобном интерфейсе",
  },
];

function WelcomePage() {
  const navigate = useNavigate();

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("app-theme") || "dark";
  });

  const [index, setIndex] = useState(0);
  const [animate, setAnimate] = useState(true);

  useEffect(() => {
    localStorage.setItem("app-theme", theme);
  }, [theme]);

  useEffect(() => {
    const interval = setInterval(() => {
      setAnimate(false);

      setTimeout(() => {
        setIndex((prev) => (prev + 1) % phrases.length);
        setAnimate(true);
      }, 180);
    }, 2800);

    return () => clearInterval(interval);
  }, []);

  const currentPhrase = phrases[index];

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return (
    <div className={`welcome-page ${theme}`}>
      <button className="theme-toggle-btn" onClick={toggleTheme}>
        {theme === "dark" ? "◐" : "◑"}
      </button>

      <div className="welcome-left">
        <div className="welcome-brand">POAIBOT</div>

        <div className={`welcome-message ${animate ? "wave-in" : "wave-out"}`}>
          <h1>{currentPhrase.title}</h1>
          <p>{currentPhrase.subtitle}</p>
        </div>
      </div>

      <div className="welcome-right">
        <div className="welcome-panel">
          <h2>Добро пожаловать</h2>
          <p className="welcome-panel-text">
            Выберите действие, чтобы перейти к авторизации или созданию нового аккаунта.
          </p>

          <div className="welcome-buttons">
            <button
              className="welcome-btn welcome-btn-secondary"
              onClick={() => navigate("/login")}
            >
              Войти
            </button>

            <button
              className="welcome-btn welcome-btn-primary"
              onClick={() => navigate("/register")}
            >
              Зарегистрироваться
            </button>
          </div>

          <button className="welcome-link-btn">
            Сначала посмотреть возможности
          </button>
        </div>

        <div className="welcome-footer">
        </div>
      </div>
    </div>
  );
}

export default WelcomePage;