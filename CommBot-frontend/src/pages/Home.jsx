import { useState, useEffect, useRef } from "react";
import "./Home.scss";
import Sidebar from "./Sidebar";

export default function Home() {
    const [prompt, setPrompt] = useState("");
    const [files, setFiles] = useState([]);
    const [messages, setMessages] = useState([]);
    const [isTyping, setIsTyping] = useState(false);
    const [showSourceMenu, setShowSourceMenu] = useState(false);
    const [showUrlInput, setShowUrlInput] = useState(false);
    const [urlInputValue, setUrlInputValue] = useState("");

    const [chats, setChats] = useState([]);
    const [activeChatId, setActiveChatId] = useState(null);

    // URLs are stored in a ref (persistent but doesn't trigger rerender)
    const urlsRef = useRef([]);

    const urls = [...new Set(urlsRef.current)]; // dedupe each render

    /* -----------------------------------------------------------
       LOAD CHATS ON MOUNT
    ----------------------------------------------------------- */
    useEffect(() => {
        const user_id = localStorage.getItem("user_id");
        if (!user_id) return (window.location.href = "/");

        fetch(import.meta.env.VITE_BACKEND_URL + `/chats/${user_id}`)
            .then(res => res.json())
            .then(data => {
                setChats(data);

                if (data.length > 0) {
                    const saved = Number(localStorage.getItem("active_chat_id"));
                    const selected = data.find(c => c.id === saved)?.id || data[0].id;

                    setActiveChatId(selected);

                    fetch(import.meta.env.VITE_BACKEND_URL +`/chats/get/${selected}`)
                        .then(res => res.json())
                        .then(chat => setMessages(JSON.parse(chat.messages)));
                }
            });
    }, []);

    /* -----------------------------------------------------------
       TITLE LOGIC
    ----------------------------------------------------------- */
    const createLocalTitle = (text) => {
        let title = text
            .replace(/\?.*$/, "")
            .replace(/[^\w\s]/g, "")
            .trim()
            .split(/\s+/)
            .slice(0, 7)
            .join(" ");

        return title ? title.charAt(0).toUpperCase() + title.slice(1) : "New Chat";
    };

    const updateChatTitle = async (chatId, newTitle) => {
        await fetch(import.meta.env.VITE_BACKEND_URL + "/chats/update_title", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chat_id: chatId, title: newTitle }),
        });

        setChats(prev =>
            prev.map(c => (c.id === chatId ? { ...c, title: newTitle } : c))
        );
    };

    /* -----------------------------------------------------------
       FILE HANDLING
    ----------------------------------------------------------- */
    const handleFileSelect = (e) => {
        setFiles(prev => [...prev, ...Array.from(e.target.files)]);
    };

    const removeFile = (i) => {
        setFiles(prev => prev.filter((_, idx) => idx !== i));
    };

    const removeUrl = (i) => {
        const deduped = [...new Set(urlsRef.current)];
        const toRemove = deduped[i];
        urlsRef.current = urlsRef.current.filter(u => u !== toRemove);
    };

    /* -----------------------------------------------------------
       SEND MESSAGE
    ----------------------------------------------------------- */
    const sendToBackend = async () => {
        if (!prompt.trim() || !activeChatId) return;

        // Store user message in DB
        await fetch(import.meta.env.VITE_BACKEND_URL + "/chats/append", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                chat_id: Number(activeChatId),
                role: "user",
                text: prompt
            })
        });

        setMessages(prev => [...prev, { role: "user", text: prompt }]);

        const chat = chats.find(c => c.id === activeChatId);
        if (chat && chat.title === "New Chat") {
            updateChatTitle(activeChatId, createLocalTitle(prompt));
        }

        setIsTyping(true);

        // Build FormData (deduped URLs)
        const form = new FormData();
        form.append("chat_id", activeChatId);
        form.append("prompt", prompt);

        files.forEach(f => form.append("files", f, f.name));
        urls.forEach(u => form.append("urls", u));

        const res = await fetch(import.meta.env.VITE_BACKEND_URL +"/ask", {
            method: "POST",
            body: form,
        });

        const data = await res.json();
        setIsTyping(false);
        setPrompt("");
        // Store assistant message in DB
        await fetch(import.meta.env.VITE_BACKEND_URL + "/chats/append", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                chat_id: activeChatId,
                role: "assistant",
                text: data.answer,
                sources: data.sources || []
            })
        });

        setMessages(prev => [
            ...prev,
            { role: "assistant", text: data.answer, sources: data.sources || [] }
        ]);

        // Clear temporary resources
        setFiles([]);
        urlsRef.current = [];
        setUrlInputValue("");
    };

    /* -----------------------------------------------------------
       CHAT CONTROLS
    ----------------------------------------------------------- */
    const handleNewChat = async () => {
        const user_id = localStorage.getItem("user_id");

        const res = await fetch(import.meta.env.VITE_BACKEND_URL + "/chats/create", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id, title: "New Chat" }),
        });

        const newChat = await res.json();

        setChats(prev => [newChat, ...prev]);
        setActiveChatId(newChat.id);
        setMessages([]);
        urlsRef.current = [];
        localStorage.setItem("active_chat_id", newChat.id);
    };

    const handleSelectChat = async (id) => {
        setActiveChatId(id);
        localStorage.setItem("active_chat_id", id);

        const res = await fetch(import.meta.env.VITE_BACKEND_URL + `/chats/get/${id}`);
        const chat = await res.json();

        setMessages(JSON.parse(chat.messages));
        setFiles([]);
        urlsRef.current = [];
    };

    const handleDeleteChat = async (id) => {
        await fetch(import.meta.env.VITE_BACKEND_URL + `/chats/${id}`, { method: "DELETE" });

        setChats(prev => prev.filter(c => c.id !== id));

        if (id === activeChatId) {
            const next = chats.find(c => c.id !== id)?.id ?? null;
            setActiveChatId(next);
            localStorage.setItem("active_chat_id", next || "");

            if (next) {
                const res = await fetch(import.meta.env.VITE_BACKEND_URL + `/chats/get/${next}`);
                const chat = await res.json();
                setMessages(JSON.parse(chat.messages));
            } else {
                setMessages([]);
            }
        }
    };

    /* -----------------------------------------------------------
       LOGOUT
    ----------------------------------------------------------- */
    const handleLogout = () => {
        localStorage.removeItem("user_id");
        localStorage.removeItem("active_chat_id");
        window.location.href = "/";
    };

    /* -----------------------------------------------------------
       RENDER
    ----------------------------------------------------------- */
    return (
        <div className="app-shell">
            <Sidebar
                chats={chats}
                activeChatId={activeChatId}
                onNewChat={handleNewChat}
                onSelectChat={handleSelectChat}
                onDeleteChat={handleDeleteChat}
                onLogout={handleLogout}
            />

            <div className="gpt-page">

                {/* CHAT MESSAGES */}
                <div className="gpt-chat">
                    {messages.map((msg, i) => (
                        <div key={i} className={`gpt-msg ${msg.role}`}>
                            <div className="inner">
                                <p>{msg.text}</p>

                                {msg.sources && msg.sources.length > 0 && (
                                    <div className="sources">
                                        <ul>
                                            {msg.sources.map((s, j) => (
                                                <li key={j}>{s}</li>
                                            ))}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}

                    {isTyping && (
                        <div className="typing-msg">
                            <div className="typing-bubble">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    )}
                </div>

                {/* INPUT AREA */}
                <div className="gpt-input-wrapper">

                    {/* FILE PILLS */}
                    {files.length > 0 && (
                        <div className="file-pills above-input">
                            {files.map((file, i) => (
                                <div key={i} className="pill removable">
                                    {file.name}
                                    <button className="remove-file" onClick={() => removeFile(i)}>✕</button>
                                </div>
                            ))}
                        </div>
                    )}

                    {/* URL PILLS (deduped) */}
                    {urls.length > 0 && (
                        <div className="file-pills above-input">
                            {urls.map((url, i) => (
                                <div key={i} className="pill removable">
                                    {url}
                                    <button className="remove-file" onClick={() => removeUrl(i)}>✕</button>
                                </div>
                            ))}
                        </div>
                    )}

                    <div className="gpt-input">
                        <div
                            className="left-plus"
                            onClick={() => setShowSourceMenu(!showSourceMenu)}
                        >
                           +
                        </div>

                        {/* Source Menu */}
                        {showSourceMenu && (
                            <div className="source-menu">
                                <button
                                    className="source-item"
                                    onClick={() => {
                                        setShowSourceMenu(false);
                                        document.getElementById("hidden-file-input").click();
                                    }}
                                >
                                    Add File
                                </button>

                                <button
                                    className="source-item"
                                    onClick={() => {
                                        setShowSourceMenu(false);
                                        setShowUrlInput(true);
                                    }}
                                >
                                    Add URL
                                </button>
                            </div>
                        )}

                        {/* Hidden file input */}
                        <input
                            id="hidden-file-input"
                            type="file"
                            style={{ display: "none" }}
                            accept=".pdf,.txt,.doc,.docx,.png,.jpg,.jpeg"
                            multiple
                            onChange={handleFileSelect}
                        />

                        <textarea
                            placeholder="Send a message..."
                            value={prompt}
                            onChange={(e) => setPrompt(e.target.value)}
                        />

                        <button className="send-btn" onClick={sendToBackend}>
                            ➤
                        </button>
                    </div>
                </div>
            </div>

            {/* URL Modal */}
            {showUrlInput && (
                <div className="url-modal">
                    <div className="url-box">
                        <h3>Add URL</h3>
                        <input
                            type="text"
                            placeholder="https://example.com"
                            value={urlInputValue}
                            onChange={(e) => setUrlInputValue(e.target.value)}
                        />

                        <div className="url-actions">
                            <button onClick={() => setShowUrlInput(false)}>Cancel</button>

                            <button
                                onClick={() => {
                                    const clean = urlInputValue.trim();
                                    if (clean) {
                                        const updated = new Set(urlsRef.current);
                                        updated.add(clean);
                                        urlsRef.current = [...updated];
                                    }
                                    setUrlInputValue("");
                                    setShowUrlInput(false);
                                }}
                            >
                                Add
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
