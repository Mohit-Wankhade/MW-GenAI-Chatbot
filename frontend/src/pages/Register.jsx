import { useState } from "react";
import { useNavigate } from "react-router-dom";

import AuthLayout from "../components/layout/AuthLayout";
import api from "../services/api";

export default function Register() {

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const navigate = useNavigate();

    async function handleRegister() {

        setLoading(true);
        setError("");

        if (password !== confirmPassword) {
            setError("Passwords do not match");
            setLoading(false);
            return;
        }

        try {

            await api.post("/auth/register", {
                username,
                password
            });

            navigate("/");

        } catch (err) {
            setError("User already exists or invalid input");
        } finally {
            setLoading(false);
        }
    }

    return (

        <AuthLayout>

            <h1 className="text-4xl font-bold text-center mb-2">
                Create Account
            </h1>

            <p className="text-gray-400 text-center mb-8">
                Join your AI Assistant workspace
            </p>

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

            <input
                className="w-full p-3 rounded-lg bg-[#40414f] mb-4 outline-none text-white"
                type="password"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
            />

            {error && (
                <p className="text-red-500 mb-4">
                    {error}
                </p>
            )}

            <button
                onClick={handleRegister}
                disabled={loading}
                className="w-full bg-[#C8A97E] hover:bg-[#B7946A] text-[#171717] rounded-lg py-3 font-semibold"
            >
                {loading ? "Creating account..." : "Register"}
            </button>

            <button
                onClick={() => navigate("/")}
                className="w-full mt-3 border border-gray-500 text-gray-300 hover:bg-gray-700 rounded-lg py-3 font-semibold transition"
            >
                Back to Login
            </button>

        </AuthLayout>
    );
}