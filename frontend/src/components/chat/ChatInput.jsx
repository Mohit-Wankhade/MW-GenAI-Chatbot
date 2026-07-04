import { SendHorizontal, Square } from "lucide-react";
import { useRef, useState } from "react";
import toast from "react-hot-toast";

import { useConversation } from "../../context/ConversationContext";
import { getAuthToken } from "../../services/api";
import api from "../../services/api";
import {
  createConversation,
  getConversation,
} from "../../services/conversationService";

const MAX_MESSAGE_LENGTH = 6000;

function getStreamUrl() {
  const baseURL = api.defaults.baseURL || "/";

  if (baseURL === "/") {
    return "/chat-stream";
  }

  return `${baseURL.replace(/\/$/, "")}/chat-stream`;
}

function createLocalMessage(role, content, extra = {}) {
  return {
    id: `${role}-${Date.now()}-${Math.random().toString(16).slice(2)}`,
    role,
    content,
    timestamp: new Date().toISOString(),
    ...extra,
  };
}

export default function ChatInput() {
  const {
    setMessages,
    conversationId,
    setConversationId,
    refreshConversations,
    setIsStreaming,
  } = useConversation();

  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);

  const abortControllerRef = useRef(null);
  const textareaRef = useRef(null);

  function resizeTextarea() {
    const textarea = textareaRef.current;

    if (!textarea) {
      return;
    }

    textarea.style.height = "auto";
    textarea.style.height = `${Math.min(textarea.scrollHeight, 140)}px`;
  }

  function updateText(value) {
    setText(value);

    requestAnimationFrame(() => {
      resizeTextarea();
    });
  }

  function stopStreaming() {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    setLoading(false);
    setIsStreaming(false);
  }

  async function refreshMessages(activeConversationId) {
    try {
      const updatedConversation = await getConversation(activeConversationId);
      setMessages(updatedConversation);
      refreshConversations();
    } catch (error) {
      console.error("Failed to refresh conversation:", error);
    }
  }

  async function sendMessage() {
    const question = text.trim();

    if (!question || loading) {
      return;
    }

    if (question.length > MAX_MESSAGE_LENGTH) {
      toast.error(`Message is too long. Maximum ${MAX_MESSAGE_LENGTH} characters allowed.`);
      return;
    }

    const token = getAuthToken();

    if (!token) {
      toast.error("Please login again.");
      return;
    }

    setText("");
    setLoading(true);
    setIsStreaming(true);

    requestAnimationFrame(() => {
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }
    });

    setMessages((previousMessages) => [
      ...previousMessages,
      createLocalMessage("user", question),
      createLocalMessage("assistant", "", {
        thinking: true,
        isStreaming: true,
      }),
    ]);

    let activeConversationId = conversationId;
    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      if (!activeConversationId) {
        const newConversation = await createConversation();
        activeConversationId = newConversation.conversation_id;

        setConversationId(activeConversationId);
        refreshConversations();
      }

      const response = await fetch(getStreamUrl(), {
        method: "POST",
        signal: abortController.signal,
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
          Accept: "text/plain",
        },
        body: JSON.stringify({
          query: question,
          conversation_id: activeConversationId,
        }),
      });

      if (!response.ok) {
        let errorMessage = "Streaming failed. Please try again.";

        try {
          const errorData = await response.json();

          if (typeof errorData?.detail === "string") {
            errorMessage = errorData.detail;
          }
        } catch {
          // Response may not be JSON.
        }

        throw new Error(errorMessage);
      }

      if (!response.body) {
        throw new Error("Streaming is not supported by this browser.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");

      let aiResponse = "";
      let firstChunkReceived = false;

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          break;
        }

        const chunk = decoder.decode(value, {
          stream: true,
        });

        if (!chunk) {
          continue;
        }

        aiResponse += chunk;

        if (!firstChunkReceived) {
          firstChunkReceived = true;
        }

        setMessages((previousMessages) => {
          const updatedMessages = [...previousMessages];
          const lastIndex = updatedMessages.length - 1;
          const lastMessage = updatedMessages[lastIndex];

          if (!lastMessage || lastMessage.role !== "assistant") {
            return previousMessages;
          }

          updatedMessages[lastIndex] = {
            ...lastMessage,
            content: aiResponse,
            thinking: false,
            isStreaming: true,
          };

          return updatedMessages;
        });
      }

      setMessages((previousMessages) => {
        const updatedMessages = [...previousMessages];
        const lastIndex = updatedMessages.length - 1;
        const lastMessage = updatedMessages[lastIndex];

        if (!lastMessage || lastMessage.role !== "assistant") {
          return previousMessages;
        }

        updatedMessages[lastIndex] = {
          ...lastMessage,
          content: aiResponse || "No response received.",
          thinking: false,
          isStreaming: false,
        };

        return updatedMessages;
      });

      await refreshMessages(activeConversationId);
    } catch (error) {
      if (error?.name === "AbortError") {
        setMessages((previousMessages) => {
          const updatedMessages = [...previousMessages];
          const lastIndex = updatedMessages.length - 1;
          const lastMessage = updatedMessages[lastIndex];

          if (!lastMessage || lastMessage.role !== "assistant") {
            return previousMessages;
          }

          updatedMessages[lastIndex] = {
            ...lastMessage,
            content: lastMessage.content || "Response stopped.",
            thinking: false,
            isStreaming: false,
          };

          return updatedMessages;
        });

        toast("Response stopped.");
      } else {
        console.error(error);

        setMessages((previousMessages) => {
          const updatedMessages = [...previousMessages];
          const lastIndex = updatedMessages.length - 1;

          updatedMessages[lastIndex] = createLocalMessage(
            "assistant",
            `⚠️ ${error?.message || "Failed to connect to server."}`,
            {
              thinking: false,
              isStreaming: false,
            }
          );

          return updatedMessages;
        });

        toast.error(error?.message || "Failed to connect to server.");
      }
    } finally {
      abortControllerRef.current = null;
      setLoading(false);
      setIsStreaming(false);
    }
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  return (
    <div className="border-t border-[#d2c6b4] bg-[#ECE6DB] py-3">
      <div className="mx-auto max-w-5xl px-4 sm:px-6">
        <div className="flex items-end rounded-2xl border border-[#cdb894] bg-white px-4 py-2 shadow-lg transition focus-within:border-[#aa8961] focus-within:shadow-md">
          <textarea
            ref={textareaRef}
            rows={1}
            value={text}
            disabled={loading}
            onChange={(event) => updateText(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={loading ? "Assistant is responding..." : "Ask anything..."}
            className="max-h-36 min-h-9 flex-1 resize-none bg-transparent py-1 leading-7 text-[#3f3a34] outline-none placeholder:text-[#9a8f80] disabled:cursor-not-allowed disabled:opacity-70"
          />

          {loading ? (
            <button
              type="button"
              onClick={stopStreaming}
              className="ml-3 flex h-9 w-9 items-center justify-center rounded-full bg-[#7d6a51] text-white transition hover:bg-[#5f4f3d]"
              title="Stop response"
              aria-label="Stop response"
            >
              <Square size={15} fill="currentColor" />
            </button>
          ) : (
            <button
              type="button"
              disabled={!text.trim()}
              onClick={sendMessage}
              className="ml-3 flex h-9 w-9 items-center justify-center rounded-full bg-[#b08a58] text-white transition hover:bg-[#9b7748] disabled:cursor-not-allowed disabled:bg-[#d9d0c4]"
              title="Send message"
              aria-label="Send message"
            >
              <SendHorizontal size={18} />
            </button>
          )}
        </div>

        <p className="mt-2 text-center text-xs text-[#8a7c6a]">
          Press Enter to send, Shift + Enter for a new line.
        </p>
      </div>
    </div>
  );
}