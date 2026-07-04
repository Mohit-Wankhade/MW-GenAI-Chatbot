import { X } from "lucide-react";
import { useEffect } from "react";

import GithubForm from "./GithubForm";

export default function GithubModal({ open, onClose, onSuccess }) {
  useEffect(() => {
    function handleEscape(event) {
      if (event.key === "Escape") {
        onClose?.();
      }
    }

    if (open) {
      document.addEventListener("keydown", handleEscape);
    }

    return () => {
      document.removeEventListener("keydown", handleEscape);
    };
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
      onMouseDown={onClose}
    >
      <div
        className="w-full max-w-lg rounded-2xl border border-[#343541] bg-[#202123] shadow-2xl"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#343541] p-5">
          <div>
            <h2 className="text-xl font-semibold text-white">
              Index GitHub Repository
            </h2>
            <p className="mt-1 text-sm text-gray-400">
              Add a public repository to your code knowledge base.
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 transition hover:bg-[#343541]"
            aria-label="Close GitHub modal"
          >
            <X size={18} className="text-gray-300" />
          </button>
        </div>

        <div className="p-6">
          <GithubForm onSuccess={onSuccess || onClose} />
        </div>
      </div>
    </div>
  );
}