import { Check, Copy } from "lucide-react";
import { useState } from "react";
import toast from "react-hot-toast";

import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

async function copyToClipboard(value) {
  if (navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }

  const textarea = document.createElement("textarea");
  textarea.value = value;
  textarea.setAttribute("readonly", "");
  textarea.style.position = "absolute";
  textarea.style.left = "-9999px";

  document.body.appendChild(textarea);
  textarea.select();
  document.execCommand("copy");
  document.body.removeChild(textarea);
}

export default function CodeBlock({ language = "text", value = "" }) {
  const [copied, setCopied] = useState(false);

  async function copyCode() {
    try {
      await copyToClipboard(value);

      setCopied(true);
      toast.success("Code copied.");

      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch {
      toast.error("Could not copy code.");
    }
  }

  return (
    <div className="relative my-5 overflow-hidden rounded-xl border border-white/10 bg-[#1e1f22]">
      <div className="flex items-center justify-between border-b border-white/10 bg-[#2c2f38] px-4 py-2">
        <span className="text-xs font-semibold uppercase tracking-wide text-gray-300">
          {language}
        </span>

        <button
          type="button"
          onClick={copyCode}
          className="flex items-center gap-2 rounded-lg bg-[#3a3d46] px-2.5 py-1.5 text-xs text-gray-100 transition hover:bg-[#4b4d52]"
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>

      <SyntaxHighlighter
        language={language}
        style={oneDark}
        customStyle={{
          margin: 0,
          borderRadius: 0,
          fontSize: "14px",
          background: "#1e1f22",
          padding: "18px",
        }}
        wrapLongLines
      >
        {value}
      </SyntaxHighlighter>
    </div>
  );
}