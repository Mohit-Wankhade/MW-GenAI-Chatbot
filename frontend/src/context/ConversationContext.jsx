import { createContext, useCallback, useContext, useMemo, useState } from "react";

const ConversationContext = createContext(null);

export function ConversationProvider({ children }) {
  const [conversationId, setConversationId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [refreshHistory, setRefreshHistory] = useState(0);
  const [isStreaming, setIsStreaming] = useState(false);
  const [activeSource, setActiveSource] = useState(null);

  const refreshConversations = useCallback(() => {
    setRefreshHistory((previousValue) => previousValue + 1);
  }, []);

  const resetConversationState = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setActiveSource(null);
    setIsStreaming(false);
  }, []);

  const startNewConversation = useCallback(() => {
    setConversationId(null);
    setMessages([]);
    setActiveSource(null);
  }, []);

  const appendMessage = useCallback((message) => {
    setMessages((previousMessages) => [
      ...previousMessages,
      {
        id: message.id || `${Date.now()}-${Math.random()}`,
        role: message.role,
        content: message.content || "",
        sources: message.sources || [],
        timestamp: message.timestamp || new Date().toISOString(),
        isStreaming: Boolean(message.isStreaming),
      },
    ]);
  }, []);

  const updateLastAssistantMessage = useCallback((contentChunk) => {
    setMessages((previousMessages) => {
      if (previousMessages.length === 0) {
        return previousMessages;
      }

      const updatedMessages = [...previousMessages];
      const lastIndex = updatedMessages.length - 1;
      const lastMessage = updatedMessages[lastIndex];

      if (lastMessage.role !== "assistant") {
        return previousMessages;
      }

      updatedMessages[lastIndex] = {
        ...lastMessage,
        content: `${lastMessage.content || ""}${contentChunk || ""}`,
      };

      return updatedMessages;
    });
  }, []);

  const finalizeLastAssistantMessage = useCallback((sources = []) => {
    setMessages((previousMessages) => {
      if (previousMessages.length === 0) {
        return previousMessages;
      }

      const updatedMessages = [...previousMessages];
      const lastIndex = updatedMessages.length - 1;
      const lastMessage = updatedMessages[lastIndex];

      if (lastMessage.role !== "assistant") {
        return previousMessages;
      }

      updatedMessages[lastIndex] = {
        ...lastMessage,
        sources,
        isStreaming: false,
      };

      return updatedMessages;
    });
  }, []);

  const value = useMemo(
    () => ({
      messages,
      setMessages,
      appendMessage,
      updateLastAssistantMessage,
      finalizeLastAssistantMessage,

      conversationId,
      setConversationId,

      conversations,
      setConversations,

      refreshHistory,
      refreshConversations,

      isStreaming,
      setIsStreaming,

      activeSource,
      setActiveSource,

      startNewConversation,
      resetConversationState,
    }),
    [
      messages,
      appendMessage,
      updateLastAssistantMessage,
      finalizeLastAssistantMessage,
      conversationId,
      conversations,
      refreshHistory,
      refreshConversations,
      isStreaming,
      activeSource,
      startNewConversation,
      resetConversationState,
    ]
  );

  return (
    <ConversationContext.Provider value={value}>
      {children}
    </ConversationContext.Provider>
  );
}

export function useConversation() {
  const context = useContext(ConversationContext);

  if (!context) {
    throw new Error("useConversation must be used inside ConversationProvider.");
  }

  return context;
}