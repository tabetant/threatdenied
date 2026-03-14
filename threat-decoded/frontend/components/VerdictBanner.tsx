"use client";
import { motion } from "framer-motion";

interface Props {
  verdict: "fraud" | "legitimate" | "inconclusive";
  confidence: number;
}

const CONFIGS = {
  fraud: {
    bg: "bg-red-600",
    label: "FRAUD DETECTED",
    sub: "This message is not from TD Bank.",
    icon: "✕",
  },
  legitimate: {
    bg: "bg-td-green",
    label: "VERIFIED LEGITIMATE",
    sub: "This appears to be a genuine TD Bank communication.",
    icon: "✓",
  },
  inconclusive: {
    bg: "bg-amber-500",
    label: "INCONCLUSIVE",
    sub: "We couldn't make a definitive determination. Proceed with caution.",
    icon: "?",
  },
};

export default function VerdictBanner({ verdict, confidence }: Props) {
  const cfg = CONFIGS[verdict] ?? CONFIGS.inconclusive;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 20 }}
      className={`${cfg.bg} rounded-2xl px-8 py-8 text-white text-center shadow-lg`}
    >
      <motion.div
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, type: "spring", stiffness: 300, damping: 18 }}
        className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center mx-auto mb-4"
      >
        <span className="text-3xl font-bold">{cfg.icon}</span>
      </motion.div>
      <h2 className="text-3xl font-bold tracking-tight mb-1">{cfg.label}</h2>
      <p className="text-white/80 text-sm mb-4">{cfg.sub}</p>
      <div className="inline-flex items-center gap-2 bg-white/20 rounded-full px-4 py-1.5">
        <span className="text-xs font-medium text-white/70">Confidence</span>
        <span className="text-sm font-bold">{Math.round(confidence * 100)}%</span>
      </div>
    </motion.div>
  );
}
