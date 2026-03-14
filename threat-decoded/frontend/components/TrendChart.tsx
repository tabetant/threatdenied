"use client";

import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from "recharts";
import { TrendPoint } from "@/lib/api";

interface Props {
  data: TrendPoint[];
}

export default function TrendChart({ data }: Props) {
  // Format dates for display
  const formatted = data.map((d) => ({
    ...d,
    label: new Date(d.date + "T00:00:00").toLocaleDateString("en-CA", { month: "short", day: "numeric" }),
  }));

  return (
    <div className="border border-gray-200 rounded-2xl overflow-hidden">
      <div className="bg-gray-50 border-b border-gray-200 px-5 py-3">
        <h3 className="text-sm font-semibold text-td-dark">Submission Trends (14 days)</h3>
      </div>
      <div className="px-4 py-4">
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={formatted} margin={{ top: 4, right: 8, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="fraudGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#DC2626" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#DC2626" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="legitGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#16A34A" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#16A34A" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="label" tick={{ fontSize: 11 }} stroke="#9CA3AF" />
            <YAxis tick={{ fontSize: 11 }} stroke="#9CA3AF" allowDecimals={false} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1A1A1A",
                border: "none",
                borderRadius: 8,
                fontSize: 12,
                color: "#fff",
              }}
            />
            <Legend
              wrapperStyle={{ fontSize: 12, paddingTop: 8 }}
              iconType="circle"
              iconSize={8}
            />
            <Area
              type="monotone"
              dataKey="fraud"
              name="Fraud"
              stroke="#DC2626"
              fill="url(#fraudGrad)"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="legitimate"
              name="Legitimate"
              stroke="#16A34A"
              fill="url(#legitGrad)"
              strokeWidth={2}
            />
            <Area
              type="monotone"
              dataKey="inconclusive"
              name="Inconclusive"
              stroke="#F59E0B"
              fill="transparent"
              strokeWidth={1.5}
              strokeDasharray="4 2"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
