import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import WaveBackground from '../components/WaveBackground';
import { AggregateBarChart } from '../components/Charts';
import { initSession, uploadShares, computeAggregate } from '../api/client';

const ROLE_CONFIG = {
  hospital:   { emoji: '🏥', title: 'Hospital Dashboard',          accent: '#1A7A8A' },
  researcher: { emoji: '🔬', title: 'Researcher Dashboard',        accent: '#2494A6' },
  insurance:  { emoji: '🏦', title: 'Insurance Provider Dashboard', accent: '#52B788' },
};

const FIELDS = ['age', 'blood_pressure_systolic', 'glucose_level', 'heart_rate', 'cholesterol', 'bmi'];

const PARTIES = [
  { id: 'party_a', label: 'Hospital A', emoji: '🏥' },
  { id: 'party_b', label: 'Hospital B', emoji: '🏥' },
  { id: 'party_c', label: 'Insurance Co', emoji: '🏦' },
];

const Dashboard = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const role = location.state?.role || 'hospital';
  const config = ROLE_CONFIG[role] || ROLE_CONFIG.hospital;

  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(0);
  const [results, setResults] = useState({});
  const [statusMessages, setStatusMessages] = useState([]);
  const [selectedField, setSelectedField] = useState('age');
  const [partyProgress, setPartyProgress] = useState({});

  const addStatus = (msg, type = 'info') => {
    setStatusMessages((prev) => [
      ...prev,
      { id: Date.now() + Math.random(), message: msg, type, timestamp: new Date().toLocaleTimeString() },
    ]);
  };

  const handleInit = async () => {
    setLoading(true);
    addStatus('Initializing SMPC session with 3 parties, 100 records each...', 'info');
    try {
      const data = await initSession(3, 2, 100);
      setSession(data);
      setStep(1);
      addStatus(`✓ Session ${data.session_id} created — ${data.num_parties} parties, ${data.records_per_party} records/party`, 'success');
    } catch (err) {
      addStatus(`✗ Error: ${err.message}`, 'error');
    }
    setLoading(false);
  };

  const handleShare = async () => {
    if (!session) return;
    setLoading(true);
    addStatus(`Generating Shamir shares for "${selectedField.replace(/_/g, ' ')}"...`, 'info');
    try {
      for (const party of PARTIES) {
        setPartyProgress((prev) => ({ ...prev, [party.id]: 'sharing' }));
        const res = await uploadShares(session.session_id, party.id, selectedField);
        setPartyProgress((prev) => ({ ...prev, [party.id]: 'done' }));
        addStatus(`${party.emoji} ${party.label}: ${res.num_records_shared} records → ${res.num_shares_per_record} shares (${res.computation_time_ms}ms)`, 'success');
      }
      setStep(2);
      addStatus('✓ All parties uploaded secret shares', 'success');
    } catch (err) {
      addStatus(`✗ Share error: ${err.message}`, 'error');
    }
    setLoading(false);
  };

  const handleCompute = async () => {
    if (!session) return;
    setLoading(true);
    addStatus('Running secure aggregation (sum, average, count)...', 'info');
    try {
      const newResults = {};
      for (const op of ['sum', 'average', 'count']) {
        const res = await computeAggregate(session.session_id, op, selectedField);
        newResults[op] = res;
        addStatus(
          `📊 ${op.charAt(0).toUpperCase() + op.slice(1)}: ${typeof res.result === 'number' ? res.result.toFixed(2) : res.result} (${res.computation_time_ms}ms)`,
          'success'
        );
      }
      setResults((prev) => ({ ...prev, [selectedField]: newResults }));
      setStep(3);
      addStatus('✓ Aggregation complete — individual values NEVER decrypted', 'success');
    } catch (err) {
      addStatus(`✗ Compute error: ${err.message}`, 'error');
    }
    setLoading(false);
  };

  const getChartData = () => {
    if (!results[selectedField]) return [];
    return [
      { name: 'Sum', value: results[selectedField].sum?.result || 0 },
      { name: 'Average', value: results[selectedField].average?.result || 0 },
      { name: 'Count', value: results[selectedField].count?.result || 0 },
    ];
  };

  return (
    <div className="relative min-h-screen">
      <WaveBackground />
      <div className="relative z-10 p-4 md:p-8 max-w-7xl mx-auto page-enter">
        {/* Header */}
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between mb-8 gap-4">
          <div className="flex items-center gap-3">
            <div
              className="w-12 h-12 rounded-2xl flex items-center justify-center text-2xl"
              style={{ background: `${config.accent}20`, border: `1px solid ${config.accent}30` }}
            >
              {config.emoji}
            </div>
            <div>
              <h1 className="font-heading text-2xl md:text-3xl text-pearl">{config.title}</h1>
              <p className="text-seafoam/50 text-sm">
                Secure Multi-Party Computation Session
                {session && <span className="text-teal-light ml-2 font-mono text-xs">#{session.session_id}</span>}
              </p>
            </div>
          </div>
          <div className="flex gap-2 flex-wrap">
            <button onClick={() => navigate('/theater')} className="btn-secondary text-sm">🎭 Theater</button>
            <button onClick={() => navigate('/results')} className="btn-secondary text-sm">📊 Results</button>
            <button onClick={() => navigate('/audit')} className="btn-secondary text-sm">📋 Audit</button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left: Controls */}
          <div className="lg:col-span-3 space-y-4">
            {/* Session Control */}
            <div className="glass-card p-5">
              <h2 className="font-heading text-lg text-seafoam mb-4">Session Control</h2>

              {/* Step 1: Init */}
              <div className={`mb-3 ${step >= 1 ? 'opacity-40 pointer-events-none' : ''}`}>
                <button id="init-session-btn" onClick={handleInit} disabled={step >= 1 || loading} className="btn-primary w-full text-sm">
                  {step >= 1 ? '✓ Session Active' : '1. Initialize SMPC Session'}
                </button>
              </div>

              {/* Field selector */}
              {step >= 1 && (
                <div className="mb-3">
                  <label className="text-xs text-seafoam/50 mb-1 block">Data Field</label>
                  <select
                    id="field-selector"
                    value={selectedField}
                    onChange={(e) => setSelectedField(e.target.value)}
                    className="w-full bg-ocean-deep/60 border border-seafoam/20 rounded-lg px-3 py-2 text-sm text-pearl focus:outline-none focus:border-teal transition-colors"
                  >
                    {FIELDS.map((f) => (
                      <option key={f} value={f}>{f.replace(/_/g, ' ')}</option>
                    ))}
                  </select>
                </div>
              )}

              {/* Step 2: Share */}
              {step >= 1 && (
                <div className={`mb-3 ${step >= 2 ? 'opacity-40 pointer-events-none' : ''}`}>
                  <button id="upload-shares-btn" onClick={handleShare} disabled={step >= 2 || loading} className="btn-primary w-full text-sm">
                    {step >= 2 ? '✓ Shares Uploaded' : '2. Generate & Upload Shares'}
                  </button>
                </div>
              )}

              {/* Step 3: Compute */}
              {step >= 2 && (
                <div className={step >= 3 ? 'opacity-40 pointer-events-none' : ''}>
                  <button id="compute-btn" onClick={handleCompute} disabled={step >= 3 || loading} className="btn-primary w-full text-sm">
                    {step >= 3 ? '✓ Results Ready' : '3. Compute Aggregation'}
                  </button>
                </div>
              )}

              {loading && (
                <div className="flex justify-center mt-4">
                  <div className="ripple-loader"><div></div><div></div></div>
                </div>
              )}
            </div>

            {/* Session Info */}
            {session && (
              <div className="glass-card p-5">
                <h2 className="font-heading text-lg text-seafoam mb-3">Session Info</h2>
                <div className="space-y-2.5">
                  {[
                    ['Session ID', session.session_id],
                    ['Parties', session.num_parties],
                    ['Threshold', `${session.threshold}-of-${session.num_parties}`],
                    ['Records/Party', session.records_per_party],
                    ['Total Records', session.num_parties * session.records_per_party],
                  ].map(([k, v]) => (
                    <div key={k} className="flex justify-between items-center">
                      <span className="text-seafoam/50 text-xs">{k}</span>
                      <span className="text-pearl font-mono text-xs font-medium">{v}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Party Status */}
            {step >= 1 && (
              <div className="glass-card p-5">
                <h2 className="font-heading text-lg text-seafoam mb-3">Party Status</h2>
                <div className="space-y-2">
                  {PARTIES.map((party) => {
                    const status = partyProgress[party.id];
                    return (
                      <div key={party.id} className="flex items-center justify-between p-2 rounded-lg bg-ocean-darkest/30">
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{party.emoji}</span>
                          <span className="text-xs text-pearl/80">{party.label}</span>
                        </div>
                        <span className={`status-badge ${
                          status === 'done' ? 'success' : status === 'sharing' ? 'running' : 'warning'
                        }`}>
                          {status === 'done' ? '✓ Shared' : status === 'sharing' ? '● Sharing' : '○ Waiting'}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>

          {/* Center: Status Feed */}
          <div className="lg:col-span-5">
            <div className="glass-card p-5 h-full">
              <div className="flex items-center justify-between mb-4">
                <h2 className="font-heading text-lg text-seafoam">📡 Real-Time Status</h2>
                {statusMessages.length > 0 && (
                  <span className="text-xs text-seafoam/30">{statusMessages.length} events</span>
                )}
              </div>
              <div className="space-y-2 max-h-[600px] overflow-y-auto pr-2">
                {statusMessages.length === 0 ? (
                  <div className="text-center py-16">
                    <div className="text-4xl mb-3">🔐</div>
                    <p className="text-seafoam/30 text-sm">Initialize a session to begin...</p>
                    <p className="text-seafoam/20 text-xs mt-2">
                      All data is synthetic — no real patient information is used
                    </p>
                  </div>
                ) : (
                  statusMessages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`text-xs p-2.5 rounded-lg border transition-all duration-300 ${
                        msg.type === 'error'
                          ? 'bg-red-500/10 border-red-500/20 text-red-300'
                          : msg.type === 'success'
                          ? 'bg-calm-green/8 border-calm-green/15 text-calm-green/90'
                          : 'bg-teal/8 border-teal/15 text-teal-light'
                      }`}
                    >
                      <span className="text-seafoam/30 mr-2 font-mono">{msg.timestamp}</span>
                      {msg.message}
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Right: Results & Charts */}
          <div className="lg:col-span-4 space-y-4">
            {step >= 3 && results[selectedField] ? (
              <>
                {/* Stat Cards */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="stat-card">
                    <div className="stat-value">{results[selectedField].count?.result || 0}</div>
                    <div className="stat-label">Records</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">
                      {typeof results[selectedField].average?.result === 'number'
                        ? results[selectedField].average.result.toFixed(1)
                        : '—'}
                    </div>
                    <div className="stat-label">Average</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">
                      {typeof results[selectedField].sum?.result === 'number'
                        ? (results[selectedField].sum.result / 1000).toFixed(1) + 'k'
                        : '—'}
                    </div>
                    <div className="stat-label">Sum</div>
                  </div>
                </div>

                {/* Chart */}
                <AggregateBarChart
                  data={getChartData()}
                  title={`Aggregated ${selectedField.replace(/_/g, ' ')}`}
                />

                {/* Privacy Note */}
                <div className="glass-card p-4 border-calm-green/15">
                  <div className="flex items-start gap-2">
                    <span className="text-lg">🛡️</span>
                    <div>
                      <p className="text-xs text-calm-green font-medium">Privacy Preserved</p>
                      <p className="text-[10px] text-seafoam/40 mt-0.5">
                        Individual patient records were never decrypted during computation.
                        Only aggregate statistics are revealed.
                      </p>
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div className="glass-card p-10 text-center">
                <div className="text-5xl mb-4">🔐</div>
                <h3 className="font-heading text-lg text-seafoam mb-2">Ready to Begin</h3>
                <p className="text-sm text-seafoam/40 leading-relaxed">
                  Initialize a session to generate synthetic patient data and begin secure computation.
                </p>
                <div className="mt-6 flex justify-center gap-2">
                  <span className="shimmer w-16 h-2 inline-block" />
                  <span className="shimmer w-24 h-2 inline-block" />
                  <span className="shimmer w-12 h-2 inline-block" />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <p className="mt-8 text-center text-xs text-seafoam/20">
          ⚠️ ALL DATA IS SYNTHETIC/FAKE — Generated using Faker for demonstration purposes
        </p>
      </div>
    </div>
  );
};

export default Dashboard;
