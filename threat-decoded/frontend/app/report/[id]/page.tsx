"use client";

import { useEffect, useState } from "react";
import NavBar from "@/components/NavBar";
import VerdictBanner from "@/components/VerdictBanner";
import ForensicCard from "@/components/ForensicCard";
import CampaignBadge from "@/components/CampaignBadge";
import ChatPanel from "@/components/ChatPanel";
import { getReport, Report, ForensicEvent } from "@/lib/api";

export default function ReportPage({ params }: { params: { id: string } }) {
  const { id } = params;
  const [report, setReport] = useState<Report | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    getReport(id)
      .then(setReport)
      .catch(() => setError("Report not found. It may not have been created yet."));
  }, [id]);

  if (error) {
    return (
      <>
        <NavBar />
        <main className="min-h-screen bg-white">
          <div className="max-w-2xl mx-auto px-6 py-20 text-center">
            <p className="text-td-fraud text-sm">{error}</p>
          </div>
        </main>
      </>
    );
  }

  if (!report) {
    return (
      <>
        <NavBar />
        <main className="min-h-screen bg-white">
          <div className="max-w-2xl mx-auto px-6 py-20 text-center">
            <div className="flex items-center justify-center gap-2 text-td-muted text-sm">
              <div className="w-4 h-4 border-2 border-td-green border-t-transparent rounded-full animate-spin" />
              Loading report&hellip;
            </div>
          </div>
        </main>
      </>
    );
  }

  // Build forensic check cards from the stored results
  const checks: ForensicEvent[] = [
    report.sender_result,
    report.url_result,
    report.template_result,
    report.campaign_result,
  ].filter((c): c is ForensicEvent => c != null && typeof c === "object" && "check" in c);

  // content_ai_result is stored differently — it's the raw AI response, not a ForensicEvent
  // We'll display it as a card if it has the right shape
  if (
    report.content_ai_result &&
    typeof report.content_ai_result === "object" &&
    "check" in report.content_ai_result
  ) {
    checks.push(report.content_ai_result as unknown as ForensicEvent);
  }

  return (
    <>
      <NavBar />
      <main className="min-h-screen bg-white">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 sm:py-12 space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-bold text-td-dark mb-1">Verdict Report</h1>
            <p className="text-td-muted text-xs font-mono">{report.id}</p>
            <p className="text-td-muted text-xs mt-1">
              Submitted {new Date(report.submitted_at).toLocaleString()} &middot;{" "}
              <span className="capitalize">{report.type}</span>
            </p>
          </div>

          {/* Submitted content preview */}
          <div className="border border-gray-200 rounded-xl px-5 py-4 bg-gray-50">
            <p className="text-xs text-td-muted mb-2 font-medium uppercase tracking-wide">
              Submitted Content
            </p>
            <p className="text-sm text-td-dark font-mono leading-relaxed whitespace-pre-wrap break-words">
              {report.content}
            </p>
          </div>

          {/* Verdict banner */}
          {report.verdict && (
            <VerdictBanner
              verdict={report.verdict}
              confidence={report.confidence ?? 0}
            />
          )}

          {/* Campaign badge */}
          {report.campaign_id && <CampaignBadge campaignId={report.campaign_id} />}

          {/* Forensic check cards */}
          {checks.length > 0 && (
            <div>
              <h2 className="text-lg font-semibold text-td-dark mb-3">Forensic Checks</h2>
              <div className="space-y-2">
                {checks.map((check, i) => (
                  <ForensicCard key={check.check} event={check} index={i} />
                ))}
              </div>
            </div>
          )}

          {/* Chat panel */}
          <div>
            <h2 className="text-lg font-semibold text-td-dark mb-3">
              Questions about this verdict?
            </h2>
            <ChatPanel reportId={id} />
          </div>
        </div>
      </main>
    </>
  );
}
