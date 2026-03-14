"use client";
import { motion } from "framer-motion";
import { UserProfile } from "@/lib/api";

interface Props {
  profile: UserProfile;
}

const TIERS = [
  { min: 0,   label: "Bronze",   color: "text-amber-600" },
  { min: 100, label: "Silver",   color: "text-gray-500"  },
  { min: 300, label: "Gold",     color: "text-yellow-500"},
  { min: 600, label: "Platinum", color: "text-td-green"  },
];

function getTier(points: number) {
  return [...TIERS].reverse().find((t) => points >= t.min) ?? TIERS[0];
}

export default function ScoreCard({ profile }: Props) {
  const tier = getTier(profile.reward_points);

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-td-green rounded-2xl px-6 py-6 text-white">
        <p className="text-white/70 text-sm mb-1">Welcome back,</p>
        <h2 className="text-2xl font-bold">{profile.name}</h2>
        <div className="flex items-center gap-3 mt-4">
          <div className="bg-white/20 rounded-xl px-4 py-2">
            <p className="text-white/70 text-xs">Reward Points</p>
            <p className="text-2xl font-bold">{profile.reward_points.toLocaleString()}</p>
          </div>
          <div className="bg-white/20 rounded-xl px-4 py-2">
            <p className="text-white/70 text-xs">Tier</p>
            <p className="text-2xl font-bold">{tier.label}</p>
          </div>
          <div className="bg-white/20 rounded-xl px-4 py-2">
            <p className="text-white/70 text-xs">Streak</p>
            <p className="text-2xl font-bold">{profile.current_streak} 🔥</p>
          </div>
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 gap-3">
        {[
          { label: "Tests Received",       value: profile.tests_sent },
          { label: "Correctly Flagged",     value: profile.tests_flagged_correctly },
          { label: "Real Reports Submitted",value: profile.real_submissions },
          { label: "Accuracy",              value: `${profile.accuracy_pct.toFixed(1)}%` },
        ].map(({ label, value }, i) => (
          <motion.div
            key={label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.07 }}
            className="border border-gray-200 rounded-xl px-4 py-4"
          >
            <p className="text-td-muted text-xs mb-1">{label}</p>
            <p className="text-2xl font-bold text-td-dark">{value}</p>
          </motion.div>
        ))}
      </div>

      {/* Accuracy bar */}
      <div className="border border-gray-200 rounded-xl px-5 py-4">
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-td-dark">Detection Accuracy</span>
          <span className="text-sm font-bold text-td-green">{profile.accuracy_pct.toFixed(1)}%</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${profile.accuracy_pct}%` }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="h-full bg-td-green rounded-full"
          />
        </div>
        <p className="text-xs text-td-muted mt-2">
          You've correctly identified {profile.tests_flagged_correctly} of {profile.tests_sent} test emails.
        </p>
      </div>
    </div>
  );
}
