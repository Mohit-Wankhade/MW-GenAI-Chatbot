import Sidebar from "../components/sidebar/Sidebar";
import ChatWindow from "../components/chat/ChatWindow";
import ChatInput from "../components/chat/ChatInput";

export default function Chat() {

    return (

        <div className="flex h-screen bg-[##E2D9CB] text-white">

            <Sidebar />

            <div className="flex flex-col flex-1">

                <ChatWindow />

                <ChatInput />

            </div>

        </div>

    );

}