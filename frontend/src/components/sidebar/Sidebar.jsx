import {
  LogOut,
  MessageSquarePlus,
  MoreVertical,
  Pencil,
  Sparkles,
  Trash2,
  Upload,
  User,
} from "lucide-react";
import { FaGithub } from "react-icons/fa";
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import GithubModal from "../github/GithubModal";
import UploadModal from "../upload/UploadModal";
import { useAuth } from "../../context/AuthContext";
import { useConversation } from "../../context/ConversationContext";
import {
  deleteConversation,
  getConversation,
  getConversations,
  renameConversation,
} from "../../services/conversationService";

function Logo() {
  return (
    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-[#C8A97E] text-sm font-bold leading-none text-black shadow-md">
      <div className="flex flex-col items-center">
        <span className="text-[16px] font-extrabold">M</span>
        <span className="-mt-1 text-[16px] font-extrabold">W</span>
      </div>
    </div>
  );
}

function EmptyHistory() {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-5 text-center">
      <Sparkles size={22} className="mx-auto mb-3 text-[#C8A97E]" />
      <p className="text-sm font-medium text-gray-300">No chats yet</p>
      <p className="mt-1 text-xs leading-5 text-gray-500">
        Start a new chat after uploading a PDF or indexing a repository.
      </p>
    </div>
  );
}

