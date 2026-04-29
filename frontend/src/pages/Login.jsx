import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import WaveBackground from '../components/WaveBackground';
import HowItWorksModal from '../components/HowItWorksModal';
import EncryptionShield from '../components/EncryptionShield';

/**
 * Role definitions for the login/landing page.
 * Each party type in the SMPC protocol has different responsibilities.
 */
const ROLES = [
  {
    id: 'hospital',
    emoji: '🏥',
    title: 'Hospital',
    subtitle: 'Share patient data securely',
    description:
      'Contribute anonymized patient records for collaborative research without exposing individual data.',
    features: ['Patient record sharing', 'Secret splitting', 'Local data control'],
    color: '#1A7A8A',
  },
  {
    id: 'researcher',
    emoji: '🔬',
    title: 'Researcher',
    subtitle: 'Analyze aggregated insights',
    description:
      'Access computed statistics and trends across hospitals without seeing any individual patient record.',
    features: ['Aggregate analytics', 'Trend analysis', 'Privacy-preserving queries'],
    color: '#2494A6',
  },
  {
    id: 'insurance',
    emoji: '🏦',
    title: 'Insurance Provider',
    subtitle: 'Validate claims privately',
    description:
      'Verify aggregate health metrics for actuarial analysis while preserving patient confidentiality.',
    features: ['Claims validation', 'Risk assessment', 'Confidential verification'],
    color: '#52B788',
  },
];

const TECH_BADGES = [
  { label: "Shamir's Secret Sharing", icon: '🔢' },
  { label: 'Homomorphic Encryption', icon: '🔐' },
  { label: 'Garbled Circuits', icon: '⚡' },
  { label: 'Zero-Knowledge Proofs', icon: '🛡️' },
];

const Login = () => {
  const navigate = useNavigate();
  const [selectedRole, setSelectedRole] = useState(null);
  const [showHowItWorks, setShowHowItWorks] = useState(false);
  const [hoveredRole, setHoveredRole] = useState(null);

  const handleLogin = () => {
    if (selectedRole) navigate('/dashboard', { state: { role: selectedRole } });
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center px-4 py-12">
      <WaveBackground />

      <div className="relative z-10 w-full max-w-5xl page-enter">
        {/* Logo & Title */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-4 mb-5">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-teal to-calm-green flex items-center justify-center shadow-lg shadow-teal/20">
              <EncryptionShield active={true} size={36} />
            </div>
            <div className="text-left">
              <h1 className="font-heading text-4xl md:text-5xl text-pearl leading-tight">MediVault</h1>
              <p className="text-teal-light text-sm font-medium tracking-wider uppercase">
                Secure Health Data Collaboration
              </p>
            </div>
          </div>
          <p className="text-seafoam/50 text-base md:text-lg max-w-2xl mx-auto leading-relaxed mt-4">
            Powered by Secure Multi-Party Computation — collaborate on patient insights
            without ever sharing raw data.
          </p>

          {/* Tech Badges */}
          <div className="flex flex-wrap justify-center gap-2 mt-6">
            {TECH_BADGES.map((badge) => (
              <span
                key={badge.label}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium
                  bg-ocean-deep/60 border border-seafoam/10 text-seafoam/60"
              >
                <span>{badge.icon}</span>
                {badge.label}
              </span>
            ))}
          </div>
        </div>

        {/* Role Selection Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
          {ROLES.map((role) => {
            const isSelected = selectedRole === role.id;
            const isHovered = hoveredRole === role.id;
            return (
              <button
                key={role.id}
                id={`role-card-${role.id}`}
                onClick={() => setSelectedRole(role.id)}
                onMouseEnter={() => setHoveredRole(role.id)}
                onMouseLeave={() => setHoveredRole(null)}
                className={`glass-card p-6 text-left cursor-pointer transition-all duration-500 relative overflow-hidden group
                  ${isSelected
                    ? 'ring-1 ring-calm-green/40'
                    : 'hover:border-seafoam/25'
                  }`}
                style={{
                  borderColor: isSelected ? `${role.color}50` : undefined,
                  background: isSelected ? `rgba(13,59,79,0.65)` : undefined,
                }}
              >
                {/* Hover gradient overlay */}
                <div
                  className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                  style={{
                    background: `radial-gradient(circle at 50% 0%, ${role.color}10 0%, transparent 70%)`,
                  }}
                />

                <div className="relative">
                  <div className="flex items-start justify-between mb-3">
                    <span className="text-3xl">{role.emoji}</span>
                    {isSelected && (
                      <span className="status-badge success">
                        ✓ Selected
                      </span>
                    )}
                  </div>
                  <h3 className="font-heading text-xl text-pearl mb-1">{role.title}</h3>
                  <p className="text-sm font-medium mb-3" style={{ color: role.color }}>
                    {role.subtitle}
                  </p>
                  <p className="text-xs text-seafoam/50 leading-relaxed mb-4">
                    {role.description}
                  </p>

                  {/* Feature list */}
                  <div className="space-y-1.5">
                    {role.features.map((f) => (
                      <div key={f} className="flex items-center gap-2 text-xs text-seafoam/40">
                        <span
                          className="w-1 h-1 rounded-full flex-shrink-0"
                          style={{ background: role.color }}
                        />
                        {f}
                      </div>
                    ))}
                  </div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col md:flex-row items-center justify-center gap-4">
          <button
            id="enter-dashboard-btn"
            onClick={handleLogin}
            disabled={!selectedRole}
            className="btn-primary text-lg px-10 py-3.5 w-full md:w-auto"
          >
            Enter Dashboard →
          </button>
          <button
            id="how-it-works-btn"
            onClick={() => setShowHowItWorks(true)}
            className="btn-secondary px-6 py-3 w-full md:w-auto"
          >
            ❓ How Does SMPC Work?
          </button>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center space-y-2">
          <p className="text-seafoam/20 text-xs">
            ⚠️ All patient data is synthetic/fake — generated for demonstration purposes only.
          </p>
          <p className="text-seafoam/15 text-[10px]">
            Built with Shamir's Secret Sharing, Homomorphic Encryption, Garbled Circuits & Zero-Knowledge Proofs
          </p>
        </div>
      </div>

      <HowItWorksModal isOpen={showHowItWorks} onClose={() => setShowHowItWorks(false)} />
    </div>
  );
};

export default Login;
