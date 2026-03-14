"use client";

import NavBar from "@/components/NavBar";
import ForensicStream from "@/components/ForensicStream";

export default function ScanPage({ params }: { params: { id: string } }) {
  const { id } = params;

  return (
    <>
      <NavBar />
      <main className="min-h-screen bg-white">
        <div className="max-w-2xl mx-auto px-4 sm:px-6 py-8 sm:py-12">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-td-dark mb-1">Forensic Analysis</h1>
            <p className="text-td-muted text-sm">
              Running checks against TD&apos;s fraud detection systems&hellip;
            </p>
          </div>
          <ForensicStream reportId={id} />
        </div>
      </main>
    </>
  );
}
