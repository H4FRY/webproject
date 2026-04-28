import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import MarkdownMessage from "../components/MarkdownMessage";
import "./Chat.css";

const API_URL = "http://localhost:8000";

function Chat() {
  const navigate = useNavigate();

  const messagesEndRef = useRef(null);

  const [theme, setTheme] = useState(() => {
    return localStorage.getItem("app-theme") || "dark";
  });

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [newChatTitle, setNewChatTitle] = useState("");

  const [user, setUser] = useState(null);
  const [error, setError] = useState("");
  const [loadingUser, setLoadingUser] = useState(true);

  const [chats, setChats] = useState([]);
  const [loadingChats, setLoadingChats] = useState(true);

  const [activeChatId, setActiveChatId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingMessages, setLoadingMessages] = useState(false);

  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [creatingChat, setCreatingChat] = useState(false);
  const [deletingChatId, setDeletingChatId] = useState(null);

  function scrollToBottom(behavior = "auto") {
    messagesEndRef.current?.scrollIntoView({ behavior, block: "end" });
  }

  useEffect(() => {
    scrollToBottom("auto");
  }, [messages]);

  const activeChat = useMemo(() => {
    return chats.find((chat) => chat.id === activeChatId) || null;
  }, [chats, activeChatId]);

  useEffect(() => {
    loadInitialData();
  }, []);

  async function loadInitialData() {
    setError("");
    await Promise.all([loadMe(), loadChats()]);
  }

  async function loadMe() {
    setLoadingUser(true);

    try {
      const response = await fetch(`${API_URL}/me`, {
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
      setLoadingUser(false);
    }
  }

  async function loadChats() {
    setLoadingChats(true);

    try {
      const response = await fetch(`${API_URL}/chats`, {
        method: "GET",
        credentials: "include",
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Не удалось загрузить список чатов");
        return;
      }

      setChats(data);

      if (data.length > 0) {
        const firstChatId = data[0].id;
        setActiveChatId(firstChatId);
        await loadChatMessages(firstChatId);
      } else {
        setActiveChatId(null);
        setMessages([]);
      }
    } catch (err) {
      setError("Не удалось загрузить список чатов");
    } finally {
      setLoadingChats(false);
    }
  }

  async function loadChatMessages(chatId) {
    setLoadingMessages(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/chats/${chatId}`, {
        method: "GET",
        credentials: "include",
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Не удалось загрузить сообщения");
        return;
      }

      setMessages(data.messages || []);
      setActiveChatId(chatId);
    } catch (err) {
      setError("Не удалось загрузить сообщения");
    } finally {
      setLoadingMessages(false);
    }
  }

  function handleOpenCreateModal() {
    setNewChatTitle("");
    setIsCreateModalOpen(true);
  }

  async function handleCreateChat() {
    const title = newChatTitle.trim() || "Новый чат";

    setCreatingChat(true);
    setError("");

    try {
      const response = await fetch(`${API_URL}/chats`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          title,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Не удалось создать чат");
        return;
      }

      setChats((prev) => [data, ...prev]);
      setActiveChatId(data.id);
      setMessages([]);
      setNewChatTitle("");
      setIsCreateModalOpen(false);
    } catch (err) {
      setError("Не удалось создать чат");
    } finally {
      setCreatingChat(false);
    }
  }

  async function handleSelectChat(chatId) {
    if (chatId === activeChatId) return;
    await loadChatMessages(chatId);
  }

  async function handleDeleteChat(chatId, e) {
    e.stopPropagation();

    setDeletingChatId(chatId);
    setError("");

    try {
      const response = await fetch(`${API_URL}/chats/${chatId}`, {
        method: "DELETE",
        credentials: "include",
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.detail || "Не удалось удалить чат");
        return;
      }

      const updatedChats = chats.filter((chat) => chat.id !== chatId);
      setChats(updatedChats);

      if (activeChatId === chatId) {
        if (updatedChats.length > 0) {
          const nextChatId = updatedChats[0].id;
          setActiveChatId(nextChatId);
          await loadChatMessages(nextChatId);
        } else {
          setActiveChatId(null);
          setMessages([]);
        }
      }
    } catch (err) {
      setError("Не удалось удалить чат");
    } finally {
      setDeletingChatId(null);
    }
  }

  async function handleSendMessage(e) {
    e.preventDefault();

    const value = input.trim();
    if (!value || !activeChatId || sending) return;

    setSending(true);
    setError("");

    const tempUserId = `temp-user-${Date.now()}`;
    const tempAssistantId = `temp-assistant-${Date.now() + 1}`;

    const optimisticUserMessage = {
      id: tempUserId,
      role: "user",
      content: value,
      created_at: new Date().toISOString(),
    };

    const optimisticAssistantMessage = {
      id: tempAssistantId,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, optimisticUserMessage, optimisticAssistantMessage]);
    setInput("");

    try {
      const response = await fetch(`${API_URL}/chats/${activeChatId}/messages/stream`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({
          content: value,
        }),
      });

      if (!response.ok || !response.body) {
        const data = await response.json();
        setMessages((prev) =>
          prev.filter(
            (message) =>
              message.id !== tempUserId && message.id !== tempAssistantId
          )
        );
        setError(data.detail || "Не удалось отправить сообщение");
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let accumulated = "";
      let done = false;

      while (!done) {
        const result = await reader.read();
        done = result.done;

        if (result.value) {
          const chunk = decoder.decode(result.value, { stream: true });
          accumulated += chunk;

          setMessages((prev) =>
            prev.map((message) =>
              message.id === tempAssistantId
                ? { ...message, content: accumulated }
                : message
            )
          );
        }
      }

      await loadChatMessages(activeChatId);
      await refreshChatsTitles(activeChatId, value);
    } catch (err) {
      setMessages((prev) =>
        prev.filter(
          (message) =>
            message.id !== tempUserId && message.id !== tempAssistantId
        )
      );
      setError("Не удалось отправить сообщение");
    } finally {
      setSending(false);
    }
  }

  async function refreshChatsTitles(chatId, fallbackTitle) {
    setChats((prev) =>
      prev.map((chat) =>
        chat.id === chatId && chat.title === "Новый чат"
          ? { ...chat, title: fallbackTitle.slice(0, 40) }
          : chat
      )
    );

    try {
      const response = await fetch(`${API_URL}/chats`, {
        method: "GET",
        credentials: "include",
      });

      const data = await response.json();

      if (response.ok) {
        setChats(data);
      }
    } catch {
        // ignore
    }
  }

  async function handleLogout() {
    try {
      await fetch(`${API_URL}/logout`, {
        method: "POST",
        credentials: "include",
      });
    } catch (err) {
      console.error("Ошибка выхода");
    } finally {
      navigate("/");
    }
  }

  function handleToggleTheme() {
    const nextTheme = theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
    localStorage.setItem("app-theme", nextTheme);
  }

  return (
    <div className={`chat-page ${theme}`}>
      <aside className="chat-sidebar">
        <div className="chat-sidebar-top">
          <div className="chat-brand">POAIBOT</div>

          <button
            className="chat-new-btn"
            onClick={handleOpenCreateModal}
            disabled={creatingChat}
          >
            + Новый чат
          </button>

          <div className="chat-list">
            {loadingChats ? (
              <div className="chat-list-empty">Загрузка чатов...</div>
            ) : chats.length === 0 ? (
              <div className="chat-list-empty">Чатов пока нет</div>
            ) : (
              chats.map((chat) => (
                <div
                  key={chat.id}
                  className={`chat-list-item ${
                    chat.id === activeChatId ? "active" : ""
                  }`}
                  onClick={() => handleSelectChat(chat.id)}
                >
                  <button className="chat-list-main-btn" type="button">
                    <span className="chat-list-title">{chat.title}</span>
                  </button>

                  <button
                    className="chat-list-delete-btn"
                    type="button"
                    onClick={(e) => handleDeleteChat(chat.id, e)}
                    disabled={deletingChatId === chat.id}
                    title="Удалить чат"
                  >
                    {deletingChatId === chat.id ? "..." : "×"}
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="chat-sidebar-bottom">
          <button className="chat-theme-btn" onClick={handleToggleTheme}>
            {theme === "dark" ? "Светлая тема" : "Тёмная тема"}
          </button>

          <div className="chat-account">
            {loadingUser ? (
              <div className="chat-account-meta">
                <div className="chat-account-name">Загрузка...</div>
              </div>
            ) : user ? (
              <>
                <div className="chat-account-avatar">
                  {user.login?.[0]?.toUpperCase() || "U"}
                </div>
                <div className="chat-account-meta">
                  <div className="chat-account-name">{user.login}</div>
                  <div className="chat-account-email">{user.email}</div>
                </div>
              </>
            ) : (
              <div className="chat-account-meta">
                <div className="chat-account-name">Нет данных</div>
              </div>
            )}
          </div>

          <button className="chat-logout-btn" onClick={handleLogout}>
            Выйти
          </button>
        </div>
      </aside>

      <main className="chat-main">
        <header className="chat-header">
          <div>
            <h1>{activeChat?.title || "Чат"}</h1>
            <p>Задайте вопрос преподавателю магистратуры</p>
          </div>
        </header>

        <section className="chat-messages">
          {error && <div className="chat-error">{error}</div>}

          {!activeChatId && !loadingChats && !error && (
            <div className="chat-empty-state">
              <h2>Создайте первый чат</h2>
              <p>Нажмите «Новый чат» и начните диалог.</p>
            </div>
          )}

          {loadingMessages && activeChatId && (
            <div className="chat-list-empty">Загрузка сообщений...</div>
          )}

          {!loadingMessages &&
            messages.map((message) => (
              <div
                key={message.id}
                className={`chat-message ${message.role}`}
              >
                <div className="chat-message-role">
                  {message.role === "assistant" ? "Ассистент" : "Вы"}
                </div>
                <div className="chat-message-content">
                  <MarkdownMessage content={message.content} theme={theme} />
                </div>
              </div>
            ))}
          <div ref={messagesEndRef} />
        </section>

        <form className="chat-input-wrap" onSubmit={handleSendMessage}>
          <textarea
            className="chat-input"
            placeholder={
              activeChatId
                ? "Спросите про магистратуру..."
                : "Сначала создайте чат..."
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            rows={1}
            disabled={!activeChatId || sending}
          />

          <button
            className="chat-send-btn"
            type="submit"
            disabled={!activeChatId || sending}
          >
            {sending ? "Отправка..." : "Отправить"}
          </button>
        </form>
      </main>

      {isCreateModalOpen && (
        <div
          className="chat-modal-overlay"
          onClick={() => {
            if (!creatingChat) {
              setIsCreateModalOpen(false);
              setNewChatTitle("");
            }
          }}
        >
          <div
            className="chat-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <h2>Создать новый чат</h2>
            <p>Введите тему или название чата</p>

            <input
              className="chat-modal-input"
              type="text"
              placeholder="Например: Вопросы по поступлению"
              value={newChatTitle}
              onChange={(e) => setNewChatTitle(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !creatingChat) {
                  handleCreateChat();
                }
              }}
              maxLength={100}
              autoFocus
            />

            <div className="chat-modal-actions">
              <button
                type="button"
                className="chat-modal-cancel"
                onClick={() => {
                  setIsCreateModalOpen(false);
                  setNewChatTitle("");
                }}
                disabled={creatingChat}
              >
                Отмена
              </button>

              <button
                type="button"
                className="chat-modal-create"
                onClick={handleCreateChat}
                disabled={creatingChat}
              >
                {creatingChat ? "Создание..." : "Создать"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chat;