import { useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import AuthLayout from "../components/layout/AuthLayout";
import api from "../services/api";

function getErrorMessage(error, fallback = "Registration failed. Please try again.") {
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

export default function Register() {
  const [username, setUsername] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const passwordHint = useMemo(() => {
    if (!password) {
      return "";
    }

    if (password.length < 8) {
      return "Password must be at least 8 characters.";
    }

    if (password !== confirmPassword && confirmPassword) {
      return "Passwords do not match.";
    }

    return "";
  }, [password, confirmPassword]);

  function validateForm() {
    const cleanUsername = username.trim().toLowerCase();

    if (cleanUsername.length < 3) {
      return "Username must be at least 3 characters.";
    }

    if (!/^[a-zA-Z0-9._]+$/.test(cleanUsername)) {
      return "Username can only contain letters, numbers, dots, and underscores.";
    }

    if (password.length < 8) {
      return "Password must be at least 8 characters.";
    }

    if (password !== confirmPassword) {
      return "Passwords do not match.";
    }

    return "";
  }

  async function handleRegister(event) {
    event.preventDefault();

    const validationError = validateForm();

    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    setError("");

    try {
      await api.post("/auth/register", {
        username: username.trim().toLowerCase(),
        password,
        full_name: fullName.trim() || null,
      });

      toast.success("Account created. Please login.");
      navigate("/login", { replace: true });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <AuthLayout>
      <form onSubmit={handleRegister} className="w-full">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-[#C8A97E] shadow-lg">
            <div className="flex flex-col items-center leading-none">
              <span className="text-2xl font-black text-black">M</span>
              <span className="-mt-3 text-2xl font-black text-black">W</span>
            </div>
          </div>

          <h1 className="text-4xl font-bold text-white">Create Account</h1>
          <p className="mt-2 text-gray-400">Join your AI Assistant workspace</p>
        </div>

        <label className="mb-2 block text-sm font-medium text-gray-300">
          Full name
        </label>
        <input
          className="mb-4 w-full rounded-lg bg-[#40414f] p-3 text-white outline-none ring-1 ring-transparent transition placeholder:text-gray-400 focus:ring-[#C8A97E]"
          placeholder="Optional"
          value={fullName}
          autoComplete="name"
          disabled={loading}
          onChange={(event) => setFullName(event.target.value)}
        />

        <label className="mb-2 block text-sm font-medium text-gray-300">
          Username
        </label>
        <input
          className="mb-4 w-full rounded-lg bg-[#40414f] p-3 text-white outline-none ring-1 ring-transparent transition placeholder:text-gray-400 focus:ring-[#C8A97E]"
          placeholder="Choose a username"
          value={username}
          autoComplete="username"
          disabled={loading}
          onChange={(event) => setUsername(event.target.value)}
        />

        <label className="mb-2 block text-sm font-medium text-gray-300">
          Password
        </label>
        <input
          className="mb-3 w-full rounded-lg bg-[#40414f] p-3 text-white outline-none ring-1 ring-transparent transition placeholder:text-gray-400 focus:ring-[#C8A97E]"
          type="password"
          placeholder="Minimum 8 characters"
          value={password}
          autoComplete="new-password"
          disabled={loading}
          onChange={(event) => setPassword(event.target.value)}
        />

        <label className="mb-2 block text-sm font-medium text-gray-300">
          Confirm password
        </label>
        <input
          className="mb-3 w-full rounded-lg bg-[#40414f] p-3 text-white outline-none ring-1 ring-transparent transition placeholder:text-gray-400 focus:ring-[#C8A97E]"
          type="password"
          placeholder="Re-enter password"
          value={confirmPassword}
          autoComplete="new-password"
          disabled={loading}
          onChange={(event) => setConfirmPassword(event.target.value)}
        />

        {passwordHint && !error && (
          <p className="mb-4 rounded-lg bg-yellow-500/10 p-2 text-sm text-yellow-300">
            {passwordHint}
          </p>
        )}

        {error && (
          <div className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm font-medium text-red-300">
            {error}
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-lg bg-[#C8A97E] py-3 font-semibold text-[#171717] transition hover:bg-[#B7946A] disabled:cursor-not-allowed disabled:opacity-60"
        >
          {loading ? "Creating account..." : "Register"}
        </button>

        <div className="mt-5 text-center text-sm text-gray-400">
          Already have an account?{" "}
          <Link
            to="/login"
            className="font-semibold text-[#C8A97E] hover:text-[#B7946A]"
          >
            Back to login
          </Link>
        </div>
      </form>
    </AuthLayout>
  );
}