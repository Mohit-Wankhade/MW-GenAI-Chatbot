import { X } from "lucide-react";
import { useEffect } from "react";

import UploadDropzone from "./UploadDropzone";

export default function UploadModal({ open, onClose, onSuccess }) {
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
        className="w-full max-w-xl rounded-2xl border border-[#3b3d42] bg-[#202123] shadow-2xl"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-center justify-between border-b border-[#3b3d42] p-5">
          <div>
            <h2 className="text-xl font-semibold text-white">Upload PDF</h2>
            <p className="mt-1 text-sm text-gray-400">
              Index a document into your RAG knowledge base.
            </p>
          </div>

          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-2 transition hover:bg-[#343541]"
            aria-label="Close upload modal"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="p-6">
          <UploadDropzone onSuccess={onSuccess || onClose} />
        </div>
      </div>
    </div>
  );
}