"use client";

import { motion } from "framer-motion";
import { FlagResult } from "@/lib/api";

interface Props {
  result: FlagResult;
  onDismiss: () => void;
}

export default function TrainingFeedback({ result, onDismiss }: Props) {
  const correct = result.correct;
  const feedback = result.feedback;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="border rounded-2xl overflow-hidden"
      style={{ borderColor: correct ? "#16A34A" : "#DC2626" }}
    >
      {/* Header */}
      <div className={`px-5 py-4 text-white ${correct ? "bg-td-legit" : "bg-td-fraud"}`}>
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
            <span className="text-xl font-bold">{correct ? "\u2713" : "\u2717"}</span>
          </div>
          <div>
            <p className="font-bold text-lg">
              {correct ? "Correct!" : "Not quite"}
            </p>
            <p className="text-white/80 text-sm">
              {result.points_delta > 0
                ? `+${result.points_delta} points`
                : result.points_delta < 0
                ? `${result.points_delta} points`
                : "0 points"}
              {" \u00B7 "}
              Streak: {result.new_streak}
            </p>
          </div>
        </div>
      </div>

      {/* Explanation */}
      <div className="px-5 py-4 space-y-4">
        {feedback.explanation && (
          <p className="text-sm text-td-dark leading-relaxed">{feedback.explanation}</p>
        )}

        {feedback.tips && feedback.tips.length > 0 && (
          <div>
            <p className="text-xs font-semibold text-td-muted uppercase tracking-wide mb-2">
              Tips for next time
            </p>
            <ul className="space-y-1.5">
              {feedback.tips.map((tip, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-td-dark">
                  <span className="text-td-green font-bold mt-0.5">&bull;</span>
                  {tip}
                </li>
              ))}
            </ul>
          </div>
        )}

        {feedback.encouragement_message && (
          <p className="text-sm text-td-muted italic">{feedback.encouragement_message}</p>
        )}

        <div className="flex items-center justify-between pt-2">
          <p className="text-xs text-td-muted">
            Total: {result.new_points} pts &middot; Accuracy: {result.accuracy_pct}%
          </p>
          <button
            onClick={onDismiss}
            className="text-sm text-td-green font-medium hover:underline"
          >
            Got it
          </button>
        </div>
      </div>
    </motion.div>
  );
}
