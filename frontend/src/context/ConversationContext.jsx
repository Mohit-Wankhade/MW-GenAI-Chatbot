import { createContext, useContext, useState } from "react";

const ConversationContext = createContext();

export function ConversationProvider({ children }) {

    const [conversationId, setConversationId] = useState(null);

    const [messages, setMessages] = useState([]);

    const [conversations, setConversations] = useState([]);

    const [refreshHistory, setRefreshHistory] = useState(0);

    function refreshConversations() {
        setRefreshHistory(prev => prev + 1);
    }

    return (

        <ConversationContext.Provider
            value={{
                messages,
                setMessages,

                conversationId,
                setConversationId,

                conversations,
                setConversations,

                refreshHistory,
                refreshConversations
            }}
        >

            {children}

        </ConversationContext.Provider>

    );

}

export function useConversation() {

    return useContext(ConversationContext);

}