"use client";
import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { sendChat } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface Props {
  reportId: string;
  initialFollowups?: string[];
}

export default function ChatPanel({ reportId, initialFollowups = [] }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [followups, setFollowups] = useState<string[]>(
    initialFollowups.length
      ? initialFollowups
      : ["What should I do with this message?", "How do I report this?", "Has anyone else received this?"]
  );
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send(text: string) {
    if (!text.trim() || loading) return;
    const userMsg: Message = { role: "user", content: text };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      const res = await sendChat(reportId, text, history);
      setMessages((prev) => [...prev, { role: "assistant", content: res.response }]);
      setFollowups(res.suggested_followups ?? []);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "I'm having trouble connecting right now. If this is urgent, call TD at 1-866-222-3456." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="border border-gray-200 rounded-2xl overflow-hidden">
      {/* Header */}
      <div className="bg-td-green-light border-b border-gray-200 px-5 py-3 flex items-center gap-2">
        <div className="w-2 h-2 rounded-full bg-td-green" />
        <span className="text-sm font-semibold text-td-green">Ask TD's AI about this report</span>
      </div>

      {/* Messages */}
      <div className="px-5 py-4 space-y-3 max-h-72 overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-sm text-td-muted text-center py-4">
            Have questions about this verdict? Ask anything below.
          </p>
        )}
        <AnimatePresence initial={false}>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-td-green text-white rounded-br-sm"
                    : "bg-gray-100 text-td-dark rounded-bl-sm"
                }`}
              >
                {msg.content}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <div className="flex justify-start">
            <div className="bg-gray-100 rounded-2xl rounded-bl-sm px-4 py-3 flex gap-1">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-td-muted"
                  animate={{ scale: [1, 1.4, 1] }}
                  transition={{ duration: 0.8, delay: i * 0.15, repeat: Infinity }}
                />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Suggested follow-ups */}
      {followups.length > 0 && !loading && (
        <div className="px-5 pb-3 flex flex-wrap gap-2">
          {followups.map((f, i) => (
            <button
              key={i}
              onClick={() => send(f)}
              className="text-xs border border-td-green/30 text-td-green bg-td-green-light hover:bg-td-green hover:text-white rounded-full px-3 py-1.5 transition-colors"
            >
              {f}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="border-t border-gray-100 px-4 py-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && (e.preventDefault(), send(input))}
          placeholder="Ask a question…"
          className="flex-1 text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-td-green/30 focus:border-td-green transition-colors"
        />
        <button
          onClick={() => send(input)}
          disabled={!input.trim() || loading}
          className="bg-td-green hover:bg-td-green-dark disabled:opacity-40 text-white rounded-lg px-4 py-2 text-sm font-medium transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
}
