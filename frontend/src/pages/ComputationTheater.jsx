import React, { useState } from 'react';
import WaveBackground from '../components/WaveBackground';
import NodeGraph from '../components/NodeGraph';
import EncryptionShield from '../components/EncryptionShield';
import { simulateProtocol } from '../api/client';

const STEPS = [
  { label: 'Initializing', desc: 'Generating synthetic patient data for each party...', icon: '🔧' },
  { label: 'Secret Sharing', desc: 'Splitting data into encrypted Shamir shares...', icon: '🔢' },
  { label: 'Share Exchange', desc: 'Exchanging shares over simulated TLS channels...', icon: '🔀' },
  { label: 'Aggregation', desc: 'Computing sum & average on encrypted shares...', icon: '🧮' },
  { label: 'Reconstruction', desc: 'Reconstructing final aggregate result...', icon: '📊' },
];

const ComputationTheater = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [protocolResult, setProtocolResult] = useState(null);
  const [stepLogs, setStepLogs] = useState([]);
  const [field, setField] = useState('age');
  const [numParties, setNumParties] = useState(3);
  const [error, setError] = useState(null);

  const runProtocol = async () => {
    setIsRunning(true);
    setCurrentStep(0);
    setStepLogs([]);
    setProtocolResult(null);
    setError(null);

    // Animate through protocol steps
    for (let i = 0; i < 4; i++) {
      setCurrentStep(i + 1);
      setStepLogs((prev) => [
        ...prev,
        { step: i + 1, name: STEPS[i].label, icon: STEPS[i].icon, status: 'running', time: new Date().toLocaleTimeString() },
      ]);
      await new Promise((r) => setTimeout(r, 1200));
      setStepLogs((prev) =>
        prev.map((l, idx) => (idx === prev.length - 1 ? { ...l, status: 'complete' } : l))
      );
    }

    // Actually call the backend
    try {
      const result = await simulateProtocol(numParties, 20, field);
      setProtocolResult(result);
      setCurrentStep(5);
      setStepLogs((prev) => [
        ...prev,
        { step: 5, name: 'Complete', icon: '✅', status: 'complete', time: new Date().toLocaleTimeString() },
      ]);
    } catch (err) {
      setError(err.message || 'Protocol simulation failed');
    }
    setIsRunning(false);
  };

  return (
    <div className="relative min-h-screen">
      <WaveBackground />
      <div className="relative z-10 p-4 md:p-8 max-w-7xl mx-auto page-enter">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="font-heading text-3xl md:text-4xl text-pearl mb-2">
            🎭 Computation Theater
          </h1>
          <p className="text-seafoam/50 text-sm max-w-lg mx-auto">
            Watch encrypted data flow between parties in real-time.
            No individual values are ever exposed during computation.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Node Graph — takes 2 columns */}
          <div className="lg:col-span-2 glass-card p-6">
            {/* Top bar */}
            <div className="flex items-center justify-between mb-4">
              <h2 className="font-heading text-xl text-seafoam">Secure Data Flow</h2>
              <div className="flex items-center gap-3">
                <EncryptionShield active={currentStep >= 2} size={28} />
                <span className={`text-xs font-medium ${currentStep >= 2 ? 'text-calm-green' : 'text-seafoam/40'}`}>
                  {currentStep >= 2 ? '🟢 Encrypted Channel Active' : '⚪ Idle'}
                </span>
              </div>
            </div>

            {/* Graph visualization */}
            <NodeGraph computationStep={currentStep} isComputing={isRunning} />

            {/* Current step indicator */}
            {currentStep > 0 && currentStep <= STEPS.length && (
              <div className="mt-4 glass-card-strong p-3 text-center">
                <div className="flex items-center justify-center gap-2">
                  <span className="text-lg">{STEPS[Math.min(currentStep, STEPS.length) - 1]?.icon}</span>
                  <span className="text-sm font-medium text-seafoam">
                    Step {Math.min(currentStep, STEPS.length)}:{' '}
                    {STEPS[Math.min(currentStep, STEPS.length) - 1]?.label}
                  </span>
                </div>
                <div className="text-xs text-seafoam/50 mt-1">
                  {STEPS[Math.min(currentStep, STEPS.length) - 1]?.desc}
                </div>
                {isRunning && (
                  <div className="flex justify-center mt-2">
                    <div className="ripple-loader" style={{ width: 28, height: 28 }}>
                      <div></div><div></div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step progress bar */}
            <div className="flex gap-1 mt-4">
              {STEPS.map((s, i) => (
                <div
                  key={i}
                  className="h-1 rounded-full flex-1 transition-all duration-500"
                  style={{
                    background:
                      i + 1 <= currentStep
                        ? i + 1 === currentStep && isRunning
                          ? '#1A7A8A'
                          : '#52B788'
                        : 'rgba(168,218,220,0.1)',
                  }}
                />
              ))}
            </div>
          </div>

          {/* Right Panel: Controls + Logs + Results */}
          <div className="space-y-4">
            {/* Protocol Controls */}
            <div className="glass-card p-5">
              <h2 className="font-heading text-lg text-seafoam mb-4">Protocol Controls</h2>

              <div className="mb-3">
                <label className="text-xs text-seafoam/50 mb-1 block">Data Field</label>
                <select
                  value={field}
                  onChange={(e) => setField(e.target.value)}
                  disabled={isRunning}
                  className="w-full bg-ocean-deep/60 border border-seafoam/20 rounded-lg px-3 py-2 text-sm text-pearl focus:outline-none focus:border-teal transition-colors"
                >
                  {['age', 'blood_pressure_systolic', 'glucose_level', 'heart_rate', 'cholesterol', 'bmi'].map(
                    (f) => (
                      <option key={f} value={f}>
                        {f.replace(/_/g, ' ')}
                      </option>
                    )
                  )}
                </select>
              </div>

              <div className="mb-4">
                <label className="text-xs text-seafoam/50 mb-1 block">
                  Parties: <span className="text-pearl font-medium">{numParties}</span>
                </label>
                <input
                  type="range"
                  min="2"
                  max="5"
                  value={numParties}
                  onChange={(e) => setNumParties(parseInt(e.target.value))}
                  disabled={isRunning}
                  className="w-full accent-teal"
                />
                <div className="flex justify-between text-[10px] text-seafoam/30 mt-0.5">
                  <span>2</span><span>3</span><span>4</span><span>5</span>
                </div>
              </div>

              <button
                id="run-protocol-btn"
                onClick={runProtocol}
                disabled={isRunning}
                className="btn-primary w-full"
              >
                {isRunning ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="inline-block w-2 h-2 bg-white rounded-full animate-pulse" />
                    Running Protocol...
                  </span>
                ) : (
                  '▶ Run SMPC Protocol'
                )}
              </button>
            </div>

            {/* Protocol Log */}
            <div className="glass-card p-5">
              <h2 className="font-heading text-lg text-seafoam mb-3">Protocol Log</h2>
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {stepLogs.length === 0 ? (
                  <p className="text-seafoam/30 text-sm text-center py-4">
                    Run the protocol to see step-by-step execution...
                  </p>
                ) : (
                  stepLogs.map((log, i) => (
                    <div
                      key={i}
                      className={`flex items-center gap-2 text-xs p-2.5 rounded-lg border transition-all ${
                        log.status === 'running'
                          ? 'bg-teal/10 border-teal/20'
                          : 'bg-calm-green/8 border-calm-green/15'
                      }`}
                    >
                      <span>{log.status === 'running' ? '⏳' : log.icon}</span>
                      <span className="text-seafoam/50 font-mono">{log.time}</span>
                      <span className="text-pearl/80 flex-1">{log.name}</span>
                      {log.status === 'complete' && (
                        <span className="text-calm-green text-[10px]">✓</span>
                      )}
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Results */}
            {protocolResult && (
              <div className="glass-card p-5 border-calm-green/20">
                <h2 className="font-heading text-lg text-calm-green mb-3">🎉 Protocol Results</h2>
                <div className="space-y-2.5">
                  <div className="grid grid-cols-2 gap-3">
                    <div className="stat-card">
                      <div className="stat-value text-lg">
                        {protocolResult.results?.secure_average?.toFixed(1) || 'N/A'}
                      </div>
                      <div className="stat-label">Average</div>
                    </div>
                    <div className="stat-card">
                      <div className="stat-value text-lg">
                        {protocolResult.results?.secure_sum || 'N/A'}
                      </div>
                      <div className="stat-label">Sum</div>
                    </div>
                  </div>

                  <div className="space-y-1.5 mt-3">
                    <div className="flex justify-between text-xs">
                      <span className="text-seafoam/50">Accuracy Match</span>
                      <span className={protocolResult.results?.sum_match ? 'text-calm-green' : 'text-red-400'}>
                        {protocolResult.results?.sum_match ? '✅ Exact' : '❌ Mismatch'}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-seafoam/50">Total Time</span>
                      <span className="text-teal-light font-mono">{protocolResult.total_time_ms}ms</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-seafoam/50">Records</span>
                      <span className="text-pearl font-mono">{protocolResult.total_records}</span>
                    </div>
                  </div>

                  <div className="mt-3 p-2.5 bg-calm-green/5 border border-calm-green/10 rounded-lg text-center">
                    <p className="text-[10px] text-calm-green/70">
                      🛡️ {protocolResult.privacy_guarantee}
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="glass-card p-4 border-red-500/30 bg-red-500/5">
                <p className="text-sm text-red-300">❌ {error}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ComputationTheater;
