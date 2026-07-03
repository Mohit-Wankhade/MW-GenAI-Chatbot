import api from "./api";

export async function uploadPdf(file, onProgress = () => {}) {

    const formData = new FormData();

    formData.append("file", file);

    const response = await api.post(

        "/upload/pdf",

        formData,

        {

            headers: {

                "Content-Type": "multipart/form-data"

            },

            onUploadProgress: (progressEvent) => {

                if (!progressEvent.total) return;

                const percent = Math.round(

                    (progressEvent.loaded * 100) /

                    progressEvent.total

                );

                onProgress(percent);

            }

        }

    );

    return response.data;

}