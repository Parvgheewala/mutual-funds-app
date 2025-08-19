// NavGraph.jsx
import React from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

export default function NavGraph({ navHistory, multiLine = false, lineColors = [], fundCodes = [] }) {
  if (!navHistory || navHistory.length === 0) return <div>No data to display</div>;

  if (!multiLine) {
    // Single line chart
    const chartData = navHistory.map((item) => ({
      date: item.date,
      nav: parseFloat(item.nav),
    }));

    return (
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid stroke="#eee" strokeDasharray="5 5" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis domain={["auto", "auto"]} />
          <Tooltip />
          <Line type="monotone" dataKey="nav" stroke="#8884d8" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  // Multi-line chart
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart data={navHistory}>
        <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
        <XAxis dataKey="date" tick={{ fontSize: 12 }} />
        <YAxis domain={["auto", "auto"]} />
        <Tooltip />
        {fundCodes.map((code, idx) => (
          <Line
            key={code}
            type="monotone"
            dataKey={code}
            stroke={lineColors[idx] || "#8884d8"}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
