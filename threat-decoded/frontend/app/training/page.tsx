"use client";

import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import NavBar from "@/components/NavBar";
import TrainingFeedback from "@/components/TrainingFeedback";
import {
  getTestEmails, flagTestEmail, generateTestEmails,
  TestEmailSummary, FlagResult,
} from "@/lib/api";

const DEMO_USER_ID = "demo-user-1";

const DIFFICULTY_COLORS: Record<string, string> = {
  easy: "bg-green-100 text-green-700",
  medium: "bg-amber-100 text-amber-700",
  hard: "bg-red-100 text-red-700",
};

export default function TrainingPage() {
  const [emails, setEmails] = useState<TestEmailSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [flagging, setFlagging] = useState<string | null>(null);
  const [flagResults, setFlagResults] = useState<Record<string, FlagResult>>({});

  useEffect(() => {
    getTestEmails(DEMO_USER_ID)
      .then(setEmails)
      .catch(() => setError("Failed to load test emails. Make sure the backend is running and seeded."))
      .finally(() => setLoading(false));
  }, []);

  async function handleFlag(emailId: string, flaggedAsPhishing: boolean) {
    setFlagging(emailId);
    try {
      const result = await flagTestEmail(emailId, flaggedAsPhishing);
      setFlagResults((prev) => ({ ...prev, [emailId]: result }));
      // Update the email's was_flagged status locally
      setEmails((prev) =>
        prev.map((e) =>
          e.id === emailId ? { ...e, was_flagged: flaggedAsPhishing } : e
        )
      );
      setExpandedId(emailId);
    } catch {
      setError("Failed to submit flag. Please try again.");
    } finally {
      setFlagging(null);
    }
  }

  async function handleGenerate() {
    setGenerating(true);
    setError("");
    try {
      await generateTestEmails(DEMO_USER_ID, 3, "medium");
      // Refresh the list
      const updated = await getTestEmails(DEMO_USER_ID);
      setEmails(updated);
    } catch {
      setError("Failed to generate test emails. Check your API key.");
    } finally {
      setGenerating(false);
    }
  }

  if (loading) {
    return (
      <>
        <NavBar />
        <main className="min-h-screen bg-white">
          <div className="max-w-2xl mx-auto px-6 py-20 text-center">
            <div className="flex items-center justify-center gap-2 text-td-muted text-sm">
              <div className="w-4 h-4 border-2 border-td-green border-t-transparent rounded-full animate-spin" />
              Loading training emails&hellip;
            </div>
          </div>
        </main>
      </>
    );
  }

  const pending = emails.filter((e) => e.was_flagged === null);
  const reviewed = emails.filter((e) => e.was_flagged !== null);

  return (
    <>
      <NavBar />
      <main className="min-h-screen bg-white">
        <div className="max-w-2xl mx-auto px-6 py-8 space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-td-dark">Phishing Training</h1>
              <p className="text-td-muted text-sm mt-1">
                Can you spot the fakes? Review each email and decide: phishing or legitimate.
              </p>
            </div>
            <button
              onClick={handleGenerate}
              disabled={generating}
              className="bg-td-green hover:bg-td-green-dark disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors flex items-center gap-2"
            >
              {generating && (
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              )}
              {generating ? "Generating..." : "New Test Emails"}
            </button>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg px-4 py-3 text-sm text-red-700">
              {error}
            </div>
          )}

          {/* Pending emails */}
          {pending.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-td-muted uppercase tracking-wide">
                Pending Review ({pending.length})
              </h2>
              {pending.map((email) => (
                <EmailCard
                  key={email.id}
                  email={email}
                  expanded={expandedId === email.id}
                  onToggle={() => setExpandedId(expandedId === email.id ? null : email.id)}
                  onFlag={handleFlag}
                  flagging={flagging === email.id}
                  flagResult={flagResults[email.id]}
                  onDismissFeedback={() => setExpandedId(null)}
                />
              ))}
            </div>
          )}

          {pending.length === 0 && emails.length > 0 && (
            <div className="text-center py-8 border border-dashed border-gray-200 rounded-xl">
              <p className="text-td-muted text-sm">All caught up! Click &quot;New Test Emails&quot; to generate more.</p>
            </div>
          )}

          {/* Reviewed emails */}
          {reviewed.length > 0 && (
            <div className="space-y-3">
              <h2 className="text-sm font-semibold text-td-muted uppercase tracking-wide">
                Previously Reviewed ({reviewed.length})
              </h2>
              {reviewed.map((email) => (
                <EmailCard
                  key={email.id}
                  email={email}
                  expanded={expandedId === email.id}
                  onToggle={() => setExpandedId(expandedId === email.id ? null : email.id)}
                  onFlag={handleFlag}
                  flagging={false}
                  flagResult={flagResults[email.id]}
                  onDismissFeedback={() => setExpandedId(null)}
                />
              ))}
            </div>
          )}
        </div>
      </main>
    </>
  );
}

