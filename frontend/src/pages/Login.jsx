import { useState } from "react";
import { useNavigate } from "react-router-dom";

import AuthLayout from "../components/layout/AuthLayout";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Login() {

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const navigate = useNavigate();
    const { login } = useAuth();

    async function handleLogin() {
        setLoading(true);
        setError("");

        try {
            const formData = new URLSearchParams();
            formData.append("username", username);
            formData.append("password", password);

            const response = await api.post(
                "/auth/login",
                formData,
                {
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                }
            );

            login(response.data.access_token, username);
            navigate("/chat");

        } catch (err) {

            // ✅ SAFE ERROR HANDLING (FIX)
            let message = "Invalid username or password";

            if (err?.response?.data?.detail) {
                message = err.response.data.detail;
            } 
            else if (err?.message) {
                message = err.message;
            }
            
            setError(message);
            console.log(err.response);

        } finally {
            setLoading(false);
        }
    }

    return (
        <AuthLayout>
           {/* Header */}

<div className="flex items-center justify-center gap-4 mb-8">
    {/* Logo */}
    <div className="w-16 h-16 rounded-2xl bg-[#C8A97E] flex items-center justify-center shadow-lg flex-shrink-0">
        <div className="flex flex-col items-center leading-none">
            <span className="text-2xl font-black text-black">M</span>
            <span className="text-2xl font-black text-black -mt-3">W</span>
        </div>
    </div>

    {/* Title */}
    <div>
        <h1 className="text-4xl font-bold text-white">
            Welcome Back
        </h1>
        <p className="text-gray-400 mt-1">
            Sign in to your AI Assistant
        </p>
    </div>
</div>

            <input
                className="w-full p-3 rounded-lg bg-[#40414f] mb-4 outline-none text-white"
                placeholder="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
            />

            <input
                className="w-full p-3 rounded-lg bg-[#40414f] mb-4 outline-none text-white"
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
            />

            {/* ✅ ERROR DISPLAY (FIXED VISIBILITY) */}
            {error && (
                <div className="text-red-400 mb-4 text-center font-medium bg-red-500/10 p-2 rounded-lg">
                    {error}
                </div>
            )}

            <button
                onClick={handleLogin}
                disabled={loading}
                className="w-full bg-[#C8A97E] hover:bg-[#B7946A] text-[#171717] rounded-lg py-3 font-semibold"
            >
                {loading ? "Logging in..." : "Login"}
            </button>

            <button
                onClick={() => navigate("/register")}
                className="w-full mt-3 border border-[#C8A97E] text-[#C8A97E] hover:bg-[#C8A97E] hover:text-[#171717] rounded-lg py-3 font-semibold transition"
            >
                Create New Account
            </button>

        </AuthLayout>
    );
}