"use client";
import { useState, useRef, useEffect } from "react";
import { queryMemory } from "@/lib/api";

interface Message {
  role: "user" | "ai";
  content: string;
  context?: string[];
}

export default function ChatWindow() {
  const [messages, setMessages] = useState<Message[]>([
    { role: "ai", content: "Hi! I'm your personal AI coach. Ask me anything about your habits, productivity, or patterns. Example: 'Why was I unproductive last week?' or 'When do I code best?'" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: q }]);
    setLoading(true);
    try {
      const res: any = await queryMemory(q);
      setMessages(prev => [...prev, {
        role: "ai",
        content: res.answer || "I couldn't generate a response. Make sure Ollama is running.",
        context: res.context_used,
      }]);
    } catch {
      setMessages(prev => [...prev, { role: "ai", content: "Error reaching the API. Is the server running?" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto flex flex-col gap-4 pb-4">
        {messages.map((m, i) => (
          <div key={i} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
              m.role === "user"
                ? "bg-indigo-600 text-white rounded-br-sm"
                : "bg-white border border-gray-100 text-gray-800 rounded-bl-sm"
            }`}>
              <p>{m.content}</p>
              {m.context && m.context.length > 0 && (
                <details className="mt-2">
                  <summary className="text-xs opacity-60 cursor-pointer">Sources used ({m.context.length})</summary>
                  <ul className="mt-1 space-y-1">
                    {m.context.map((c, j) => (
                      <li key={j} className="text-xs opacity-60 border-t border-white/20 pt-1">{c}</li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-100 rounded-2xl rounded-bl-sm px-4 py-3">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-gray-300 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2 pt-4 border-t border-gray-100">
        <input
          className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-indigo-400 transition-colors"
          placeholder="Ask anything about your life data..."
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={e => e.key === "Enter" && send()}
        />
        <button
          onClick={send}
          disabled={loading || !input.trim()}
          className="bg-indigo-600 text-white px-5 py-2.5 rounded-xl text-sm font-medium hover:bg-indigo-700 disabled:opacity-40 transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
