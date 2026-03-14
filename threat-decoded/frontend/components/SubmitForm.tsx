"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { SUBMISSION_KEY } from "@/lib/api";

const TABS = [
  { id: "sms",   label: "SMS / Text",    placeholder: "Paste the suspicious text message here\u2026" },
  { id: "email", label: "Email",         placeholder: "Paste the full email \u2014 subject, sender, and body\u2026" },
  { id: "url",   label: "URL",           placeholder: "Paste the suspicious link here\u2026" },
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
    <motion.form
      onSubmit={handleSubmit}
      className="w-full"
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
    >
      {/* Tabs */}
      <div className="flex border border-gray-200 rounded-xl overflow-hidden mb-4 bg-gray-50 relative">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => { setActiveTab(tab.id as "sms" | "email" | "url"); setContent(""); setError(""); }}
            className={`flex-1 py-2.5 text-sm font-medium transition-all relative z-10 ${
              activeTab === tab.id
                ? "text-td-green"
                : "text-td-muted hover:text-td-dark"
            }`}
          >
            {tab.label}
            {activeTab === tab.id && (
              <motion.div
                layoutId="tab-bg"
                className="absolute inset-0 bg-white shadow-sm rounded-lg m-0.5"
                style={{ zIndex: -1 }}
                transition={{ type: "spring", stiffness: 400, damping: 30 }}
              />
            )}
          </button>
        ))}
      </div>

      {/* Textarea */}
      <textarea
        value={content}
        onChange={(e) => { setContent(e.target.value); setError(""); }}
        placeholder={placeholder}
        rows={6}
        className="w-full border border-gray-200 rounded-xl px-4 py-3 text-sm text-td-dark placeholder-td-muted resize-none focus:outline-none focus:ring-2 focus:ring-td-green/30 focus:border-td-green transition-all font-mono leading-relaxed"
      />

      {error && (
        <motion.p
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-td-fraud text-xs mt-2"
        >
          {error}
        </motion.p>
      )}

      <motion.button
        type="submit"
        disabled={loading || !content.trim()}
        whileTap={{ scale: 0.98 }}
        className="mt-4 w-full bg-td-green hover:bg-td-green-dark disabled:opacity-40 disabled:cursor-not-allowed text-white font-semibold py-3 rounded-xl transition-colors text-sm"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
            Analyzing&hellip;
          </span>
        ) : (
          "Verify with TD"
        )}
      </motion.button>

      <p className="text-center text-td-muted text-xs mt-4">
        Your submission is analyzed by TD&apos;s AI fraud detection system. We never store identifying personal information.
      </p>
    </motion.form>
  );
}
