import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.scss";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setError("");

        try {
            const res = await fetch(import.meta.env.VITE_BACKEND_URL + "/auth/login", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            if (!res.ok) {
                const data = await res.json();
                setError(data.detail || "Login failed");
                return;
            }

            const data = await res.json();
            localStorage.setItem("user_id", data.user_id);

            navigate("/home");
        } catch (err) {
            setError("Server unreachable.");
        }
    };

    return (
        <div className="auth-wrapper">
            <div className="auth-card">
                <h1 className="auth-title">Login</h1>

                {error && <p className="auth-error">{error}</p>}

                <form onSubmit={handleLogin} className="auth-form">
                    <input
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />

                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />

                    <button type="submit" className="auth-btn">
                        Login
                    </button>
                </form>

                <p className="auth-link">
                    No account? <Link to="/signup">Sign up</Link>
                </p>
            </div>
        </div>
    );
}
