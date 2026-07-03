import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { User, Sparkles } from "lucide-react";

import ThinkingIndicator from "./ThinkingIndicator";
import CodeBlock from "./CodeBlock";
import SourceCards from "./SourceCards";

export default function MessageBubble({ message }) {

    const isUser = message.role === "user";

    return (

        <div
            className={`flex gap-4 ${
                isUser ? "justify-end" : "justify-start"
            }`}
        >

            {!isUser && (

                <div
                    className="
                        w-10
                        h-10
                        rounded-full
                        bg-[#A9824F]
                        flex
                        items-center
                        justify-center
                        shadow
                        flex-shrink-0
                    "
                >

                    <Sparkles
                        size={18}
                        className="text-white"
                    />

                </div>

            )}

            <div
                className={`
                    max-w-3xl
                    rounded-3xl
                    px-6
                    py-5
                    shadow-xl
                    border
                    ${
                        isUser
                            ? "bg-[#b89363] text-white border-[#C8A97E]"
                            : "bg-[#343541] text-white border-[#50535a]"
                    }
                `}
            >

                {message.thinking ? (

                    <ThinkingIndicator />

                ) : (

                    <div className="prose prose-invert max-w-none">

                        <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                                code({
                                    inline,
                                    className,
                                    children
                                }) {

                                    const match =
                                        /language-(\w+)/.exec(
                                            className || ""
                                        );

                                    if (!inline && match) {

                                        return (

                                            <CodeBlock
                                                language={match[1]}
                                                value={String(children).replace(
                                                    /\n$/,
                                                    ""
                                                )}
                                            />

                                        );

                                    }

                                    return (

                                        <code
                                            className="
                                                bg-[#1E1F22]
                                                text-[#F7D794]
                                                px-1.5
                                                py-0.5
                                                rounded
                                            "
                                        >

                                            {children}

                                        </code>

                                    );

                                },
                            }}
                        >

                            {message.content}

                        </ReactMarkdown>

                        {!isUser &&
                            message.sources &&
                            message.sources.length > 0 && (

                                <div className="mt-6">

                                    <SourceCards
                                        sources={message.sources}
                                    />

                                </div>

                            )}

                    </div>

                )}

            </div>

            {isUser && (

                <div
                    className="
                        w-10
                        h-10
                        rounded-full
                        bg-[#a9824f]
                        flex
                        items-center
                        justify-center
                        shadow
                        flex-shrink-0
                    "
                >

                    <User
                        size={18}
                        className="text-white"
                    />

                </div>

            )}

        </div>

    );

}