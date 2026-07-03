import { Upload, Loader2 } from "lucide-react";
import { useRef, useState } from "react";
import { uploadPdf } from "../../services/uploadService";
import SuccessCard from "../common/SuccessCard";
import toast from "react-hot-toast";

export default function UploadDropzone({ onSuccess }) {

    const fileInputRef = useRef(null);

    const [dragging, setDragging] = useState(false);

    const [loading, setLoading] = useState(false);

    const [progress, setProgress] = useState(0);

    const [result, setResult] = useState(null);

    async function handleFile(file) {

        if (!file) return;

        if (file.type !== "application/pdf") {

            setMessage("❌ Please select a PDF file.");

            return;

        }

        try {

            setProgress(0);
            
            setLoading(true);

            setResult(null);
            const data = await uploadPdf(file, setProgress);

            setResult(data);

            

        }

        catch (err) {

            console.error(err);

            setResult({

                error: true,

                message: "Upload failed."

                });

        }

        finally {

            setLoading(false);

        }

    }

    return (

        <div

            onDragOver={(e) => {

                e.preventDefault();

                setDragging(true);

            }}

            onDragEnter={(e) => {

                e.preventDefault();

                setDragging(true);

            }}

            onDragLeave={(e) => {

                e.preventDefault();

                setDragging(false);

            }}

            onDrop={(e) => {

                e.preventDefault();

                setDragging(false);

                const file = e.dataTransfer.files[0];

                handleFile(file);

            }}

            className={`
                border-2
                border-dashed
                rounded-2xl
                p-10
                text-center
                transition-all
                duration-200

                ${
                    dragging
? "border-[#C6A969] bg-[#C6A969]/10 scale-[1.01]"
: "border-[#4A4A4A] hover:border-[#C6A969]"
                }
            `}
        >

            <Upload
                size={48}
                className="mx-auto text-[#C6A969] mb-5"
            />

            <h3 className="text-xl font-semibold text-[#F4E7D3]">

                {dragging
                    ? "📄 Drop your PDF here"
                    : "Drag & Drop your PDF"}

            </h3>

            <p className="text-[#B9AE9F] mt-2">

                or click below to browse

            </p>

            <input

                ref={fileInputRef}

                type="file"

                accept=".pdf"

                hidden

                onChange={(e) =>

                    handleFile(e.target.files[0])

                }

            />

            <button

                disabled={loading}

                onClick={() => fileInputRef.current.click()}

                className="
                mt-8
                bg-[#C6A969]
                hover:bg-[#D4B67A]
                text-[#1C1C1C]
                font-semibold
                disabled:bg-[#555]
                px-6
                py-3
                rounded-xl
                transition-all
                duration-200
                shadow-md
                hover:shadow-lg
                flex
                items-center
                gap-2
                mx-auto
                "

            >

                {loading ? (

                    <>

                        <Loader2
                            size={18}
                            className="animate-spin"
                        />

                        Uploading... {progress}%

                    </>

                ) : (

                    "Choose PDF"

                )}

            </button>
            {loading && (

                <div className="mt-5">

                    <div className="w-full h-2 bg-gray-700 rounded-full overflow-hidden">

                        <div

                            className="h-full bg-[#C6A969] transition-all duration-300"

                            style={{

                            width: `${progress}%`

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

        <div className="mt-6 text-[#E57373]">

            ❌ {result.message}

        </div>

    ) : (

        <SuccessCard

            title="✅ PDF Indexed Successfully"

            items={[

                {
                    icon: "📄",
                    label: "File",
                    value: result.file
                },

                {
                    icon: "📚",
                    label: "Pages",
                    value: result.pages
                },

                {
                    icon: "🧩",
                    label: "Chunks",
                    value: result.chunks
                }

            ]}

            footer="Ready to answer questions."

            onContinue={onSuccess}

        />

    )

)}

        </div>

    );

}