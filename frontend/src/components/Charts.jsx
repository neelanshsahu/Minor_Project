import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  LineChart, Line, PieChart, Pie, Cell, ResponsiveContainer,
  AreaChart, Area, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from 'recharts';

const COLORS = ['#1A7A8A', '#52B788', '#A8DADC', '#2494A6', '#6ECF9E', '#7CC0C3'];

/**
 * Custom tooltip matching the ocean-dawn theme.
 */
const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload) return null;
  return (
    <div className="glass-card p-3 text-sm" style={{ border: '1px solid rgba(168,218,220,0.25)' }}>
      <p className="text-seafoam font-medium mb-1">{label}</p>
      {payload.map((e, i) => (
        <p key={i} style={{ color: e.color }} className="text-xs">
          {e.name}:{' '}
          <span className="font-semibold">
            {typeof e.value === 'number' ? e.value.toFixed(2) : e.value}
          </span>
        </p>
      ))}
    </div>
  );
};

/**
 * AggregateBarChart — Displays aggregate computation results as bars.
 * Used on Dashboard and Results pages.
 */
export const AggregateBarChart = ({ data, title, dataKey = 'value', nameKey = 'name' }) => (
  <div className="glass-card p-5">
    <h3 className="font-heading text-lg text-seafoam mb-4">{title}</h3>
    <ResponsiveContainer width="100%" height={280}>
      <BarChart data={data} barSize={40}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(168,218,220,0.08)" />
        <XAxis dataKey={nameKey} tick={{ fill: '#A8DADC', fontSize: 12 }} axisLine={{ stroke: 'rgba(168,218,220,0.1)' }} />
        <YAxis tick={{ fill: '#A8DADC', fontSize: 12 }} axisLine={{ stroke: 'rgba(168,218,220,0.1)' }} />
        <Tooltip content={<CustomTooltip />} />
        <Bar dataKey={dataKey} radius={[8, 8, 0, 0]}>
          {(data || []).map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
    <p className="text-xs text-seafoam/30 mt-2 text-center">
      ⚠️ Aggregated data only — individual records never revealed
    </p>
  </div>
);

/**
 * PerformanceLineChart — Multi-line chart for performance benchmarks.
 */
export const PerformanceLineChart = ({ data, title, lines = [] }) => (
  <div className="glass-card p-5">
    <h3 className="font-heading text-lg text-seafoam mb-4">{title}</h3>
    <ResponsiveContainer width="100%" height={280}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(168,218,220,0.08)" />
        <XAxis dataKey="name" tick={{ fill: '#A8DADC', fontSize: 12 }} axisLine={{ stroke: 'rgba(168,218,220,0.1)' }} />
        <YAxis tick={{ fill: '#A8DADC', fontSize: 12 }} axisLine={{ stroke: 'rgba(168,218,220,0.1)' }} />
        <Tooltip content={<CustomTooltip />} />
        <Legend wrapperStyle={{ fontSize: '12px', color: '#A8DADC' }} />
        {lines.map((line, i) => (
          <Line
            key={line.key}
            type="monotone"
            dataKey={line.key}
            stroke={COLORS[i % COLORS.length]}
            strokeWidth={2}
            dot={{ r: 4, fill: COLORS[i % COLORS.length], strokeWidth: 2, stroke: '#051E28' }}
            activeDot={{ r: 6, fill: COLORS[i % COLORS.length], stroke: '#fff', strokeWidth: 2 }}
            name={line.label}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  </div>
);

/**
 * DiagnosisDistributionChart — Donut chart for diagnosis distribution.
 */
export const DiagnosisDistributionChart = ({ data, title }) => (
  <div className="glass-card p-5">
    <h3 className="font-heading text-lg text-seafoam mb-4">{title}</h3>
    <ResponsiveContainer width="100%" height={280}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          outerRadius={100}
          innerRadius={55}
          dataKey="value"
          nameKey="name"
          strokeWidth={2}
          stroke="#051E28"
        >
          {(data || []).map((_, i) => (
            <Cell key={i} fill={COLORS[i % COLORS.length]} />
          ))}
        </Pie>
        <Tooltip content={<CustomTooltip />} />
      </PieChart>
    </ResponsiveContainer>
  </div>
);

/**
 * BenchmarkAreaChart — Gradient-filled area chart for trend data.
 */
export const BenchmarkAreaChart = ({ data, title, dataKey = 'time_ms' }) => (
  <div className="glass-card p-5">
    <h3 className="font-heading text-lg text-seafoam mb-4">{title}</h3>
    <ResponsiveContainer width="100%" height={250}>
      <AreaChart data={data}>
        <defs>
          <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#1A7A8A" stopOpacity={0.4} />
            <stop offset="95%" stopColor="#1A7A8A" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(168,218,220,0.08)" />
        <XAxis dataKey="name" tick={{ fill: '#A8DADC', fontSize: 12 }} axisLine={{ stroke: 'rgba(168,218,220,0.1)' }} />
        <YAxis tick={{ fill: '#A8DADC', fontSize: 12 }} axisLine={{ stroke: 'rgba(168,218,220,0.1)' }} />
        <Tooltip content={<CustomTooltip />} />
        <Area type="monotone" dataKey={dataKey} stroke="#1A7A8A" fill="url(#areaGrad)" strokeWidth={2} />
      </AreaChart>
    </ResponsiveContainer>
  </div>
);

/**
 * SecurityRadarChart — Radar visualization for security metrics.
 */
export const SecurityRadarChart = ({ data, title }) => (
  <div className="glass-card p-5">
    <h3 className="font-heading text-lg text-seafoam mb-4">{title}</h3>
    <ResponsiveContainer width="100%" height={280}>
      <RadarChart data={data}>
        <PolarGrid stroke="rgba(168,218,220,0.15)" />
        <PolarAngleAxis dataKey="metric" tick={{ fill: '#A8DADC', fontSize: 11 }} />
        <PolarRadiusAxis tick={{ fill: '#A8DADC', fontSize: 10 }} angle={30} />
        <Radar
          name="Score"
          dataKey="value"
          stroke="#52B788"
          fill="#52B788"
          fillOpacity={0.2}
          strokeWidth={2}
        />
      </RadarChart>
    </ResponsiveContainer>
  </div>
);
