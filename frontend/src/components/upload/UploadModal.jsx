import { X } from "lucide-react";
import UploadDropzone from "./UploadDropzone";

export default function UploadModal({ open, onClose }) {

    if (!open) return null;

    return (

        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60">

            <div className="bg-[#202123] rounded-2xl w-[500px] border border-[#3b3d42] shadow-2xl">

                {/* Header */}

                <div className="flex items-center justify-between p-5 border-b border-[#3b3d42]">

                    <h2 className="text-xl font-semibold text-white">

                        Upload PDF

                    </h2>

                    <button

                        onClick={onClose}

                        className="p-2 rounded-lg hover:bg-[#343541] transition"

                    >

                        <X size={20} className="text-gray-400" />

                    </button>

                </div>

                {/* Body */}

                <div className="p-6">

                    <UploadDropzone onSuccess={onClose} />

                </div>

            </div>

        </div>

    );

}