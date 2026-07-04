import api from "./api";

const MAX_PDF_SIZE_MB = 25;
const MAX_PDF_SIZE_BYTES = MAX_PDF_SIZE_MB * 1024 * 1024;

function validatePdfFile(file) {
  if (!file) {
    throw new Error("Please select a PDF file.");
  }

  const fileName = file.name || "";

  if (!fileName.toLowerCase().endsWith(".pdf")) {
    throw new Error("Only PDF files are allowed.");
  }

  if (file.size > MAX_PDF_SIZE_BYTES) {
    throw new Error(`PDF is too large. Maximum allowed size is ${MAX_PDF_SIZE_MB} MB.`);
  }
}

export async function uploadPdf(file, onProgress = () => {}) {
  validatePdfFile(file);

  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/upload/pdf", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    timeout: 10 * 60 * 1000,
    onUploadProgress: (progressEvent) => {
      if (!progressEvent.total) {
        return;
      }

      const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
      onProgress(Math.min(percent, 100));
    },
  });

  return response.data;
}