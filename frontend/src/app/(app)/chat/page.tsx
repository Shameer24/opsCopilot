import AuthGuard from "@/components/AuthGuard";
import ChatBox from "@/components/ChatBox";

export default function ChatPage() {
  return (
    <AuthGuard>
      <div className="space-y-4">
        <h1 className="text-xl font-semibold">Chat</h1>
        <ChatBox />
      </div>
    </AuthGuard>
  );
}