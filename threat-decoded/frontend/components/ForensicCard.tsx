"use client";
import { motion } from "framer-motion";
import { ForensicEvent } from "@/lib/api";

const STATUS_CONFIG: Record<string, { color: string; bg: string; icon: string; label: string }> = {
  pass:    { color: "text-td-legit",   bg: "bg-green-50  border-green-200",  icon: "✓", label: "Pass"    },
  fail:    { color: "text-td-fraud",   bg: "bg-red-50    border-red-200",    icon: "✕", label: "Fail"    },
  warning: { color: "text-td-warning", bg: "bg-amber-50  border-amber-200",  icon: "⚠", label: "Warning" },
  info:    { color: "text-td-muted",   bg: "bg-gray-50   border-gray-200",   icon: "·", label: "Info"    },
};

interface Props {
  event: ForensicEvent;
  index: number;
}

export default function ForensicCard({ event, index }: Props) {
  const cfg = STATUS_CONFIG[event.status] ?? STATUS_CONFIG.info;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: index * 0.05 }}
      className={`rounded-xl border px-5 py-4 ${cfg.bg}`}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-3 min-w-0">
          <span className={`text-lg font-bold ${cfg.color} flex-shrink-0`}>
            {cfg.icon}
          </span>
          <div className="min-w-0">
            <p className="text-sm font-semibold text-td-dark">{event.title}</p>
            <p className="text-sm text-td-muted mt-0.5 leading-snug">{event.detail}</p>
          </div>
        </div>
        {event.score != null && (
          <div className="flex-shrink-0 text-right">
            <span className={`text-xs font-semibold ${cfg.color}`}>
              {cfg.label}
            </span>
            <div className="w-16 h-1.5 bg-gray-200 rounded-full mt-1 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${Math.round(event.score * 100)}%` }}
                transition={{ duration: 0.5, delay: index * 0.05 + 0.2 }}
                className={`h-full rounded-full ${
                  event.status === "pass" ? "bg-td-legit" :
                  event.status === "fail" ? "bg-td-fraud" :
                  event.status === "warning" ? "bg-td-warning" : "bg-gray-400"
                }`}
              />
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
}
