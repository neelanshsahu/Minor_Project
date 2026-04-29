import React, { useState, useEffect, useRef } from 'react';
import WaveBackground from '../components/WaveBackground';
import { getAuditLog } from '../api/client';

/**
 * Event type styling — maps event names to visual styles.
 */
const EVENT_STYLES = {
  SESSION_INITIALIZED:    { bg: 'bg-teal/10',         border: 'border-teal/20',         text: 'text-teal-light',   icon: '🔧', label: 'Session Init' },
  SHARES_UPLOADED:        { bg: 'bg-calm-green/10',    border: 'border-calm-green/20',   text: 'text-calm-green',   icon: '📤', label: 'Shares Uploaded' },
  AGGREGATION_COMPUTED:   { bg: 'bg-seafoam/10',       border: 'border-seafoam/20',      text: 'text-seafoam',      icon: '🧮', label: 'Aggregation' },
  PROTOCOL_SIMULATED:     { bg: 'bg-purple-500/10',    border: 'border-purple-500/20',   text: 'text-purple-300',   icon: '🎭', label: 'Protocol Sim' },
  ZKP_GENERATED:          { bg: 'bg-yellow-500/10',    border: 'border-yellow-500/20',   text: 'text-yellow-300',   icon: '🛡️', label: 'ZKP Generated' },
  ZKP_VERIFIED:           { bg: 'bg-green-500/10',     border: 'border-green-500/20',    text: 'text-green-300',    icon: '✅', label: 'ZKP Verified' },
  GARBLED_CIRCUIT_EVALUATED: { bg: 'bg-cyan-500/10',   border: 'border-cyan-500/20',     text: 'text-cyan-300',     icon: '⚡', label: 'Garbled Circuit' },
  BENCHMARK_STARTED:      { bg: 'bg-orange-500/10',    border: 'border-orange-500/20',   text: 'text-orange-300',   icon: '⏱️', label: 'Benchmark Start' },
  BENCHMARK_COMPLETED:    { bg: 'bg-blue-500/10',      border: 'border-blue-500/20',     text: 'text-blue-300',     icon: '📊', label: 'Benchmark Done' },
};
const DEFAULT_STYLE = { bg: 'bg-ocean-deep/30', border: 'border-seafoam/10', text: 'text-seafoam/60', icon: '📋', label: 'Event' };

