"use client";
import { useEffect, useState, useRef } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import ForensicCard from "./ForensicCard";
import VerdictBanner from "./VerdictBanner";
import CampaignBadge from "./CampaignBadge";
import { ForensicEvent, SUBMISSION_KEY } from "@/lib/api";

const CHECK_LABELS: Record<string, string> = {
  sender:     "Verifying sender identity…",
  url:        "Scanning URLs and domains…",
  template:   "Matching TD communication templates…",
  campaign:   "Checking fraud campaign database…",
  content_ai: "Running AI content analysis…",
  verdict:    "Calculating verdict…",
};

interface Props {
  reportId: string;
}

export default function ForensicStream({ reportId }: Props) {
  const router = useRouter();
  const [checks, setChecks] = useState<ForensicEvent[]>([]);
  const [verdict, setVerdict] = useState<ForensicEvent | null>(null);
  const [scanning, setScanning] = useState<string>("Initializing analysis…");
  const [error, setError] = useState("");
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    const stored = sessionStorage.getItem(SUBMISSION_KEY(reportId));
    if (!stored) {
      setError("Submission not found. Please go back and try again.");
      return;
    }
    const { type, content } = JSON.parse(stored);

    async function stream() {
      try {
        const res = await fetch("/api/analyze", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ type, content, report_id: reportId }),
        });

        if (!res.ok || !res.body) {
          setError("Analysis failed. Please try again.");
          return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          for (const line of lines) {
            if (!line.startsWith("data: ")) continue;
            try {
              const event: ForensicEvent = JSON.parse(line.slice(6));

              if (event.check === "verdict") {
                setScanning("Done.");
                setVerdict(event);
                // Clean up sessionStorage after analysis is complete
                sessionStorage.removeItem(SUBMISSION_KEY(reportId));
              } else {
                setScanning(CHECK_LABELS[event.check] ?? "Analyzing…");
                setChecks((prev) => [...prev, event]);
              }
            } catch {
              // malformed line — skip
            }
          }
        }
      } catch (err) {
        setError("Connection error. Please try again.");
      }
    }

    stream();
  }, [reportId]);

  if (error) {
    return (
      <div className="text-center py-16">
        <p className="text-td-fraud text-sm">{error}</p>
        <button onClick={() => router.push("/")} className="mt-4 text-td-green text-sm underline">
          Back to submission
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {/* Live status indicator */}
      <AnimatePresence>
        {!verdict && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-3 py-2"
          >
            <div className="flex gap-1">
              {[0, 1, 2].map((i) => (
                <motion.div
                  key={i}
                  className="w-1.5 h-1.5 rounded-full bg-td-green"
                  animate={{ scale: [1, 1.4, 1], opacity: [0.4, 1, 0.4] }}
                  transition={{ duration: 1, delay: i * 0.2, repeat: Infinity }}
                />
              ))}
            </div>
            <span className="text-sm text-td-muted">{scanning}</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Forensic check cards */}
      <div className="space-y-2">
        {checks.map((check, i) => (
          <ForensicCard key={check.check} event={check} index={i} />
        ))}
      </div>

      {/* Verdict */}
      {verdict && (
        <div className="space-y-3 pt-2">
          <VerdictBanner
            verdict={verdict.status as "fraud" | "legitimate" | "inconclusive"}
            confidence={verdict.confidence ?? 0}
          />
          {verdict.campaign_id && (
            <CampaignBadge
              campaignId={verdict.campaign_id}
              reportCount={verdict.campaign_report_count}
            />
          )}
          <div className="pt-2 flex gap-3">
            <button
              onClick={() => router.push(`/report/${reportId}`)}
              className="flex-1 bg-td-green hover:bg-td-green-dark text-white font-semibold py-3 rounded-xl text-sm transition-colors"
            >
              View full report & ask follow-up questions
            </button>
            <button
              onClick={() => router.push("/")}
              className="px-5 border border-gray-200 text-td-muted hover:text-td-dark rounded-xl text-sm transition-colors"
            >
              New submission
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
