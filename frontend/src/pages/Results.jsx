import React, { useState, useEffect } from 'react';
import WaveBackground from '../components/WaveBackground';
import { AggregateBarChart, PerformanceLineChart, SecurityRadarChart } from '../components/Charts';
import { getEvaluationReport, getSecurityMetrics, saveReport, listReports } from '../api/client';

const Results = () => {
  const [benchmarks, setBenchmarks] = useState(null);
  const [security, setSecurity] = useState(null);
  const [loading, setLoading] = useState(false);
  const [tab, setTab] = useState('benchmarks');
  const [savedReports, setSavedReports] = useState([]);
  const [saveStatus, setSaveStatus] = useState(null);

  const loadSavedReports = async () => {
    try {
      const data = await listReports();
      setSavedReports(data.reports || []);
    } catch (err) {
      console.error('Could not load saved reports:', err);
    }
  };

  useEffect(() => {
    loadSavedReports();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [b, s] = await Promise.all([
        getEvaluationReport('json').catch(() => null),
        getSecurityMetrics().catch(() => null),
      ]);
      setBenchmarks(b);
      setSecurity(s);
      // Refresh saved reports list (backend auto-saves on evaluation)
      await loadSavedReports();
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handleSaveReport = async () => {
    if (!benchmarks) return;
    setSaveStatus('saving');
    try {
      const dataToSave = { ...benchmarks };
      delete dataToSave._cache_time;
      if (security) dataToSave.security_metrics = security;
      await saveReport(dataToSave, 'manual_report');
      setSaveStatus('saved');
      await loadSavedReports();
      setTimeout(() => setSaveStatus(null), 3000);
    } catch (err) {
      setSaveStatus('error');
      setTimeout(() => setSaveStatus(null), 3000);
    }
  };

  const getSSData = () =>
    (benchmarks?.benchmarks?.secret_sharing?.data || []).map((d) => ({
      name: `${d.num_parties}P`,
      split: d.avg_split_time_ms,
      reconstruct: d.avg_reconstruct_time_ms,
    }));

  const getAggData = () =>
    (benchmarks?.benchmarks?.secure_aggregation?.data || []).map((d) => ({
      name: `${d.num_parties}P`,
      sum: d.avg_sum_time_ms,
      average: d.avg_average_time_ms,
    }));

  const getGCData = () =>
    (benchmarks?.benchmarks?.garbled_circuits?.data || []).map((d) => ({
      name: `${d.bit_width}b`,
      create: d.avg_create_time_ms,
      compare: d.avg_compare_time_ms,
    }));

  const getHEData = () =>
    (benchmarks?.benchmarks?.homomorphic_encryption?.data || []).map((d) => ({
      name: `S${d.vector_size}`,
      encrypt: d.avg_encrypt_time_ms,
      add: d.avg_add_time_ms,
      decrypt: d.avg_decrypt_time_ms,
    }));

  const getZKPData = () =>
    (benchmarks?.benchmarks?.zero_knowledge_proofs?.data || []).map((d) => ({
      name: d.proof_type,
      value: d.avg_generation_time_ms + d.avg_verification_time_ms,
    }));

  const getSecurityRadarData = () => {
    if (!security) return [];
    return [
      { metric: 'Entropy', value: Math.min(security.avg_share_entropy || 0, 8) },
      { metric: 'Accuracy', value: (security.reconstruction_accuracy || 0) * 10 },
      { metric: 'Info Security', value: security.information_theoretic_security ? 10 : 0 },
      { metric: 'Threshold', value: 8 },
      { metric: 'Integrity', value: security.max_reconstruction_error === 0 ? 10 : 5 },
    ];
  };

  const TABS = [
    { id: 'benchmarks', label: '📊 Performance', icon: '📊' },
    { id: 'security', label: '🛡️ Security', icon: '🛡️' },
    { id: 'reports', label: '📁 Saved Reports', icon: '📁' },
  ];

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div className="relative min-h-screen">
      <WaveBackground />
      <div className="relative z-10 p-4 md:p-8 max-w-7xl mx-auto page-enter">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="font-heading text-3xl md:text-4xl text-pearl mb-2">
            📊 Results & Evaluation
          </h1>
          <p className="text-seafoam/50 text-sm max-w-lg mx-auto">
            Performance benchmarks and security metrics for the SMPC protocol suite
          </p>
        </div>

        {/* Run Button */}
        {!benchmarks && (
          <div className="flex justify-center mb-8">
            <button
              id="run-benchmarks-btn"
              onClick={loadData}
              disabled={loading}
              className="btn-primary text-lg px-10 py-3.5"
            >
              {loading ? (
                <span className="flex items-center gap-2">
                  <span className="inline-block w-2 h-2 bg-white rounded-full animate-pulse" />
                  Running Benchmarks...
                </span>
              ) : (
                '🚀 Run Evaluation Suite'
              )}
            </button>
          </div>
        )}

        {/* Loading state */}
        {loading && !benchmarks && (
          <div className="flex flex-col items-center gap-4 mb-8">
            <div className="ripple-loader"><div></div><div></div></div>
            <p className="text-seafoam/40 text-sm">
              Running all benchmarks: Secret Sharing, Aggregation, Garbled Circuits, HE, ZKPs...
            </p>
            <p className="text-seafoam/30 text-xs">
              Report will be auto-saved to backend/reports/ directory
            </p>
          </div>
        )}

        {/* Tab Selector */}
        {(benchmarks || savedReports.length > 0) && (
          <div className="flex justify-center gap-2 mb-8">
            {TABS.map((t) => (
              <button
                key={t.id}
                onClick={() => setTab(t.id)}
                className={`px-5 py-2.5 rounded-xl text-sm font-medium transition-all duration-300 ${
                  tab === t.id
                    ? 'bg-teal/25 text-pearl border border-teal/35 shadow-lg shadow-teal/10'
                    : 'text-seafoam/50 hover:text-seafoam hover:bg-ocean-deep/40 border border-transparent'
                }`}
              >
                {t.label}
                {t.id === 'reports' && savedReports.length > 0 && (
                  <span className="ml-1.5 text-xs bg-teal/30 px-1.5 py-0.5 rounded-full">
                    {savedReports.length}
                  </span>
                )}
              </button>
            ))}
          </div>
        )}

        {/* Performance Tab */}
        {tab === 'benchmarks' && benchmarks && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <PerformanceLineChart
              data={getSSData()}
              title="🔑 Secret Sharing"
              lines={[
                { key: 'split', label: 'Split (ms)' },
                { key: 'reconstruct', label: 'Reconstruct (ms)' },
              ]}
            />
            <PerformanceLineChart
              data={getAggData()}
              title="📈 Secure Aggregation"
              lines={[
                { key: 'sum', label: 'Sum (ms)' },
                { key: 'average', label: 'Average (ms)' },
              ]}
            />
            <PerformanceLineChart
              data={getGCData()}
              title="🔐 Garbled Circuits"
              lines={[
                { key: 'create', label: 'Create (ms)' },
                { key: 'compare', label: 'Compare (ms)' },
              ]}
            />
            <PerformanceLineChart
              data={getHEData()}
              title="🔢 Homomorphic Encryption"
              lines={[
                { key: 'encrypt', label: 'Encrypt (ms)' },
                { key: 'add', label: 'Add (ms)' },
                { key: 'decrypt', label: 'Decrypt (ms)' },
              ]}
            />
            <AggregateBarChart data={getZKPData()} title="🛡️ Zero-Knowledge Proofs — Total Time" />

            {/* Summary Card */}
            <div className="glass-card p-5">
              <h3 className="font-heading text-lg text-seafoam mb-4">📋 Benchmark Summary</h3>
              <div className="space-y-3 mb-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-seafoam/60">Total Benchmark Time</span>
                  <span className="text-pearl font-bold font-mono">
                    {benchmarks.total_benchmark_time_seconds}s
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-seafoam/60">Timestamp</span>
                  <span className="text-seafoam/70 text-xs font-mono">{benchmarks.timestamp}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-seafoam/60">HE Backend</span>
                  <span className="status-badge warning">
                    {benchmarks.benchmarks?.homomorphic_encryption?.data?.[0]?.using_tenseal
                      ? 'TenSEAL'
                      : 'Simulated'}
                  </span>
                </div>
              </div>

              {/* Module stats */}
              <div className="grid grid-cols-2 gap-2 mb-4">
                {[
                  { label: 'SS Configs', value: getSSData().length },
                  { label: 'Agg Configs', value: getAggData().length },
                  { label: 'GC Widths', value: getGCData().length },
                  { label: 'ZKP Types', value: getZKPData().length },
                ].map((s) => (
                  <div key={s.label} className="stat-card" style={{ padding: '0.75rem' }}>
                    <div className="stat-value text-base">{s.value}</div>
                    <div className="stat-label" style={{ fontSize: '0.6rem' }}>{s.label}</div>
                  </div>
                ))}
              </div>

              <div className="flex gap-2">
                <button onClick={loadData} className="btn-secondary flex-1 text-sm">
                  🔄 Re-run Benchmarks
                </button>
                <button
                  onClick={handleSaveReport}
                  disabled={saveStatus === 'saving'}
                  className="btn-primary flex-1 text-sm"
                >
                  {saveStatus === 'saving' ? '💾 Saving...'
                    : saveStatus === 'saved' ? '✅ Saved!'
                    : saveStatus === 'error' ? '❌ Error'
                    : '💾 Save Report'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Security Tab */}
        {tab === 'security' && security && (
          <div className="max-w-4xl mx-auto">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Security metrics */}
              <div className="glass-card p-6">
                <h3 className="font-heading text-xl text-seafoam mb-5">🛡️ Security Evaluation</h3>

                <div className="grid grid-cols-2 gap-3 mb-6">
                  <div className="stat-card">
                    <div className="stat-value">{security.avg_share_entropy}</div>
                    <div className="stat-label">Share Entropy (bits)</div>
                  </div>
                  <div className="stat-card">
                    <div className="stat-value">
                      {(security.reconstruction_accuracy * 100).toFixed(0)}%
                    </div>
                    <div className="stat-label">Reconstruction</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div className="flex justify-between p-3 bg-calm-green/5 rounded-lg border border-calm-green/10">
                    <span className="text-sm text-seafoam/70">Info-Theoretic Security</span>
                    <span className="text-calm-green font-medium">
                      {security.information_theoretic_security ? '✅ Proven' : '❌ No'}
                    </span>
                  </div>
                  <div className="flex justify-between p-3 bg-teal/5 rounded-lg border border-teal/10">
                    <span className="text-sm text-seafoam/70">Max Reconstruction Error</span>
                    <span className="text-pearl font-mono">{security.max_reconstruction_error}</span>
                  </div>
                  <div className="flex justify-between p-3 bg-ocean-deep/30 rounded-lg border border-seafoam/10">
                    <span className="text-sm text-seafoam/70">Min Entropy</span>
                    <span className="text-pearl font-mono">{security.min_share_entropy} bits</span>
                  </div>
                  <div className="flex justify-between p-3 bg-ocean-deep/30 rounded-lg border border-seafoam/10">
                    <span className="text-sm text-seafoam/70">Max Entropy</span>
                    <span className="text-pearl font-mono">{security.max_share_entropy} bits</span>
                  </div>
                </div>

                <div className="mt-4 p-3 bg-calm-green/5 rounded-lg border border-calm-green/10">
                  <p className="text-xs text-calm-green/80 leading-relaxed">
                    🔒 {security.threshold_security}
                  </p>
                </div>
              </div>

              {/* Radar Chart */}
              <SecurityRadarChart data={getSecurityRadarData()} title="Security Profile" />
            </div>
          </div>
        )}

        {/* Saved Reports Tab */}
        {tab === 'reports' && (
          <div className="max-w-4xl mx-auto">
            <div className="glass-card p-6">
              <div className="flex items-center justify-between mb-5">
                <h3 className="font-heading text-xl text-seafoam">📁 Saved Reports</h3>
                <button onClick={loadSavedReports} className="btn-secondary text-sm py-1.5 px-3">
                  🔄 Refresh
                </button>
              </div>

              {savedReports.length === 0 ? (
                <div className="text-center py-12">
                  <div className="text-5xl mb-4">📭</div>
                  <h4 className="font-heading text-lg text-seafoam mb-2">No Reports Yet</h4>
                  <p className="text-seafoam/40 text-sm mb-4">
                    Run the evaluation suite to generate and auto-save reports.
                  </p>
                  <p className="text-seafoam/30 text-xs">
                    Reports are stored in <code className="text-teal-light">backend/reports/</code> directory
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {savedReports.map((report, i) => (
                    <div
                      key={report.filename}
                      className="flex items-center justify-between p-4 rounded-xl bg-ocean-deep/30 border border-seafoam/10 hover:border-seafoam/25 transition-all duration-300"
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <span className="text-lg flex-shrink-0">📄</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm text-pearl font-medium truncate">{report.filename}</p>
                          <div className="flex items-center gap-3 mt-0.5">
                            <span className="text-[10px] text-seafoam/40 font-mono">
                              {formatFileSize(report.size_bytes)}
                            </span>
                            <span className="text-[10px] text-seafoam/30 font-mono">
                              {new Date(report.created_at).toLocaleString()}
                            </span>
                          </div>
                        </div>
                      </div>
                      <span className="status-badge success ml-3">
                        ✓ Saved
                      </span>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-4 p-3 bg-teal/5 rounded-lg border border-teal/10">
                <p className="text-xs text-seafoam/50 leading-relaxed">
                  💡 Reports are automatically saved when you run the evaluation suite.
                  You can also manually save with the "Save Report" button on the Performance tab.
                  All reports are stored as JSON in the <code className="text-teal-light">backend/reports/</code> directory.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Placeholder when no data */}
        {!benchmarks && !loading && savedReports.length === 0 && (
          <div className="text-center mt-12">
            <div className="glass-card inline-block p-10 mx-auto">
              <div className="text-5xl mb-4">📈</div>
              <h3 className="font-heading text-lg text-seafoam mb-2">No Data Yet</h3>
              <p className="text-seafoam/40 text-sm">
                Run the evaluation suite to benchmark all SMPC modules
              </p>
              <div className="mt-6 flex justify-center gap-2">
                <span className="shimmer w-20 h-2 inline-block" />
                <span className="shimmer w-16 h-2 inline-block" />
                <span className="shimmer w-24 h-2 inline-block" />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Results;
