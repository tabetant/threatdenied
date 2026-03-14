"use client";
import { motion } from "framer-motion";

interface Props {
  campaignId: string;
  reportCount?: number | null;
  label?: string;
}

export default function CampaignBadge({ campaignId, reportCount, label }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center gap-2 bg-red-50 border border-red-200 rounded-lg px-4 py-3"
    >
      <span className="text-red-500 text-sm">⚑</span>
      <div>
        <p className="text-sm font-semibold text-red-700">
          {label ?? `Part of Campaign #${campaignId.slice(0, 6).toUpperCase()}`}
        </p>
        {reportCount != null && (
          <p className="text-xs text-red-500">
            {reportCount} TD customer{reportCount !== 1 ? "s" : ""} reported this
          </p>
        )}
      </div>
    </motion.div>
  );
}
