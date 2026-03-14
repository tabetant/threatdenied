"use client";

import { motion } from "framer-motion";
import { GeoPoint } from "@/lib/api";

interface Props {
  data: GeoPoint[];
}

// Simplified Canada map bounds for positioning dots
const MAP_BOUNDS = {
  latMin: 42.0,
  latMax: 56.0,
  lngMin: -140.0,
  lngMax: -52.0,
};

function geoToPercent(lat: number, lng: number) {
  const x = ((lng - MAP_BOUNDS.lngMin) / (MAP_BOUNDS.lngMax - MAP_BOUNDS.lngMin)) * 100;
  const y = ((MAP_BOUNDS.latMax - lat) / (MAP_BOUNDS.latMax - MAP_BOUNDS.latMin)) * 100;
  return { x: Math.max(2, Math.min(98, x)), y: Math.max(2, Math.min(98, y)) };
}

export default function ThreatMap({ data }: Props) {
  const maxCount = Math.max(...data.map((d) => d.count), 1);

  return (
    <div className="border border-gray-200 rounded-2xl overflow-hidden">
      <div className="bg-gray-50 border-b border-gray-200 px-5 py-3 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-td-dark">Geographic Threat Radar</h3>
        <span className="text-xs text-td-muted">{data.length} locations</span>
      </div>
      <div className="relative bg-gray-900 h-56 md:h-64 lg:h-72 overflow-hidden">
        {/* Grid overlay */}
        <div className="absolute inset-0 opacity-10">
          {[...Array(10)].map((_, i) => (
            <div key={`h${i}`} className="absolute w-full border-t border-green-400" style={{ top: `${i * 10}%` }} />
          ))}
          {[...Array(10)].map((_, i) => (
            <div key={`v${i}`} className="absolute h-full border-l border-green-400" style={{ left: `${i * 10}%` }} />
          ))}
        </div>

        {/* Province label hints */}
        <span className="absolute text-[10px] text-green-700/40 font-mono" style={{ left: "18%", top: "55%" }}>BC</span>
        <span className="absolute text-[10px] text-green-700/40 font-mono" style={{ left: "28%", top: "50%" }}>AB</span>
        <span className="absolute text-[10px] text-green-700/40 font-mono" style={{ left: "38%", top: "48%" }}>SK</span>
        <span className="absolute text-[10px] text-green-700/40 font-mono" style={{ left: "48%", top: "46%" }}>MB</span>
        <span className="absolute text-[10px] text-green-700/40 font-mono" style={{ left: "62%", top: "58%" }}>ON</span>
        <span className="absolute text-[10px] text-green-700/40 font-mono" style={{ left: "78%", top: "52%" }}>QC</span>

        {/* Threat dots */}
        {data.map((point, i) => {
          const { x, y } = geoToPercent(point.lat, point.lng);
          const size = 8 + (point.count / maxCount) * 20;
          const opacity = 0.4 + (point.count / maxCount) * 0.6;

          return (
            <motion.div
              key={`${point.city}-${point.province}`}
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: i * 0.06, type: "spring", stiffness: 300 }}
              className="absolute group"
              style={{ left: `${x}%`, top: `${y}%`, transform: "translate(-50%, -50%)" }}
            >
              {/* Pulse ring */}
              <motion.div
                className="absolute rounded-full bg-red-500"
                style={{ width: size * 2, height: size * 2, left: -size / 2, top: -size / 2, opacity: opacity * 0.2 }}
                animate={{ scale: [1, 1.5, 1] }}
                transition={{ duration: 2, delay: i * 0.2, repeat: Infinity }}
              />
              {/* Dot */}
              <div
                className="rounded-full bg-red-500 border border-red-400 shadow-lg shadow-red-500/30"
                style={{ width: size, height: size, opacity }}
              />
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                <div className="bg-gray-800 text-white text-xs rounded-lg px-3 py-1.5 whitespace-nowrap shadow-lg">
                  <span className="font-medium">{point.city}, {point.province}</span>
                  <span className="text-gray-400 ml-1">&middot; {point.count} reports</span>
                </div>
              </div>
            </motion.div>
          );
        })}

        {data.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center text-green-700/40 text-sm">
            No geographic data available
          </div>
        )}
      </div>
    </div>
  );
}
