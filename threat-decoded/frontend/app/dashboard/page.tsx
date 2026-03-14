"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import NavBar from "@/components/NavBar";
import CampaignTable from "@/components/CampaignTable";
import ThreatMap from "@/components/ThreatMap";
import TrendChart from "@/components/TrendChart";
import AlertPreview from "@/components/AlertPreview";
import {
  getDashboardStats, getDashboardTrends, getCampaigns,
  DashboardStats, TrendPoint, Campaign,
} from "@/lib/api";

function StatCard({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="border border-gray-200 rounded-xl px-5 py-4"
    >
      <p className="text-xs text-td-muted font-medium uppercase tracking-wide">{label}</p>
      <p className="text-2xl md:text-3xl font-bold text-td-dark mt-1 truncate">{value}</p>
      {sub && <p className="text-xs text-td-muted mt-1">{sub}</p>}
    </motion.div>
  );
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [trends, setTrends] = useState<TrendPoint[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([
      getDashboardStats(),
      getDashboardTrends(),
      getCampaigns(),
    ])
      .then(([s, t, c]) => {
        setStats(s);
        setTrends(t);
        setCampaigns(c);
      })
      .catch(() => setError("Failed to load dashboard. Make sure the backend is running."));
  }, []);

  if (error) {
    return (
      <>
        <NavBar />
        <main className="min-h-screen bg-white">
          <div className="max-w-6xl mx-auto px-6 py-20 text-center">
            <p className="text-td-fraud text-sm">{error}</p>
          </div>
        </main>
      </>
    );
  }

  if (!stats) {
    return (
      <>
        <NavBar />
        <main className="min-h-screen bg-white">
          <div className="max-w-6xl mx-auto px-6 py-20 text-center">
            <div className="flex items-center justify-center gap-2 text-td-muted text-sm">
              <div className="w-4 h-4 border-2 border-td-green border-t-transparent rounded-full animate-spin" />
              Loading dashboard&hellip;
            </div>
          </div>
        </main>
      </>
    );
  }

  return (
    <>
      <NavBar />
      <main className="min-h-screen bg-white">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 space-y-5 sm:space-y-6">
          {/* Header */}
          <div>
            <h1 className="text-2xl font-bold text-td-dark">Threat Intelligence Dashboard</h1>
            <p className="text-td-muted text-sm mt-1">
              Real-time fraud campaign monitoring for TD Bank
            </p>
          </div>

          {/* Stats bar */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-2 sm:gap-3">
            <StatCard
              label="Submissions Today"
              value={stats.total_submissions_today}
            />
            <StatCard
              label="Fraud Rate"
              value={`${Math.round(stats.fraud_rate * 100)}%`}
              sub={`${stats.total_submissions} total submissions`}
            />
            <StatCard
              label="Active Campaigns"
              value={stats.active_campaigns}
            />
            <StatCard
              label="Top Campaign"
              value={stats.top_campaign ?? "None"}
            />
          </div>

          {/* Two-column: Map + Trends */}
          <div className="grid lg:grid-cols-2 gap-4">
            <ThreatMap data={stats.geographic_data} />
            <TrendChart data={trends} />
          </div>

          {/* Campaign table */}
          <CampaignTable campaigns={campaigns} />

          {/* Alert preview for top campaign */}
          {campaigns.length > 0 && (
            <AlertPreview
              campaignId={campaigns[0].id}
              campaignLabel={campaigns[0].label}
            />
          )}
        </div>
      </main>
    </>
  );
}
