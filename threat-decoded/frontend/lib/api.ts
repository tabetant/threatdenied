// All API calls go through Next.js rewrites → http://localhost:8000
const BASE = "/api";

export interface ForensicEvent {
  check: "sender" | "url" | "content_ai" | "template" | "campaign" | "verdict";
  status: string;
  title?: string;
  detail?: string;
  score?: number | null;
  metadata?: Record<string, unknown>;
  // verdict-only fields
  confidence?: number;
  report_id?: string;
  campaign_id?: string | null;
  campaign_report_count?: number | null;
}

export interface Report {
  id: string;
  type: string;
  content: string;
  verdict: "fraud" | "legitimate" | "inconclusive" | null;
  confidence: number | null;
  sender_result: ForensicEvent | null;
  url_result: ForensicEvent | null;
  content_ai_result: Record<string, unknown> | null;
  template_result: ForensicEvent | null;
  campaign_result: ForensicEvent | null;
  campaign_id: string | null;
  submitted_at: string;
}

export interface Campaign {
  id: string;
  label: string;
  attack_vector: string;
  severity: string;
  report_count: number;
  first_seen: string;
  last_seen: string;
  is_active: boolean;
  tactics_summary: string | null;
  customer_alert: string | null;
}

export interface UserProfile {
  id: string;
  email: string;
  name: string;
  reward_points: number;
  current_streak: number;
  tests_sent: number;
  tests_flagged_correctly: number;
  real_submissions: number;
  accuracy_pct: number;
}

export async function getReport(id: string): Promise<Report> {
  const res = await fetch(`${BASE}/report/${id}`);
  if (!res.ok) throw new Error("Report not found");
  return res.json();
}

export async function getProfile(userId: string): Promise<UserProfile> {
  const res = await fetch(`${BASE}/profile/${userId}`);
  if (!res.ok) throw new Error("Profile not found");
  return res.json();
}

export async function getCampaigns(): Promise<Campaign[]> {
  const res = await fetch(`${BASE}/campaigns`);
  if (!res.ok) throw new Error("Failed to load campaigns");
  return res.json();
}

export async function sendChat(
  reportId: string,
  message: string,
  history: { role: string; content: string }[]
): Promise<{ response: string; suggested_followups: string[] }> {
  const res = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ report_id: reportId, message, history }),
  });
  if (!res.ok) throw new Error("Chat failed");
  return res.json();
}

export const SUBMISSION_KEY = (id: string) => `td_submission_${id}`;
