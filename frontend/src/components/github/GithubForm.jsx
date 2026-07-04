import { Loader2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { FaGithub } from "react-icons/fa";
import toast from "react-hot-toast";

import { indexGithub } from "../../services/githubService";
import SuccessCard from "../common/SuccessCard";

function getErrorMessage(error, fallback = "Failed to index repository.") {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (error?.message) {
    return error.message;
  }

  return fallback;
}

function validateGithubUrl(url) {
  const cleanUrl = String(url || "").trim();

  if (!cleanUrl) {
    return "GitHub repository URL is required.";
  }

  try {
    const parsed = new URL(cleanUrl);

    if (parsed.protocol !== "https:") {
      return "Only HTTPS GitHub URLs are supported.";
    }

    if (parsed.hostname !== "github.com") {
      return "Only github.com repository URLs are supported.";
    }

    const pathParts = parsed.pathname.split("/").filter(Boolean);

    if (pathParts.length < 2) {
      return "Expected format: https://github.com/owner/repo";
    }

    return "";
  } catch {
    return "Please enter a valid GitHub repository URL.";
  }
}

export default function GithubForm({ onSuccess }) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [seconds, setSeconds] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  const validationMessage = useMemo(() => {
    if (!url.trim()) {
      return "";
    }

    return validateGithubUrl(url);
  }, [url]);

  useEffect(() => {
    if (!loading) {
      setSeconds(0);
      return undefined;
    }

    const interval = setInterval(() => {
      setSeconds((previousValue) => previousValue + 1);
    }, 1000);

    return () => clearInterval(interval);
  }, [loading]);

  async function handleSubmit(event) {
    event.preventDefault();

    const cleanUrl = url.trim();
    const validationError = validateGithubUrl(cleanUrl);

    if (validationError) {
      setError(validationError);
      toast.error(validationError);
      return;
    }

    try {
      setLoading(true);
      setResult(null);
      setError("");

      const data = await indexGithub(cleanUrl);

      setResult(data);
      toast.success("Repository indexed successfully.");
    } catch (err) {
      console.error(err);

      const message = getErrorMessage(err);

      setError(message);
      setResult({
        error: true,
        message,
      });

      toast.error(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div>
        <label className="mb-2 block text-sm text-[#CBB58A]">
          GitHub Repository URL
        </label>

        <input
          value={url}
          disabled={loading}
          onChange={(event) => {
            setUrl(event.target.value);
            setError("");
            setResult(null);
          }}
          placeholder="https://github.com/user/repository"
          className="w-full rounded-xl border border-[#3E3A34] bg-[#242321] px-4 py-3 text-[#F4E7D3] outline-none transition placeholder:text-[#7B746B] focus:border-[#C6A969] disabled:cursor-not-allowed disabled:opacity-70"
        />

        {validationMessage && !error && (
          <p className="mt-2 text-sm text-yellow-300">
            {validationMessage}
          </p>
        )}
      </div>

      <button
        type="submit"
        disabled={loading || Boolean(validationMessage)}
        className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#C6A969] py-3 font-semibold text-[#1D1D1B] transition-all duration-200 hover:bg-[#D4B67A] disabled:cursor-not-allowed disabled:opacity-70"
      >
        {loading ? (
          <>
            <Loader2 className="animate-spin" size={18} />
            Indexing... ({seconds}s)
          </>
        ) : (
          <>
            <FaGithub size={18} />
            Index Repository
          </>
        )}
      </button>

      {loading && (
        <div className="rounded-xl border border-[#3E3A34] bg-[#242321] p-4">
          <div className="h-2 w-full overflow-hidden rounded-full bg-[#34322F]">
            <div
              className="h-full animate-pulse bg-[#C6A969]"
              style={{
                width: "100%",
              }}
            />
          </div>

          <p className="mt-3 text-center text-sm text-[#B9AE9F]">
            Cloning repository → Reading files → Creating embeddings → Building index...
          </p>
        </div>
      )}

      {error && !result && (
        <div className="rounded-xl border border-red-800 bg-red-900/20 p-4 text-red-300">
          ❌ {error}
        </div>
      )}

      {result && (
        result.error ? (
          <div className="mt-4 rounded-xl border border-red-800 bg-red-900/20 p-4 text-red-300">
            ❌ {result.message}
          </div>
        ) : (
          <SuccessCard
            title="Repository Indexed Successfully"
            items={[
              {
                icon: "💻",
                label: "Repository",
                value: result.repo,
              },
              {
                icon: "📄",
                label: "Files Indexed",
                value: result.files,
              },
              {
                icon: "🧩",
                label: "Chunks",
                value: result.chunks,
              },
              {
                icon: "🧠",
                label: "Total GitHub Chunks",
                value: result.total_github_chunks,
              },
            ]}
            footer="Repository is ready for AI-powered code questions."
            onContinue={onSuccess}
          />
        )
      )}
    </form>
  );
}