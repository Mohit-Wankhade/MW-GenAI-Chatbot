import { useEffect, useRef } from "react";
import { MessageCircle, Sparkles, UploadCloud } from "lucide-react";
import { FaGithub } from "react-icons/fa";

import { useConversation } from "../../context/ConversationContext";
import MessageBubble from "./MessageBubble";

function EmptyStateCard({ icon, title, description }) {
  return (
    <div className="rounded-2xl border border-[#d9c9a8] bg-white px-5 py-4 text-left text-[#3E3428] shadow-sm">
      <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-xl bg-[#f2e7d5] text-[#A9824F]">
        {icon}
      </div>

      <div className="font-semibold">{title}</div>

      <p className="mt-1 text-sm leading-5 text-[#756B5F]">
        {description}
      </p>
    </div>
  );
}

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
    <section className="flex-1 overflow-y-auto bg-[#D8CCB8] px-4 py-6 sm:px-8">
      {messages.length === 0 ? (
        <div className="flex h-full items-center justify-center">
          <div className="mx-auto max-w-4xl text-center">
            <div className="mx-auto mb-8 flex h-20 w-20 items-center justify-center rounded-3xl bg-[#C8A97E] shadow-lg">
              <Sparkles size={38} className="text-white" />
            </div>

            <h1 className="text-4xl font-bold text-[#3E3428] sm:text-5xl">
              GenAI Assistant
            </h1>

            <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-[#756B5F] sm:text-lg">
              Upload PDFs or index GitHub repositories, then ask questions from
              your private knowledge base using retrieval-augmented AI.
            </p>

            <div className="mt-10 grid gap-4 sm:grid-cols-3">
              <EmptyStateCard
                icon={<UploadCloud size={20} />}
                title="Upload PDFs"
                description="Index documents and ask page-grounded questions."
              />

              <EmptyStateCard
                icon={<FaGithub size={20} />}
                title="Index GitHub"
                description="Chat with source code, READMEs, and config files."
              />

              <EmptyStateCard
                icon={<MessageCircle size={20} />}
                title="Ask Naturally"
                description="Use normal language and continue with follow-up questions."
              />
            </div>
          </div>
        </div>
      ) : (
        <div className="mx-auto max-w-5xl space-y-8">
          {messages.map((message, index) => (
            <MessageBubble
              key={message.id || `${message.role}-${index}`}
              message={message}
            />
          ))}

          <div ref={bottomRef} />
        </div>
      )}
    </section>
  );
}