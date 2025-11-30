// Sidebar.jsx
import "./Home.scss";

export default function Sidebar({
  chats,
  activeChatId,
  onNewChat,
  onSelectChat,
  onDeleteChat,
  onLogout,
}) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <button className="sidebar-new-chat" onClick={onNewChat}>
          + New chat
        </button>
      </div>

      <div className="sidebar-chats">
        {chats.length === 0 ? (
          <div className="sidebar-empty">No chats yet</div>
        ) : (
          chats.map((chat) => (
            <button
              key={chat.id}
              className={`sidebar-chat-item ${
                chat.id === activeChatId ? "active" : ""
              }`}
              onClick={() => onSelectChat(chat.id)}
            >
              <span className="sidebar-chat-title">{chat.title}</span>
              <span
                className="sidebar-chat-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteChat(chat.id);
                }}
              >
                ✕
              </span>
            </button>
          ))
        )}
      </div>

      <div className="sidebar-footer">
        <button className="sidebar-user" onClick={onLogout}>
          <div className="sidebar-avatar">U</div>
          <span className="sidebar-user-label">Logout</span>
        </button>
      </div>
    </aside>
  );
}
