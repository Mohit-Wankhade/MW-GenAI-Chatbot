import { Loader2, Upload } from "lucide-react";
import { useRef, useState } from "react";
import toast from "react-hot-toast";

import { uploadPdf } from "../../services/uploadService";
import SuccessCard from "../common/SuccessCard";

const MAX_PDF_SIZE_MB = 25;
const MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024;

function getErrorMessage(error, fallback = "Upload failed.") {
  const detail = error?.response?.data?.detail;

  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  if (error?.message) {
    return error.message;
  }

  return fallback;
}

function validateFile(file) {
  if (!file) {
    return "Please select a PDF file.";
  }

  const fileName = file.name || "";

  if (!fileName.toLowerCase().endsWith(".pdf")) {
    return "Please select a PDF file.";
  }

  if (file.size > MAX_PDF_SIZE_BYTES) {
    return `PDF is too large. Maximum allowed size is ${MAX_PDF_SIZE_MB} MB.`;
  }

  return "";
}

export default function UploadDropzone({ onSuccess }) {
  const fileInputRef = useRef(null);

  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);

  async function handleFile(file) {
    const validationError = validateFile(file);

    if (validationError) {
      toast.error(validationError);
      setResult({
        error: true,
        message: validationError,
      });
      return;
    }

    try {
      setProgress(0);
      setLoading(true);
      setResult(null);

      const data = await uploadPdf(file, setProgress);

      setProgress(100);
      setResult(data);
      toast.success("PDF indexed successfully.");
    } catch (error) {
      console.error(error);

      const message = getErrorMessage(error);

      setResult({
        error: true,
        message,
      });

      toast.error(message);
    } finally {
      setLoading(false);

      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    }
  }

  function openFilePicker() {
    if (!loading) {
      fileInputRef.current?.click();
    }
  }

  return (
    <div
      role="button"
      tabIndex={0}
      onClick={openFilePicker}
      onKeyDown={(event) => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openFilePicker();
        }
      }}
      onDragOver={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragEnter={(event) => {
        event.preventDefault();
        setDragging(true);
      }}
      onDragLeave={(event) => {
        event.preventDefault();
        setDragging(false);
      }}
      onDrop={(event) => {
        event.preventDefault();
        setDragging(false);

        const file = event.dataTransfer.files?.[0];
        handleFile(file);
      }}
      className={`rounded-2xl border-2 border-dashed p-10 text-center transition-all duration-200 ${
        dragging
          ? "scale-[1.01] border-[#C6A969] bg-[#C6A969]/10"
          : "border-[#4A4A4A] hover:border-[#C6A969]"
      } ${loading ? "cursor-not-allowed opacity-80" : "cursor-pointer"}`}
    >
      <Upload size={48} className="mx-auto mb-5 text-[#C6A969]" />

      <h3 className="text-xl font-semibold text-[#F4E7D3]">
        {dragging ? "Drop your PDF here" : "Drag & drop your PDF"}
      </h3>

      <p className="mt-2 text-[#B9AE9F]">
        or click below to browse
      </p>

      <p className="mt-2 text-xs text-[#7B746B]">
        Maximum size: {MAX_PDF_SIZE_MB} MB
      </p>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,application/pdf"
        hidden
        disabled={loading}
        onChange={(event) => handleFile(event.target.files?.[0])}
      />

      <button
        type="button"
        disabled={loading}
        onClick={(event) => {
          event.stopPropagation();
          openFilePicker();
        }}
        className="mx-auto mt-8 flex items-center gap-2 rounded-xl bg-[#C6A969] px-6 py-3 font-semibold text-[#1C1C1C] shadow-md transition-all duration-200 hover:bg-[#D4B67A] hover:shadow-lg disabled:cursor-not-allowed disabled:bg-[#555] disabled:text-gray-300"
      >
        {loading ? (
          <>
            <Loader2 size={18} className="animate-spin" />
            Uploading... {progress}%
          </>
        ) : (
          "Choose PDF"
        )}
      </button>

      {loading && (
        <div className="mt-5">
          <div className="h-2 w-full overflow-hidden rounded-full bg-gray-700">
            <div
              className="h-full bg-[#C6A969] transition-all duration-300"
              style={{
                width: `${progress}%`,
              }}
            />
          </div>

          <p className="mt-2 text-sm text-[#D8CDBE]">
            {progress}% Uploaded
          </p>
        </div>
      )}

      {result && (
        result.error ? (
          <div className="mt-6 rounded-xl border border-red-800 bg-red-900/20 p-4 text-[#E57373]">
            ❌ {result.message}
          </div>
        ) : (
          <div onClick={(event) => event.stopPropagation()}>
            <SuccessCard
              title="PDF Indexed Successfully"
              items={[
                {
                  icon: "📄",
                  label: "File",
                  value: result.file,
                },
                {
                  icon: "📚",
                  label: "Pages",
                  value: result.pages,
                },
                {
                  icon: "🧩",
                  label: "Chunks",
                  value: result.chunks,
                },
                {
                  icon: "🧠",
                  label: "Total PDF Chunks",
                  value: result.total_pdf_chunks,
                },
              ]}
              footer="Ready to answer questions from this PDF."
              onContinue={onSuccess}
            />
          </div>
        )
      )}
    </div>
  );
}