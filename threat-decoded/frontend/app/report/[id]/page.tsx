"use client";

export default function ReportPage({ params }: { params: { id: string } }) {
  return (
    <main className="min-h-screen bg-white">
      <div className="max-w-2xl mx-auto px-6 py-20">
        <h1 className="text-2xl font-semibold text-td-dark mb-2">Verdict Report</h1>
        <p className="text-td-muted text-sm font-mono-td">{params.id}</p>
        <p className="mt-8 text-td-muted text-sm">[VerdictBanner + ForensicCard + ChatPanel — Phase 3]</p>
      </div>
    </main>
  );
}
