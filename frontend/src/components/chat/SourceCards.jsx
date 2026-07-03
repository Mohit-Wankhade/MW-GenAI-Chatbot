import { FileText, GitBranch } from "lucide-react";

export default function SourceCards({ sources }) {
    if (!sources || sources.length === 0) return null;

    return (
        <div className="mt-6">
            <p className="text-xs uppercase tracking-[0.18em] text-[#8b7355] mb-3 font-semibold">
                Sources
            </p>

            <div className="grid gap-3 sm:grid-cols-2">
                {sources.map((source, index) => (
                    <div
                        key={index}
                        className="
                            rounded-2xl
                            border
                            border-[#d5c1a0]
                            bg-[#fcfaf7]
                            p-4
                            hover:border-[#b89363]
                            hover:shadow-md
                            transition-all
                        "
                    >
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-[#f2e7d5] flex items-center justify-center">
                                {source.type === "pdf" ? (
                                    <FileText
                                        size={18}
                                        className="text-[#b44b3c]"
                                    />
                                ) : (
                                    <GitBranch
                                        size={18}
                                        className="text-[#8b7355]"
                                    />
                                )}
                            </div>

                            <div className="flex-1 overflow-hidden">
                                <div className="font-medium text-[#3b342d] truncate">
                                    {source.name}
                                </div>

                                <div className="text-sm text-[#7d6a51] mt-1">
                                    {source.type === "pdf"
                                        ? `PDF • Page ${source.page}`
                                        : "GitHub Repository"}
                                </div>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}