const Audit = () => {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const intervalRef = useRef(null);

  const fetchLog = async () => {
    setLoading(true);
    try {
      const data = await getAuditLog(null, 200);
      setEvents(data.events || []);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchLog();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      intervalRef.current = setInterval(fetchLog, 3000);
    }
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [autoRefresh]);

  // Filter and search
  const filtered = events
    .filter((e) => filter === 'all' || e.event === filter)
    .filter((e) => {
      if (!searchTerm) return true;
      const term = searchTerm.toLowerCase();
      return (
        e.event?.toLowerCase().includes(term) ||
        e.session_id?.toLowerCase().includes(term) ||
        JSON.stringify(e.details || {}).toLowerCase().includes(term)
      );
    });

  const types = [...new Set(events.map((e) => e.event))];

  // Stats
  const stats = {
    total: events.length,
    sessions: new Set(events.filter((e) => e.session_id && e.session_id !== 'system').map((e) => e.session_id)).size,
    types: types.length,
  };

  return (
    <div className="relative min-h-screen">
      <WaveBackground />
      <div className="relative z-10 p-4 md:p-8 max-w-5xl mx-auto page-enter">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="font-heading text-3xl md:text-4xl text-pearl mb-2">📋 Audit Log</h1>
          <p className="text-seafoam/50 text-sm">
            Complete tamper-evident history of all SMPC computation events
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="stat-card">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Events</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.sessions}</div>
            <div className="stat-label">Sessions</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.types}</div>
            <div className="stat-label">Event Types</div>
          </div>
        </div>

        {/* Toolbar */}
        <div className="glass-card p-4 flex flex-wrap items-center gap-3 mb-6">
          {/* Filter */}
          <div className="flex items-center gap-2">
            <label className="text-xs text-seafoam/50">Filter:</label>
            <select
              id="audit-filter"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
              className="bg-ocean-deep/60 border border-seafoam/20 rounded-lg px-3 py-1.5 text-sm text-pearl focus:outline-none focus:border-teal transition-colors"
            >
              <option value="all">All Events ({events.length})</option>
              {types.map((t) => {
                const style = EVENT_STYLES[t] || DEFAULT_STYLE;
                return (
                  <option key={t} value={t}>
                    {style.icon} {t} ({events.filter((e) => e.event === t).length})
                  </option>
                );
              })}
            </select>
          </div>

          {/* Search */}
          <input
            type="text"
            placeholder="Search events..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-ocean-deep/60 border border-seafoam/20 rounded-lg px-3 py-1.5 text-sm text-pearl focus:outline-none focus:border-teal transition-colors flex-1 min-w-[150px]"
          />

          {/* Auto-refresh toggle */}
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              autoRefresh
                ? 'bg-calm-green/20 text-calm-green border border-calm-green/30'
                : 'bg-ocean-deep/40 text-seafoam/50 border border-seafoam/10'
            }`}
          >
            {autoRefresh ? '● Live' : '○ Auto'}
          </button>

          {/* Refresh */}
          <button onClick={fetchLog} className="btn-secondary text-sm py-1.5 px-3 ml-auto">
            🔄 Refresh
          </button>

          <span className="text-xs text-seafoam/30">{filtered.length} shown</span>
        </div>

        {/* Event List — Timeline Style */}
        <div className="space-y-2">
          {filtered.length === 0 ? (
            <div className="glass-card p-12 text-center">
              <div className="text-5xl mb-4">📭</div>
              <h3 className="font-heading text-lg text-seafoam mb-2">No Events Yet</h3>
              <p className="text-seafoam/40 text-sm">
                Use the Dashboard or Computation Theater to generate SMPC events.
              </p>
            </div>
          ) : (
            [...filtered].reverse().map((event, i) => {
              const style = EVENT_STYLES[event.event] || DEFAULT_STYLE;
              return (
                <div
                  key={event.id || i}
                  className={`${style.bg} border ${style.border} rounded-xl p-4 transition-all duration-300 hover:scale-[1.005]`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      {/* Icon */}
                      <span className="text-lg flex-shrink-0 mt-0.5">{style.icon}</span>

                      <div className="flex-1 min-w-0">
                        {/* Event name and session */}
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`font-medium text-sm ${style.text}`}>{event.event}</span>
                          {event.session_id && event.session_id !== 'system' && event.session_id !== 'protocol_sim' && (
                            <span className="text-[10px] text-seafoam/30 font-mono bg-ocean-darkest/40 px-1.5 py-0.5 rounded">
                              {event.session_id}
                            </span>
                          )}
                        </div>

                        {/* Details */}
                        {event.details && Object.keys(event.details).length > 0 && (
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {Object.entries(event.details).map(([k, v]) => (
                              <span
                                key={k}
                                className="text-[10px] bg-ocean-darkest/50 text-seafoam/50 px-2 py-0.5 rounded-full"
                              >
                                {k}:{' '}
                                <span className="text-pearl/70">
                                  {typeof v === 'object' ? JSON.stringify(v) : String(v)}
                                </span>
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Timestamp */}
                    <span className="text-[10px] text-seafoam/30 whitespace-nowrap font-mono flex-shrink-0">
                      {event.timestamp
                        ? new Date(event.timestamp).toLocaleString()
                        : '-'}
                    </span>
                  </div>
                </div>
              );
            })
          )}
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-seafoam/20">
          All events are logged with cryptographic timestamps for audit compliance
        </p>
      </div>
    </div>
  );
};

export default Audit;
