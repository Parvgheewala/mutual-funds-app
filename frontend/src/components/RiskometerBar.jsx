// components/RiskometerBar.jsx
import React, { useMemo } from "react";

const LEVELS = [
  "Very Low",
  "Low",
  "Moderate",
  "Moderately High",
  "High",
  "Very High",
];

// Pick colors from green (low) to red (very high)
const COLORS = {
  "Very Low": "#2e7d32",        // green
  "Low": "#558b2f",             // yellow-green
  "Moderate": "#f9a825",        // amber
  "Moderately High": "#fb8c00", // orange
  "High": "#e53935",            // red
  "Very High": "#b71c1c",       // dark red
};

export default function RiskometerBar({
  category,          // one of LEVELS
  showLabel = true,
  height = 12,
  radius = 999,
  disclaimer = "Computed risk based on historical data; not the official SEBI/AMFI Riskometer.",
  className = "",
}) {
  const idx = useMemo(() => {
    const i = LEVELS.indexOf(category);
    return i >= 0 ? i : 0;
  }, [category]);

  const color = COLORS[LEVELS[idx]];
  const percent = useMemo(() => ((idx + 1) / LEVELS.length) * 100, [idx]);

  return (
    <div className={className} style={{ maxWidth: 520 }}>
      {showLabel && (
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: 12,
            color: "#666",
            marginBottom: 6,
          }}
          aria-hidden
        >
          <span>Low</span>
          <span>Risk</span>
        </div>
      )}

      <div
        role="img"
        aria-label={`Risk category: ${LEVELS[idx]}`}
        style={{
          position: "relative",
          width: "100%",
          height,
          background:
            "linear-gradient(90deg, #2e7d32 0%, #558b2f 20%, #f9a825 40%, #fb8c00 60%, #e53935 80%, #b71c1c 100%)",
          borderRadius: radius,
          overflow: "hidden",
        }}
      >
        {/* Fill overlay to indicate selected level */}
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            height: "100%",
            width: `${percent}%`,
            backgroundColor: color,
            opacity: 0.35,
          }}
        />
        {/* Marker dot */}
        <div
          title={LEVELS[idx]}
          style={{
            position: "absolute",
            left: `calc(${percent}% - 6px)`,
            top: -3,
            width: 18,
            height: height + 6,
            borderRadius: radius,
            border: "2px solid rgba(0,0,0,0.25)",
            boxShadow: "0 0 0 2px rgba(255,255,255,0.9) inset",
          }}
        />
      </div>

      {/* Legend under bar */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          fontSize: 11,
          marginTop: 6,
          color: "#444",
        }}
      >
        {LEVELS.map((lvl) => (
          <span
            key={lvl}
            style={{
              color: lvl === LEVELS[idx] ? color : "#777",
              fontWeight: lvl === LEVELS[idx] ? 600 : 400,
              whiteSpace: "nowrap",
            }}
          >
            {lvl}
          </span>
        ))}
      </div>

      {/* Disclaimer */}
      <p
        style={{
          marginTop: 8,
          fontSize: 11,
          lineHeight: 1.3,
          color: "#666",
        }}
      >
        {disclaimer}
      </p>
    </div>
  );
}
