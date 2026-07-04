import { FileText } from "lucide-react";
import { FaGithub } from "react-icons/fa";

function dedupeSources(sources) {
  const seen = new Set();
  const output = [];

  for (const source of sources || []) {
    const key = [
      source.type || "",
      source.name || "",
      source.repo || "",
      source.file || "",
      source.page || "",
    ].join("|");

    if (seen.has(key)) {
      continue;
    }

    seen.add(key);
    output.push(source);
  }

  return output;
}

function getSourceTitle(source) {
  if (!source) {
    return "Unknown source";
  }

  if (source.type === "pdf") {
    return source.name || "PDF Document";
  }

  if (source.type === "github") {
    return source.repo || source.name || "GitHub Repository";
  }

  return source.name || source.file || source.repo || "Unknown source";
}

function getSourceSubtitle(source) {
  if (!source) {
    return "Source";
  }

  if (source.type === "pdf") {
    return source.page ? `PDF • Page ${source.page}` : "PDF Document";
  }

  if (source.type === "github") {
    if (source.file) {
      return `GitHub • ${source.file}`;
    }

    return "GitHub Repository";
  }

  return "Source";
}

function getSourceDetail(source) {
  if (!source) {
    return "";
  }

  if (source.type === "github" && source.name) {
    return source.name;
  }

  return "";
}

function SourceIcon({ type }) {
  if (type === "pdf") {
    return <FileText size={18} className="text-[#b44b3c]" />;
  }

  if (type === "github") {
    return <FaGithub size={18} className="text-[#171717]" />;
  }

  return <FileText size={18} className="text-[#8b7355]" />;
}

export default function SourceCards({ sources }) {
  const uniqueSources = dedupeSources(sources);

  if (uniqueSources.length === 0) {
    return null;
  }

  return (
    <div className="mt-4 w-full max-w-3xl">
      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.18em] text-[#6f5a3f]">
        Sources
      </p>

      <div className="grid gap-3 sm:grid-cols-2">
        {uniqueSources.map((source, index) => {
          const detail = getSourceDetail(source);

          return (
            <div
              key={`${source.type}-${source.name}-${source.page}-${index}`}
              className="rounded-2xl border border-[#d5c1a0] bg-[#fcfaf7] p-4 text-[#3b342d] shadow-sm transition-all hover:border-[#b89363] hover:shadow-md"
            >
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-xl bg-[#f2e7d5]">
                  <SourceIcon type={source.type} />
                </div>

                <div className="min-w-0 flex-1">
                  <div
                    className="truncate font-medium text-[#3b342d]"
                    title={getSourceTitle(source)}
                  >
                    {getSourceTitle(source)}
                  </div>

                  <div className="mt-1 truncate text-sm text-[#7d6a51]">
                    {getSourceSubtitle(source)}
                  </div>

                  {detail && (
                    <div
                      className="mt-1 truncate text-xs text-[#9a8a73]"
                      title={detail}
                    >
                      {detail}
                    </div>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}