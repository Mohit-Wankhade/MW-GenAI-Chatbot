import { X } from "lucide-react";
import GithubForm from "./GithubForm";

export default function GithubModal({ open, onClose }) {

    if (!open) return null;

    return (

        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">

            <div className="w-full max-w-lg rounded-2xl bg-[#202123] border border-[#343541] shadow-2xl">

                <div className="flex items-center justify-between p-5 border-b border-[#343541]">

                    <h2 className="text-xl font-semibold text-white">

                        Index GitHub Repository

                    </h2>

                    <button

                        onClick={onClose}

                        className="p-2 rounded-lg hover:bg-[#343541]"

                    >

                        <X size={18} />

                    </button>

                </div>

                <div className="p-6">

                    <GithubForm onSuccess={onClose} />

                </div>

            </div>

        </div>

    );

}