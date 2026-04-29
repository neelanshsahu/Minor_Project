import React from 'react';

/**
 * EncryptionShield — SVG shield icon with glow animation.
 * Glows green when the encrypted channel is active.
 */
const EncryptionShield = ({ active = false, size = 40 }) => (
  <div className={`inline-flex items-center justify-center transition-all duration-500 ${active ? 'shield-active' : ''}`}>
    <svg width={size} height={size} viewBox="0 0 40 40" fill="none">
      <defs>
        <linearGradient id="shieldGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={active ? '#52B788' : '#A8DADC'} stopOpacity={active ? 0.5 : 0.2} />
          <stop offset="100%" stopColor={active ? '#3D9A6E' : '#7CC0C3'} stopOpacity={active ? 0.3 : 0.1} />
        </linearGradient>
        {active && (
          <filter id="shieldBlur">
            <feGaussianBlur stdDeviation="1.5" />
          </filter>
        )}
      </defs>
      {/* Outer glow layer */}
      {active && (
        <path
          d="M20 3L5 10V19C5 28.5 11.5 37.1 20 39C28.5 37.1 35 28.5 35 19V10L20 3Z"
          fill="rgba(82,183,136,0.15)"
          filter="url(#shieldBlur)"
        />
      )}
      {/* Shield body */}
      <path
        d="M20 3L5 10V19C5 28.5 11.5 37.1 20 39C28.5 37.1 35 28.5 35 19V10L20 3Z"
        fill="url(#shieldGrad)"
        stroke={active ? '#52B788' : '#A8DADC'}
        strokeWidth="1.5"
      />
      {/* Lock body */}
      <rect
        x="15" y="18" width="10" height="8" rx="2"
        fill={active ? '#52B788' : '#A8DADC'}
        opacity={active ? 0.9 : 0.5}
      />
      {/* Lock shackle */}
      <path
        d="M17 18V15C17 13.3431 18.3431 12 20 12C21.6569 12 23 13.3431 23 15V18"
        stroke={active ? '#52B788' : '#A8DADC'}
        strokeWidth="1.5"
        fill="none"
        opacity={active ? 0.9 : 0.5}
      />
      {/* Keyhole */}
      {active && (
        <circle cx="20" cy="22" r="1.5" fill="#0D3B4F" opacity={0.7} />
      )}
    </svg>
  </div>
);

export default EncryptionShield;
