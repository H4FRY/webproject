import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./Chat.css";

function Chat() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadMe() {
      try {
        const response = await fetch("http://localhost:8000/me", {
          method: "GET",
          credentials: "include",
        });

        const data = await response.json();

        if (!response.ok) {
          setError(data.detail || "Не удалось получить данные пользователя");
          if (response.status === 401) {
            navigate("/login");
          }
          return;
        }

        setUser(data);
      } catch (err) {
        setError("Не удалось подключиться к серверу");
      } finally {
        setLoading(false);
      }
    }

    loadMe();
  }, [navigate]);

  async function handleLogout() {
    try {
      await fetch("http://localhost:8000/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Ошибка выхода");
    } finally {
      navigate("/login");
    }
  }

  return (
    <div
      style={{
        background: "#000",
        color: "#fff",
        minHeight: "100vh",
        padding: "24px",
      }}
    >
      <h1>Это мой гриб и я его ем</h1>

      {loading && <p>Загрузка...</p>}

      {error && <p>{error}</p>}

      {user && (
        <div>
          <p>ID: {user.id}</p>
          <p>Логин: {user.login}</p>
          <p>Email: {user.email}</p>
        </div>
      )}

      <button onClick={handleLogout}>Выйти</button>
    </div>
  );
}

export default Chat;