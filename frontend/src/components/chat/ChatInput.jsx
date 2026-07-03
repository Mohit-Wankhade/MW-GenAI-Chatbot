import { SendHorizontal } from "lucide-react";
import { useState } from "react";
import api from "../../services/api";

import { useConversation } from "../../context/ConversationContext";

export default function ChatInput() {

    const {

        setMessages,

        conversationId,
        setConversationId,

        refreshConversations

    } = useConversation();

    const [text, setText] = useState("");
    const [loading, setLoading] = useState(false);
    console.log("sendMessage", { text, loading });
    async function sendMessage() {

        if (!text.trim() || loading) return;

        const question = text;

        setText("");

        setLoading(true);

        // Add user message
        setMessages(prev => [
            ...prev,
            {
                role: "user",
                content: question
            }
        ]);

        // Assistant placeholder
        let assistantIndex;

        setMessages(prev => {

            assistantIndex = prev.length;

            return [
                ...prev,
                {
                    role: "assistant",
                    content: "",
                    thinking: true
                }
            ];

        });

        try {

            const token = localStorage.getItem("token");

            let activeConversationId = conversationId;

            // Create conversation only once
            if (!activeConversationId) {

                const newConversation = await api.post("/conversation/new");

                activeConversationId =
                    newConversation.data.conversation_id;

                setConversationId(activeConversationId);

                refreshConversations();

            }

            const response = await fetch(`${api.defaults.baseURL}chat-stream`, {
                method: "POST",
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    query: question,
                    conversation_id: activeConversationId,
                }),
                });
            if (!response.ok) {

                throw new Error("Streaming failed");

            }

            const reader = response.body.getReader();

            const decoder = new TextDecoder();

            let aiResponse = "";

            while (true) {

                const { done, value } = await reader.read();

                if (done) break;

                aiResponse += decoder.decode(value);

                setMessages(prev => {

                    const updated = [...prev];

                    updated[updated.length - 1] = {
                        ...updated[updated.length - 1],
                        role: "assistant",
                        content: aiResponse,
                        thinking: false
                    };

                    return updated;

                    });

            }
            try {
                const updatedConversation = await api.get(
                    `/auth/conversation/${activeConversationId}`
                    );

                setMessages(updatedConversation.data);
                refreshConversations();
            } catch (err) {
                console.error("Failed to refresh conversation:", err);
                }

        }

        catch (err) {

            console.error(err);

            setMessages(prev => {

                const updated = [...prev];

                updated[updated.length - 1] = {

                    role: "assistant",
                    content: "⚠️ Failed to connect to server.",
                    thinking: false

                };

                return updated;

            });

        }

        finally {
            console.log("loading -> false");
            setLoading(false);

        }

    }

    function handleKeyDown(e) {

        if (e.key === "Enter" && !e.shiftKey) {

            e.preventDefault();

            sendMessage();

        }

    }

    return (

    <div className="border-t border-[#d2c6b4] bg-[#ECE6DB] py-3">

        <div className="max-w-5xl mx-auto px-6">

            <div
                className="
                    flex
                    items-end
                    rounded-2xl
                    border
                    border-[#cdb894]
                    bg-white
                    shadow-lg
                    transition
                    focus-within:border-[#aa8961]
                    focus-within:shadow-md
                    px-5
                    py-2
                "
            >

                <textarea
                    rows={1}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Ask anything..."
                    className="
                        flex-1
                        resize-none
                        bg-transparent
                        outline-none
                        text-[#3f3a34]
                        placeholder:text-[#9a8f80]
                        h-8
                        max-h-28
                        leading-8
                    "
                />

                <button
                    disabled={loading}
                    onClick={sendMessage}
                    className="
                        ml-3
                        h-9
                        w-9
                        rounded-full
                        bg-[#b08a58]
                        text-white
                        flex
                        items-center
                        justify-center
                        transition
                        hover:bg-[#9b7748]
                        disabled:bg-[#d9d0c4]
                    "
                >
                    <SendHorizontal size={18}/>
                </button>

            </div>

        </div>

    </div>

);

}