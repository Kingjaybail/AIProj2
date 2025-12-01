import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.scss";

export default function Signup() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleSignup = async (e) => {
        e.preventDefault();
        setError("");

        try {
            const res = await fetch(import.meta.env.VITE_BACKEND_URL + "/auth/signup", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password })
            });

            if (!res.ok) {
                const data = await res.json();
                setError(data.detail || "Signup failed");
                return;
            }

            // account created → redirect to login
            navigate("/");
        } catch (err) {
            setError("Server unreachable.");
        }
    };

    return (
        <div className="auth-wrapper">
            <div className="auth-card">
                <h1 className="auth-title">Create Account</h1>

                {error && <p className="auth-error">{error}</p>}

                <form onSubmit={handleSignup} className="auth-form">
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
                        Sign Up
                    </button>
                </form>

                <p className="auth-link">
                    Already have an account? <Link to="/">Log in</Link>
                </p>
            </div>
        </div>
    );
}