// ── Email Card ─────────────────────────────────────────────────────────────

interface EmailCardProps {
  email: TestEmailSummary;
  expanded: boolean;
  onToggle: () => void;
  onFlag: (id: string, flaggedAsPhishing: boolean) => void;
  flagging: boolean;
  flagResult?: FlagResult;
  onDismissFeedback: () => void;
}

function EmailCard({ email, expanded, onToggle, onFlag, flagging, flagResult, onDismissFeedback }: EmailCardProps) {
  const isPending = email.was_flagged === null;
  const wasCorrect = email.ai_feedback
    ? (email.type === "phishing") === email.was_flagged
    : undefined;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="border border-gray-200 rounded-xl overflow-hidden"
    >
      {/* Email header — clickable to expand */}
      <button
        onClick={onToggle}
        className="w-full px-5 py-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="min-w-0 flex-1">
            <p className="text-xs text-td-muted font-mono">{email.from_address}</p>
            <p className="text-sm font-semibold text-td-dark mt-0.5 truncate">{email.subject}</p>
            <p className="text-xs text-td-muted mt-1 line-clamp-1">{email.body}</p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {!isPending && wasCorrect !== undefined && (
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                wasCorrect ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
              }`}>
                {wasCorrect ? "Correct" : "Missed"}
              </span>
            )}
            <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${
              DIFFICULTY_COLORS[email.difficulty] || "bg-gray-100 text-gray-600"
            }`}>
              {email.difficulty}
            </span>
          </div>
        </div>
      </button>

      {/* Expanded content */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 pb-4 space-y-4 border-t border-gray-100 pt-4">
              {/* Full email body */}
              <div className="bg-gray-50 rounded-lg px-4 py-3">
                <p className="text-xs text-td-muted font-medium mb-1">From: {email.from_address}</p>
                <p className="text-xs text-td-muted font-medium mb-2">Subject: {email.subject}</p>
                <p className="text-sm text-td-dark whitespace-pre-wrap leading-relaxed font-mono">
                  {email.body}
                </p>
              </div>

              {/* Action buttons (only for pending) */}
              {isPending && !flagResult && (
                <div className="flex gap-3">
                  <button
                    onClick={() => onFlag(email.id, true)}
                    disabled={flagging}
                    className="flex-1 border-2 border-red-200 text-red-600 hover:bg-red-50 disabled:opacity-50 font-medium py-2.5 rounded-xl text-sm transition-colors"
                  >
                    {flagging ? "Analyzing..." : "Report as Phishing"}
                  </button>
                  <button
                    onClick={() => onFlag(email.id, false)}
                    disabled={flagging}
                    className="flex-1 border-2 border-green-200 text-green-600 hover:bg-green-50 disabled:opacity-50 font-medium py-2.5 rounded-xl text-sm transition-colors"
                  >
                    {flagging ? "Analyzing..." : "Mark as Legitimate"}
                  </button>
                </div>
              )}

              {/* Flag result / training feedback */}
              {flagResult && (
                <TrainingFeedback result={flagResult} onDismiss={onDismissFeedback} />
              )}

              {/* Previously cached feedback (for reviewed emails) */}
              {!flagResult && !isPending && email.ai_feedback && (
                <div className="border border-gray-200 rounded-xl px-4 py-3 space-y-2">
                  <p className="text-xs font-semibold text-td-muted uppercase tracking-wide">AI Feedback</p>
                  <p className="text-sm text-td-dark leading-relaxed">{email.ai_feedback.explanation}</p>
                  {email.ai_feedback.tips && (
                    <ul className="space-y-1">
                      {email.ai_feedback.tips.map((tip, i) => (
                        <li key={i} className="text-sm text-td-muted flex items-start gap-2">
                          <span className="text-td-green">&bull;</span> {tip}
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
