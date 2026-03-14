"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { SUBMISSION_KEY } from "@/lib/api";

const TABS = [
  { id: "sms",   label: "SMS / Text",    placeholder: "Paste the suspicious text message here…" },
  { id: "email", label: "Email",         placeholder: "Paste the full email — subject, sender, and body…" },
  { id: "url",   label: "URL",           placeholder: "Paste the suspicious link here…" },
];

export default function SubmitForm() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"sms" | "email" | "url">("sms");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const placeholder = TABS.find((t) => t.id === activeTab)?.placeholder ?? "";

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed) { setError("Please paste the suspicious content above."); return; }
    setError("");
    setLoading(true);

    const reportId = crypto.randomUUID();
    sessionStorage.setItem(SUBMISSION_KEY(reportId), JSON.stringify({ type: activeTab, content: trimmed }));
    router.push(`/scan/${reportId}`);
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      {/* Tabs */}
      <div className="flex border border-gray-200 rounded-xl overflow-hidden mb-4 bg-gray-50">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => { setActiveTab(tab.id as "sms" | "email" | "url"); setContent(""); setError(""); }}
            className={`flex-1 py-2.5 text-sm font-medium transition-colors ${
              activeTab === tab.id
                ? "bg-white text-td-green shadow-sm"
                : "text-td-muted hover:text-td-dark"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Textarea */}
      <textarea
        value={content}
        onChange={(e) => { setContent(e.target.value); setError(""); }}
        placeholder={placeholder}
        rows={6}
        className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm text-td-dark placeholder-td-muted resize-none focus:outline-none focus:ring-2 focus:ring-td-green/30 focus:border-td-green transition-colors font-mono-td leading-relaxed"
      />

      {error && <p className="text-td-fraud text-xs mt-2">{error}</p>}

      <button
        type="submit"
        disabled={loading || !content.trim()}
        className="mt-4 w-full bg-td-green hover:bg-td-green-dark disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors text-sm"
      >
        {loading ? "Analyzing…" : "Verify with TD"}
      </button>

      <p className="text-center text-td-muted text-xs mt-4">
        Your submission is analyzed by TD's AI fraud detection system. We never store identifying personal information.
      </p>
    </form>
  );
}
