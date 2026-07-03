import {
    MessageSquarePlus,
    Upload,
    LogOut,
    User,
    Sparkles
} from "lucide-react";
import { FaGithub } from "react-icons/fa";
import UploadModal from "../upload/UploadModal";
import GithubModal from "../github/GithubModal";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import { useConversation } from "../../context/ConversationContext";
import {
    getConversations,
    getConversation,
    deleteConversation,
    renameConversation
} from "../../services/conversationService";


export default function Sidebar() {

    const navigate = useNavigate();
    const [uploadOpen, setUploadOpen] = useState(false);
    const [githubOpen, setGithubOpen] = useState(false);
    const [menuOpen, setMenuOpen] = useState(null);
    const {
    logout,
    username
} = useAuth();
    const {

        conversations,
        setConversations,

        conversationId,
        setConversationId,

        setMessages

    } = useConversation();

    const { refreshHistory } = useConversation();
    async function handleDelete(id) {

    if (!window.confirm("Delete this conversation?"))
        return;

    await deleteConversation(id);

    if (conversationId === id) {

        setConversationId(null);

        setMessages([]);

    }

    loadConversations();

}
    async function handleRename(id, currentTitle) {

    const title = window.prompt(

        "Rename conversation",

        currentTitle

    );

    if (!title) return;

    await renameConversation(id, title);

    loadConversations();

}
    useEffect(() => {
        loadConversations();
        }, [refreshHistory]);
    async function loadConversations() {

        try {

            const data = await getConversations();

            setConversations(data);

        }

        catch (err) {

            console.log(err);

        }

    }

    async function handleNewChat() {

        setConversationId(null);

        setMessages([]);

    }

    async function handleConversationClick(id) {

        try {

            const data = await getConversation(id);

            setConversationId(id);

            setMessages(data);

        }

        catch (err) {

            console.log(err);

        }

    }

    function handleLogout() {

        logout();

        navigate("/");

    }

    return (

        <aside className="w-72 h-screen bg-[#171717] border-r border-white/10 flex flex-col text-white">

            {/* Logo */}
            

            <div className="px-6 py-7 border-b border-white/10">

                <div className="flex items-center gap-3">

                    <div className="w-11 h-11 rounded-xl bg-[#C8A97E] flex items-center justify-center shadow-md text-black font-bold text-sm leading-none">
  <div className="flex flex-col items-center">
    <span className="text-[16px] font-extrabold">M</span>
    <span className="text-[16px] font-extrabold -mt-1">W</span>
  </div>


                    </div>


                    <div>

                        <h1 className="font-semibold text-lg">

                            GenAI Assistant

                        </h1>

                        <p className="text-xs text-gray-400">

                            Personal AI Workspace

                        </p>

                    </div>

                </div>

            </div>

            {/* New Chat */}

            <div className="p-4">

                <button

                    onClick={handleNewChat}

                    className="w-full flex items-center gap-3 rounded-xl bg-[#C8A97E] hover:bg-[#B7946A] text-[#171717] font-semibold transition-all duration-200 hover:scale-[1.02] p-3 shadow-md"

                >

                    <MessageSquarePlus size={20} />

                    <span className="font-medium">

                        New Chat

                    </span>

                </button>

            </div>

            {/* History */}

            <div className="flex-1 overflow-y-auto px-4">

                <p className="uppercase text-[10px] tracking-[0.18em] tracking-wider text-gray-500 mb-3">

                    Recent Chats

                </p>

                <div className="space-y-2">

{conversations.map((conversation) => (

    <div
        key={conversation.id}
        className="relative group"
    >

        <button

            onClick={() =>
                handleConversationClick(conversation.id)
            }

            className={`
                w-full
            flex
            items-center
            gap-3
            text-left
            p-3
            pr-10
            rounded-xl
            transition-all
            duration-200
                ${
                    conversationId === conversation.id
                        ? "border-l-4 border-[#C8A97E] bg-[#2b2d31]"
                : "hover:bg-[#2d2f34] hover:scale-[1.01]"
                }
            `}
        >   
            <MessageSquarePlus
            size={16}
            className="text-[#C8A97E]"
        />

            <span className="truncate">
            {conversation.title}
            </span>

        </button>

        <button

            onClick={() =>

                setMenuOpen(

                    menuOpen === conversation.id

                        ? null

                        : conversation.id

                )

            }

            className="
                absolute
                right-2
                top-2
                px-2
                rounded
                hover:bg-[#444]
            "

        >

            ⋮

        </button>

        {menuOpen === conversation.id && (

            <div
                className="
                    absolute
                    right-0
                    top-10
                    bg-[#26282d]
                    border-white/10
                    rounded-lg
                    shadow-lg
                    hover:bg-[#343541]
                    z-50
                    w-36
                "
            >

                <button

                    onClick={() => {

                        handleRename(
                            conversation.id,
                            conversation.title
                        );

                        setMenuOpen(null);

                    }}

                    className="
                        w-full
                        text-left
                        px-4
                        py-2
                        hover:bg-[#343541]
                    "

                >

                    Rename

                </button>

                <button

                    onClick={() => {

                        handleDelete(
                            conversation.id
                        );

                        setMenuOpen(null);

                    }}

                    className="
                        w-full
                        text-left
                        px-4
                        py-2
                        text-red-400
                        hover:bg-[#3a3a3a]
                    "

                >

                    Delete

                </button>

            </div>

        )}

    </div>

))}

                </div>

            </div>

            {/* Workspace */}

            <div className="border-t border-white/10 p-4">

                <p className="uppercase text-[10px] tracking-[0.18em] tracking-wider text-gray-500 mb-3">

                    Workspace

                </p>

                <div className="space-y-2">

                    <button
                            onClick={() => setUploadOpen(true)}
                            
                            className="
                                w-full
                                flex
                                items-center
                                gap-3
                                rounded-xl
                                px-3
                                py-3
                                hover:bg-[#2d2f34]
                                transition-all
                                duration-200
                                hover:translate-x-1
                                "
                                >
                            <Upload size={18} />
                             Upload PDF
                    </button>

                <UploadModal
                    open={uploadOpen}
                    onClose={() => setUploadOpen(false)}
                />

                    <button

                            onClick={() => setGithubOpen(true)}

                            className="
                                w-full
                                flex
                                items-center
                                gap-3
                                rounded-xl
                                px-3
                                py-3
                                hover:bg-[#2d2f34]
                                transition-all
                                duration-200
                                hover:translate-x-1
                                "

                            >

                        <FaGithub size={18} />

                        Index GitHub

                    </button>

                </div>

            </div>

            {/* User */}

            <div className="border-t border-[#2a2a2a] p-4">

                <div className="flex items-center justify-between">

                    <div className="flex items-center gap-4">

                        <div className="w-11 h-11 rounded-full bg-[#C8A97E] text-[#171717] flex items-center justify-center shadow-md">

                            <User size={18} />

                        </div>

                        <div>

                            <p className="font-medium truncate">

                                {username}

                            </p>

                            <p className="text-xs text-gray-400">

                                Signed in

                            </p>

                        </div>

                    </div>
                    
                    
                    <button

                        onClick={handleLogout}

                        className="
                                p-2
                                rounded-xl
                                hover:bg-red-500/10
                                hover:text-red-400
                                transition-all
                                duration-200
                                "

                    >

                        <LogOut size={18} />

                    </button>

                </div>

            </div>
            <UploadModal
                open={uploadOpen}
                onClose={() => setUploadOpen(false)}
                />
            <GithubModal

                open={githubOpen}
                onClose={() => setGithubOpen(false)}

                />
        </aside>

    );

}