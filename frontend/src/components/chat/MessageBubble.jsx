import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Sparkles, User } from "lucide-react";

import CodeBlock from "./CodeBlock";
import SourceCards from "./SourceCards";
import ThinkingIndicator from "./ThinkingIndicator";

function formatTime(timestamp) {
  if (!timestamp) {
    return "";
  }

  try {
    return new Intl.DateTimeFormat(undefined, {
      hour: "2-digit",
      minute: "2-digit",
    }).format(new Date(timestamp));
  } catch {
    return "";
  }
}

export default function MessageBubble({ message }) {
  const isUser = message.role === "user";
  const time = formatTime(message.timestamp);

  return (
    <article className={`flex gap-4 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-[#A9824F] shadow">
          <Sparkles size={18} className="text-white" />
        </div>
      )}

      <div className={`flex max-w-3xl flex-col ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={`rounded-3xl border px-6 py-5 shadow-xl ${
            isUser
              ? "border-[#C8A97E] bg-[#b89363] text-white"
              : "border-[#50535a] bg-[#343541] text-white"
          }`}
        >
          {message.thinking ? (
            <ThinkingIndicator label="Thinking" />
          ) : (
            <>
              <div className="prose prose-invert max-w-none prose-pre:m-0 prose-pre:bg-transparent">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || "");
                      const value = String(children).replace(/\n$/, "");

                      if (!inline && match) {
                        return (
                          <CodeBlock
                            language={match[1]}
                            value={value}
                          />
                        );
                      }

                      return (
                        <code
                          className="rounded bg-[#1E1F22] px-1.5 py-0.5 text-[#F7D794]"
                          {...props}
                        >
                          {children}
                        </code>
                      );
                    },

                    a({ children, href, ...props }) {
                      return (
                        <a
                          href={href}
                          target="_blank"
                          rel="noreferrer"
                          className="text-[#F7D794] underline underline-offset-4"
                          {...props}
                        >
                          {children}
                        </a>
                      );
                    },
                  }}
                >
                  {message.content || ""}
                </ReactMarkdown>
              </div>

              {!isUser && Boolean(message.isStreaming) && (
                <div className="mt-4">
                  <ThinkingIndicator label="Generating" compact />
                </div>
              )}
            </>
          )}
        </div>

        {!isUser && message.sources && message.sources.length > 0 && (
          <SourceCards sources={message.sources} />
        )}

        {time && (
          <div
            className={`mt-2 text-xs ${
              isUser ? "text-[#6f6253]" : "text-[#756B5F]"
            }`}
          >
            {time}
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-[#a9824f] shadow">
          <User size={18} className="text-white" />
        </div>
      )}
    </article>
  );
}