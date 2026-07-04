import ChatInput from "../components/chat/ChatInput";
import ChatWindow from "../components/chat/ChatWindow";
import Sidebar from "../components/sidebar/Sidebar";

export default function Chat() {
  return (
    <div className="flex h-screen overflow-hidden bg-[#E2D9CB] text-white">
      <Sidebar />

      <main className="flex min-w-0 flex-1 flex-col">
        <ChatWindow />
        <ChatInput />
      </main>
    </div>
  );
}