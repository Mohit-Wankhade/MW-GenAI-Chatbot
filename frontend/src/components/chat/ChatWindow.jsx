import { useEffect, useRef } from "react";
import { Sparkles } from "lucide-react";
import MessageBubble from "./MessageBubble";
import { useConversation } from "../../context/ConversationContext";

export default function ChatWindow() {
    const { messages } = useConversation();

    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({
            behavior: "smooth",
            block: "end",
        });
    }, [messages]);

    return (
        <div className="flex-1 overflow-y-auto bg-[#D8CCB8] px-8 py-6">

            {messages.length === 0 ? (

                <div className="h-full flex items-center justify-center">

                    <div className="text-center max-w-2xl">

                        <div className="mx-auto mb-8 w-20 h-20 rounded-3xl bg-[#C8A97E] flex items-center justify-center shadow-lg">

                            <Sparkles
                                size={38}
                                className="text-white"
                            />

                        </div>

                        <h1 className="text-5xl font-bold text-[#3E3428]">

                            GenAI Assistant

                        </h1>

                        <p className="mt-5 text-lg text-[#756B5F]">

                            Upload PDFs or GitHub repositories and chat with
                            your knowledge base using AI.

                        </p>

                        <div className="mt-10 flex justify-center gap-4 flex-wrap">

                            <div
                                className="
                                rounded-2xl
                                bg-white
                                border
                                border-[#d9c9a8]
                                px-6
                                py-4
                                shadow-sm
                                flex
                                items-center
                                gap-3
                                text-[#3E3428]
                                font-semibold
                                ">
                                    <span className="text-xl">📄</span>

                                 Upload PDFs

                            </div>

                            <div
                                className="
                                rounded-2xl
                                bg-white
                                border
                                border-[#d9c9a8]
                                px-6
                                py-4
                                shadow-sm
                                flex
                                items-center
                                gap-3
                                text-[#3E3428]
                                font-semibold
                                ">
                                    <span className="text-xl">

                                💻</span> Index GitHub Repositories

                            </div>

                            <div
                                className="
                                rounded-2xl
                                bg-white
                                border
                                border-[#d9c9a8]
                                px-6
                                py-4
                                shadow-sm
                                flex
                                items-center
                                gap-3
                                text-[#3E3428]
                                font-semibold
                                ">
                                    <span className="text-xl">💬</span>

                                 Ask Questions Naturally

                            </div>

                        </div>

                    </div>

                </div>

            ) : (

                <div className="max-w-5xl mx-auto space-y-8">

                    {messages.map((message, index) => (

                        <MessageBubble
                            key={index}
                            message={message}
                        />

                    ))}

                    <div ref={bottomRef} />

                </div>

            )}

        </div>
    );
}