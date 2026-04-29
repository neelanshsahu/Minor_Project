import React from 'react';
import EncryptionShield from './EncryptionShield';

/**
 * Party node positions and metadata for the computation theater.
 * Arranged in a triangular layout with the aggregator in the center.
 */
const PARTY_NODES = [
  { id: 'hospital_a', label: 'Hospital A', emoji: '🏥', x: 15, y: 25, color: '#1A7A8A' },
  { id: 'hospital_b', label: 'Hospital B', emoji: '🏥', x: 15, y: 75, color: '#2494A6' },
  { id: 'insurance',  label: 'Insurance Co', emoji: '🏦', x: 85, y: 50, color: '#52B788' },
];

const AGGREGATOR = { id: 'aggregator', label: 'Secure Aggregator', emoji: '🔐', x: 50, y: 50 };

/**
 * NodeGraph — Animated visualization of the SMPC data flow.
 * Shows party nodes, connections, encryption shields, and data flow animations.
 */
const NodeGraph = ({ computationStep = 0, isComputing = false }) => {
  const isActive = () => computationStep >= 2;
  const showResult = computationStep >= 4;

  // Determine node status text
  const getNodeStatus = (step) => {
    if (!isComputing && step === 0) return null;
    if (step >= 1 && step < 2) return { text: 'Splitting data...', color: 'text-teal-light' };
    if (step >= 2 && step < 3) return { text: 'Sharing...', color: 'text-yellow-400' };
    if (step >= 3 && step < 4) return { text: 'Computing...', color: 'text-calm-green' };
    if (step >= 4) return { text: '✓ Complete', color: 'text-calm-green' };
    return null;
  };

  const nodeStatus = getNodeStatus(computationStep);

  return (
    <div className="relative w-full" style={{ height: '380px' }}>
      {/* SVG connection lines */}
      <svg className="absolute inset-0 w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="lineGradActive" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#52B788" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#1A7A8A" stopOpacity="0.6" />
            <stop offset="100%" stopColor="#52B788" stopOpacity="0.8" />
          </linearGradient>
          <linearGradient id="lineGradIdle" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%" stopColor="#A8DADC" stopOpacity="0.15" />
            <stop offset="100%" stopColor="#A8DADC" stopOpacity="0.08" />
          </linearGradient>
          <filter id="glowFilter">
            <feGaussianBlur stdDeviation="0.5" result="blur"/>
            <feMerge>
              <feMergeNode in="blur"/>
              <feMergeNode in="SourceGraphic"/>
            </feMerge>
          </filter>
        </defs>

        {PARTY_NODES.map((node) => {
          const active = isActive();
          return (
            <g key={node.id}>
              {/* Main connection line */}
              <line
                x1={node.x + 5}
                y1={node.y}
                x2={AGGREGATOR.x - 5}
                y2={AGGREGATOR.y}
                stroke={active ? 'url(#lineGradActive)' : 'url(#lineGradIdle)'}
                strokeWidth={active ? '0.5' : '0.2'}
                className={active ? 'data-flow-line' : ''}
                filter={active ? 'url(#glowFilter)' : undefined}
              />
              {/* Data flow particles along the line */}
              {active && computationStep >= 2 && computationStep < 5 && (
                <>
                  <circle r="1.2" fill="#52B788" opacity="0.9">
                    <animateMotion
                      dur={`${1.5 + Math.random()}s`}
                      repeatCount="indefinite"
                      path={`M${node.x + 5},${node.y} L${AGGREGATOR.x - 5},${AGGREGATOR.y}`}
                    />
                  </circle>
                  <circle r="0.8" fill="#A8DADC" opacity="0.6">
                    <animateMotion
                      dur={`${2 + Math.random()}s`}
                      repeatCount="indefinite"
                      path={`M${node.x + 5},${node.y} L${AGGREGATOR.x - 5},${AGGREGATOR.y}`}
                    />
                  </circle>
                </>
              )}
              {/* Shield icon at midpoint */}
              {active && (
                <g>
                  <text
                    x={(node.x + 5 + AGGREGATOR.x - 5) / 2}
                    y={(node.y + AGGREGATOR.y) / 2 - 2}
                    textAnchor="middle"
                    fontSize="3"
                    style={{ filter: 'drop-shadow(0 0 2px rgba(82,183,136,0.6))' }}
                  >
                    🔒
                  </text>
                </g>
              )}
            </g>
          );
        })}
      </svg>

      {/* Party Nodes */}
      {PARTY_NODES.map((node) => (
        <div
          key={node.id}
          className={`absolute glass-card p-3 text-center transition-all duration-500
            ${isComputing && computationStep >= 1 ? 'node-computing' : ''}`}
          style={{
            left: `${node.x}%`,
            top: `${node.y}%`,
            transform: 'translate(-50%, -50%)',
            minWidth: '100px',
            borderColor: computationStep >= 1 ? `${node.color}40` : undefined,
          }}
        >
          <div className="text-2xl mb-1">{node.emoji}</div>
          <div className="text-xs text-seafoam font-medium">{node.label}</div>
          {nodeStatus && (
            <div className={`text-[10px] mt-1 font-medium ${nodeStatus.color}`}>
              {nodeStatus.text}
            </div>
          )}
        </div>
      ))}

      {/* Aggregator Node (central) */}
      <div
        className={`absolute glass-card-strong p-4 text-center transition-all duration-500
          ${isComputing && computationStep >= 3 ? 'node-computing' : ''}`}
        style={{
          left: `${AGGREGATOR.x}%`,
          top: `${AGGREGATOR.y}%`,
          transform: 'translate(-50%, -50%)',
          minWidth: '130px',
          borderColor: computationStep >= 3 ? 'rgba(82,183,136,0.35)' : undefined,
        }}
      >
        <div className="flex justify-center mb-1">
          <EncryptionShield active={computationStep >= 2} size={36} />
        </div>
        <div className="text-sm font-semibold text-pearl">{AGGREGATOR.label}</div>
        {isComputing && computationStep >= 3 && computationStep < 5 && (
          <div className="text-xs text-calm-green mt-1 flex items-center justify-center gap-1">
            <span className="inline-block w-1.5 h-1.5 bg-calm-green rounded-full animate-pulse" />
            Computing...
          </div>
        )}
        {showResult && (
          <div className="text-xs text-calm-green mt-1 font-bold">✅ Complete</div>
        )}
      </div>

      {/* Legend */}
      <div className="absolute bottom-2 left-2 flex items-center gap-4 text-[10px] text-seafoam/40">
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-0.5 bg-seafoam/20 rounded" /> Idle
        </span>
        <span className="flex items-center gap-1">
          <span className="inline-block w-3 h-0.5 bg-calm-green rounded" /> Encrypted
        </span>
        <span className="flex items-center gap-1">
          🔒 TLS Protected
        </span>
      </div>
    </div>
  );
};

export default NodeGraph;
