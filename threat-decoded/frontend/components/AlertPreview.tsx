"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { getCampaignBrief, CampaignBrief } from "@/lib/api";

interface Props {
  campaignId: string;
  campaignLabel: string;
}

export default function AlertPreview({ campaignId, campaignLabel }: Props) {
  const [brief, setBrief] = useState<CampaignBrief | null>(null);
  const [loading, setLoading] = useState(true);
  const [sent, setSent] = useState(false);

  useEffect(() => {
    getCampaignBrief(campaignId)
      .then(setBrief)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [campaignId]);

  if (loading) {
    return (
      <div className="border border-gray-200 rounded-2xl px-5 py-6 text-center">
        <div className="flex items-center justify-center gap-2 text-td-muted text-sm">
          <div className="w-4 h-4 border-2 border-td-green border-t-transparent rounded-full animate-spin" />
          Generating alert preview&hellip;
        </div>
      </div>
    );
  }

  if (!brief) return null;

  const severityColor =
    brief.severity === "critical" ? "bg-red-100 text-red-700 border-red-200" :
    brief.severity === "high" ? "bg-amber-100 text-amber-700 border-amber-200" :
    "bg-gray-100 text-gray-600 border-gray-200";

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="border border-amber-200 rounded-2xl overflow-hidden bg-amber-50"
    >
      <div className="px-5 py-3 border-b border-amber-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-amber-600 text-sm">&#9888;</span>
          <span className="text-sm font-semibold text-amber-800">Customer Alert Preview</span>
        </div>
        <span className={`text-xs font-medium px-2 py-0.5 rounded-full border ${severityColor}`}>
          {brief.severity.toUpperCase()}
        </span>
      </div>

      <div className="px-5 py-4 space-y-3">
        <p className="text-xs text-amber-600 font-medium">{campaignLabel}</p>
        <p className="text-sm text-td-dark leading-relaxed">{brief.recommended_alert}</p>

        <div className="flex items-center gap-3 pt-2">
          {sent ? (
            <div className="flex items-center gap-2 text-td-legit text-sm font-medium">
              <span>&#10003;</span> Alert queued for distribution
            </div>
          ) : (
            <button
              onClick={() => setSent(true)}
              className="bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              Approve &amp; Send to Customers
            </button>
          )}
          <button className="text-sm text-td-muted hover:text-td-dark transition-colors">
            Edit draft
          </button>
        </div>
      </div>
    </motion.div>
  );
}
