import api from "./api";

function normalizeGithubUrl(repoUrl) {
  return String(repoUrl || "").trim();
}

function validateGithubUrl(repoUrl) {
  const cleanUrl = normalizeGithubUrl(repoUrl);

  if (!cleanUrl) {
    throw new Error("GitHub repository URL is required.");
  }

  let parsedUrl;

  try {
    parsedUrl = new URL(cleanUrl);
  } catch {
    throw new Error("Please enter a valid GitHub repository URL.");
  }

  if (parsedUrl.protocol !== "https:") {
    throw new Error("Only HTTPS GitHub URLs are supported.");
  }

  if (parsedUrl.hostname !== "github.com") {
    throw new Error("Only github.com repository URLs are supported.");
  }

  const pathParts = parsedUrl.pathname.split("/").filter(Boolean);

  if (pathParts.length < 2) {
    throw new Error("Expected format: https://github.com/owner/repo");
  }

  return cleanUrl;
}

export async function indexGithub(repoUrl) {
  const cleanUrl = validateGithubUrl(repoUrl);

  const response = await api.post(
    "/github/index",
    {
      repo_url: cleanUrl,
    },
    {
      timeout: 15 * 60 * 1000,
    }
  );

  return response.data;
}