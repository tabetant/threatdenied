"use client";

import { useEffect, useState } from "react";
import { getCampaignBrief, CampaignBrief as CampaignBriefType } from "@/lib/api";

interface Props {
  campaignId: string;
}

export default function CampaignBrief({ campaignId }: Props) {
  const [brief, setBrief] = useState<CampaignBriefType | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    getCampaignBrief(campaignId)
      .then(setBrief)
      .catch(() => setError("Could not load AI brief."))
      .finally(() => setLoading(false));
  }, [campaignId]);

  if (loading) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3">
        <div className="flex items-center gap-2 text-blue-600 text-sm">
          <div className="w-3.5 h-3.5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
          Generating AI threat brief&hellip;
        </div>
      </div>
    );
  }

  if (error || !brief) return null;

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-xl px-4 py-3">
      <p className="text-xs font-medium text-blue-700 uppercase tracking-wide mb-1">
        AI Threat Brief
      </p>
      <p className="text-sm text-blue-900 leading-relaxed">{brief.ai_summary}</p>
      {brief.recommended_alert && (
        <div className="mt-2 pt-2 border-t border-blue-200">
          <p className="text-xs font-medium text-blue-700 mb-0.5">Recommended Alert</p>
          <p className="text-xs text-blue-800 leading-relaxed">{brief.recommended_alert}</p>
        </div>
      )}
    </div>
  );
}
