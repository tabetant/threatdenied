"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Campaign } from "@/lib/api";
import CampaignBrief from "./CampaignBrief";

const SEVERITY_STYLES: Record<string, { dot: string; bg: string; text: string }> = {
  critical: { dot: "bg-red-500", bg: "bg-red-50", text: "text-red-700" },
  high:     { dot: "bg-orange-500", bg: "bg-orange-50", text: "text-orange-700" },
  medium:   { dot: "bg-amber-500", bg: "bg-amber-50", text: "text-amber-700" },
  low:      { dot: "bg-green-500", bg: "bg-green-50", text: "text-green-700" },
};

const VECTOR_ICONS: Record<string, string> = {
  sms: "SMS",
  email: "Email",
  url: "URL",
};

interface Props {
  campaigns: Campaign[];
}

export default function CampaignTable({ campaigns }: Props) {
  const [expanded, setExpanded] = useState<string | null>(null);

  return (
    <div className="border border-gray-200 rounded-2xl overflow-hidden">
      <div className="bg-gray-50 border-b border-gray-200 px-5 py-3">
        <h3 className="text-sm font-semibold text-td-dark">Active Campaigns</h3>
      </div>
      <div className="divide-y divide-gray-100">
        {campaigns.map((c) => {
          const sev = SEVERITY_STYLES[c.severity] ?? SEVERITY_STYLES.medium;
          const isOpen = expanded === c.id;

          return (
            <div key={c.id}>
              <button
                onClick={() => setExpanded(isOpen ? null : c.id)}
                className="w-full px-4 md:px-5 py-4 flex items-center gap-3 md:gap-4 hover:bg-gray-50 transition-colors text-left"
              >
                {/* Severity dot */}
                <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${sev.dot}`} />

                {/* Label + vector */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-td-dark truncate">{c.label}</p>
                  <p className="text-xs text-td-muted mt-0.5">
                    {VECTOR_ICONS[c.attack_vector] ?? c.attack_vector} &middot;{" "}
                    First seen {new Date(c.first_seen).toLocaleDateString()}
                  </p>
                </div>

                {/* Report count */}
                <div className="text-right flex-shrink-0">
                  <p className="text-lg font-bold text-td-dark">{c.report_count}</p>
                  <p className="text-xs text-td-muted">reports</p>
                </div>

                {/* Severity badge — hidden on small screens */}
                <span className={`hidden sm:inline-block text-xs font-medium px-2 py-1 rounded-full flex-shrink-0 ${sev.bg} ${sev.text}`}>
                  {c.severity}
                </span>

                {/* Chevron */}
                <svg
                  className={`w-4 h-4 text-td-muted transition-transform flex-shrink-0 ${isOpen ? "rotate-180" : ""}`}
                  fill="none" viewBox="0 0 24 24" stroke="currentColor"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Expanded detail */}
              <AnimatePresence>
                {isOpen && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-5 pb-5 space-y-3">
                      {/* Tactics summary */}
                      {c.tactics_summary && (
                        <div className="bg-gray-50 rounded-xl px-4 py-3">
                          <p className="text-xs font-medium text-td-muted uppercase tracking-wide mb-1">
                            Tactics
                          </p>
                          <p className="text-sm text-td-dark leading-relaxed">
                            {c.tactics_summary}
                          </p>
                        </div>
                      )}

                      {/* Customer alert */}
                      {c.customer_alert && (
                        <div className="bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
                          <p className="text-xs font-medium text-amber-700 uppercase tracking-wide mb-1">
                            Customer Alert
                          </p>
                          <p className="text-sm text-amber-900 leading-relaxed">
                            {c.customer_alert}
                          </p>
                        </div>
                      )}

                      {/* AI-generated brief */}
                      <CampaignBrief campaignId={c.id} />
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
        {campaigns.length === 0 && (
          <div className="px-5 py-8 text-center text-td-muted text-sm">
            No active campaigns detected.
          </div>
        )}
      </div>
    </div>
  );
}
