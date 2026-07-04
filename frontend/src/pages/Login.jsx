import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import AuthLayout from "../components/layout/AuthLayout";
import { useAuth } from "../context/AuthContext";
import api from "../services/api";

function getErrorMessage(error, fallback = "Invalid username or password.") {
  const detail = error?.response?.data?.detail;

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg).join(", ");
  }

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (error?.message) {
    return error.message;
  }

  return fallback;
}

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();
  const location = useLocation();

  const { login, isAuthenticated } = useAuth();

  const redirectTo = location.state?.from?.pathname || "/chat";

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/chat", { replace: true });
    }
  }, [isAuthenticated, navigate]);

  async function handleLogin(event) {
    event.preventDefault();

    const cleanUsername = username.trim().toLowerCase();

    if (!cleanUsername || !password) {
      setError("Please enter both username and password.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new URLSearchParams();
      formData.append("username", cleanUsername);
      formData.append("password", password);

      const response = await api.post("/auth/login", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      login(response.data.access_token, response.data.username || cleanUsername);

      toast.success("Logged in successfully.");
      navigate(redirectTo, { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout>
      <form onSubmit={handleLogin} className="w-full">
        <div className="mb-8 flex items-center justify-center gap-4">
          <div className="flex h-16 w-16 flex-shrink-0 items-center justify-center rounded-2xl bg-[#C8A97E] shadow-lg">
            <div className="flex flex-col items-center leading-none">
              <span className="text-2xl font-black text-black">M</span>
              <span className="-mt-3 text-2xl font-black text-black">W</span>
            </div>
          </div>

          <div>
            <h1 className="text-4xl font-bold text-white">Welcome Back</h1>
            <p className="mt-1 text-gray-400">Sign in to your AI Assistant</p>
          </div>
        </div>

        <label className="mb-2 block text-sm font-medium text-gray-300">
          Username
        </label>
        <input
          className="mb-4 w-full rounded-lg bg-[#40414f] p-3 text-white outline-none ring-1 ring-transparent transition placeholder:text-gray-400 focus:ring-[#C8A97E]"
          placeholder="Enter your username"
          value={username}
          autoComplete="username"
          disabled={loading}
          onChange={(event) => setUsername(event.target.value)}
        />

        <label className="mb-2 block text-sm font-medium text-gray-300">
          Password
        </label>
        <input
          className="mb-4 w-full rounded-lg bg-[#40414f] p-3 text-white outline-none ring-1 ring-transparent transition placeholder:text-gray-400 focus:ring-[#C8A97E]"
          type="password"
          placeholder="Enter your password"
          value={password}
          autoComplete="current-password"
          disabled={loading}
          onChange={(event) => setPassword(event.target.value)}
        />

        {error && (
          <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-center text-sm font-medium text-red-300">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-[#C8A97E] py-3 font-semibold text-[#171717] transition hover:bg-[#B7946A] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Logging in..." : "Login"}
        </button>

        <div className="mt-5 text-center text-sm text-gray-400">
          New here?{" "}
          <Link
            to="/register"
            className="font-semibold text-[#C8A97E] hover:text-[#B7946A]"
          >
            Create an account
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}