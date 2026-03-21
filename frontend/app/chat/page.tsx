import ChatWindow from "@/components/ai/ChatWindow";

export default function ChatPage() {
  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] gap-4">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Coach</h1>
        <p className="text-sm text-gray-400 mt-1">Powered by your local data. Runs on your machine — zero cloud.</p>
      </div>
      <div className="card flex-1 flex flex-col overflow-hidden">
        <ChatWindow />
      </div>
    </div>
  );
}