export default function Sidebar() {
  const navigate = useNavigate();
  const menuRef = useRef(null);

  const [uploadOpen, setUploadOpen] = useState(false);
  const [githubOpen, setGithubOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  const { logout, username } = useAuth();

  const {
    conversations,
    setConversations,
    conversationId,
    setConversationId,
    setMessages,
    refreshHistory,
    refreshConversations,
    resetConversationState,
  } = useConversation();

  async function loadConversations() {
    setHistoryLoading(true);

    try {
      const data = await getConversations();
      setConversations(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(error);
      toast.error("Failed to load conversations.");
    } finally {
      setHistoryLoading(false);
    }
  }

  useEffect(() => {
    loadConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshHistory]);

  useEffect(() => {
    function handleClickOutside(event) {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(null);
      }
    }

    document.addEventListener("mousedown", handleClickOutside);

    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  function handleNewChat() {
    if (resetConversationState) {
      resetConversationState();
      return;
    }

    setConversationId(null);
    setMessages([]);
  }

  async function handleConversationClick(id) {
    if (!id || id === conversationId) {
      return;
    }

    try {
      const data = await getConversation(id);
      setConversationId(id);
      setMessages(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error(error);
      toast.error("Failed to open conversation.");
    }
  }

  async function handleDelete(id) {
    const confirmed = window.confirm("Delete this conversation?");

    if (!confirmed) {
      return;
    }

    try {
      await deleteConversation(id);

      if (conversationId === id) {
        handleNewChat();
      }

      toast.success("Conversation deleted.");
      refreshConversations();
    } catch (error) {
      console.error(error);
      toast.error("Failed to delete conversation.");
    }
  }

  async function handleRename(id, currentTitle) {
    const title = window.prompt("Rename conversation", currentTitle || "New Chat");

    if (!title || !title.trim()) {
      return;
    }

    try {
      await renameConversation(id, title.trim());
      toast.success("Conversation renamed.");
      refreshConversations();
    } catch (error) {
      console.error(error);
      toast.error("Failed to rename conversation.");
    }
  }

  function handleLogout() {
    logout();
    resetConversationState?.();
    navigate("/login", { replace: true });
  }

  function handleIndexSuccess() {
    setUploadOpen(false);
    setGithubOpen(false);
    toast.success("Knowledge base updated.");
  }

  return (
    <aside className="flex h-screen w-72 flex-shrink-0 flex-col border-r border-white/10 bg-[#171717] text-white">
      <div className="border-b border-white/10 px-6 py-7">
        <div className="flex items-center gap-3">
          <Logo />

          <div className="min-w-0">
            <h1 className="truncate text-lg font-semibold">GenAI Assistant</h1>
            <p className="text-xs text-gray-400">Personal AI Workspace</p>
          </div>
        </div>
      </div>

      <div className="p-4">
        <button
          type="button"
          onClick={handleNewChat}
          className="flex w-full items-center gap-3 rounded-xl bg-[#C8A97E] p-3 font-semibold text-[#171717] shadow-md transition-all duration-200 hover:scale-[1.02] hover:bg-[#B7946A]"
        >
          <MessageSquarePlus size={20} />
          <span className="font-medium">New Chat</span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto px-4">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-[10px] uppercase tracking-[0.18em] text-gray-500">
            Recent Chats
          </p>

          {historyLoading && (
            <span className="text-[10px] text-gray-500">Loading...</span>
          )}
        </div>

        <div className="space-y-2" ref={menuRef}>
          {!historyLoading && conversations.length === 0 ? (
            <EmptyHistory />
          ) : (
            conversations.map((conversation) => (
              <div key={conversation.id} className="group relative">
                <button
                  type="button"
                  onClick={() => handleConversationClick(conversation.id)}
                  className={`flex w-full items-center gap-3 rounded-xl p-3 pr-10 text-left transition-all duration-200 ${
                    conversationId === conversation.id
                      ? "border-l-4 border-[#C8A97E] bg-[#2b2d31]"
                      : "hover:scale-[1.01] hover:bg-[#2d2f34]"
                  }`}
                  title={conversation.title}
                >
                  <MessageSquarePlus size={16} className="flex-shrink-0 text-[#C8A97E]" />

                  <span className="truncate text-sm">
                    {conversation.title || "New Chat"}
                  </span>
                </button>

                <button
                  type="button"
                  onClick={() =>
                    setMenuOpen(menuOpen === conversation.id ? null : conversation.id)
                  }
                  className="absolute right-2 top-2 rounded-lg px-2 py-1 text-gray-400 opacity-80 transition hover:bg-[#444] hover:text-white group-hover:opacity-100"
                  aria-label="Conversation menu"
                >
                  <MoreVertical size={16} />
                </button>

                {menuOpen === conversation.id && (
                  <div className="absolute right-0 top-10 z-50 w-40 overflow-hidden rounded-lg border border-white/10 bg-[#26282d] shadow-lg">
                    <button
                      type="button"
                      onClick={() => {
                        setMenuOpen(null);
                        handleRename(conversation.id, conversation.title);
                      }}
                      className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm hover:bg-[#343541]"
                    >
                      <Pencil size={14} />
                      Rename
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        setMenuOpen(null);
                        handleDelete(conversation.id);
                      }}
                      className="flex w-full items-center gap-2 px-4 py-2 text-left text-sm text-red-400 hover:bg-red-500/10"
                    >
                      <Trash2 size={14} />
                      Delete
                    </button>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      <div className="border-t border-white/10 p-4">
        <p className="mb-3 text-[10px] uppercase tracking-[0.18em] text-gray-500">
          Workspace
        </p>

        <div className="space-y-2">
          <button
            type="button"
            onClick={() => setUploadOpen(true)}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-3 transition-all duration-200 hover:translate-x-1 hover:bg-[#2d2f34]"
          >
            <Upload size={18} />
            Upload PDF
          </button>

          <button
            type="button"
            onClick={() => setGithubOpen(true)}
            className="flex w-full items-center gap-3 rounded-xl px-3 py-3 transition-all duration-200 hover:translate-x-1 hover:bg-[#2d2f34]"
          >
            <FaGithub size={18} />
            Index GitHub
          </button>
        </div>
      </div>

      <div className="border-t border-[#2a2a2a] p-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex min-w-0 items-center gap-4">
            <div className="flex h-11 w-11 flex-shrink-0 items-center justify-center rounded-full bg-[#C8A97E] text-[#171717] shadow-md">
              <User size={18} />
            </div>

            <div className="min-w-0">
              <p className="truncate font-medium">{username || "User"}</p>
              <p className="text-xs text-gray-400">Signed in</p>
            </div>
          </div>

          <button
            type="button"
            onClick={handleLogout}
            className="rounded-xl p-2 transition-all duration-200 hover:bg-red-500/10 hover:text-red-400"
            aria-label="Logout"
          >
            <LogOut size={18} />
          </button>
        </div>
      </div>

      <UploadModal
        open={uploadOpen}
        onClose={() => setUploadOpen(false)}
        onSuccess={handleIndexSuccess}
      />

      <GithubModal
        open={githubOpen}
        onClose={() => setGithubOpen(false)}
        onSuccess={handleIndexSuccess}
      />
    </aside>
  );
}