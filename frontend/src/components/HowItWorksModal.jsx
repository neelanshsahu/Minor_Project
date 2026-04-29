import React, { useState } from 'react';

/**
 * Step-by-step SMPC explainer for non-technical healthcare staff.
 * Uses animated transitions between steps with a progress indicator.
 */
const STEPS = [
  {
    icon: '🏥',
    title: 'Data Stays Private',
    description:
      'Each hospital keeps their patient data on their own systems. No raw data is ever shared with anyone. Your records never leave your secure servers.',
    visual: '[ Hospital A 🔒 ] [ Hospital B 🔒 ] [ Insurance Co 🔒 ]',
    color: '#1A7A8A',
  },
  {
    icon: '🔢',
    title: 'Secret Splitting',
    description:
      'Each value (like a patient\'s age) is split into random "shares" using advanced mathematics. A single share reveals NOTHING about the original value — it looks like a random number.',
    visual: 'Age: 45 → Share₁: 8391723 | Share₂: 9182836 | Share₃: 7291047',
    color: '#2494A6',
  },
  {
    icon: '🔀',
    title: 'Secure Exchange',
    description:
      'Parties exchange only random shares over encrypted channels — never actual data. Even if someone intercepts a share, they cannot learn anything about the original value.',
    visual: '📤 Encrypted shares travel between parties via TLS 🔐',
    color: '#52B788',
  },
  {
    icon: '🧮',
    title: 'Encrypted Computation',
    description:
      'Mathematical calculations happen directly on the encrypted shares. Nobody — not even the computer performing the calculation — can see individual patient values during this step.',
    visual: 'Share₁ + Share₂ + Share₃ = Encrypted Sum → Only the TOTAL is revealed',
    color: '#A8DADC',
  },
  {
    icon: '📊',
    title: 'Only Aggregates Revealed',
    description:
      'The final aggregate result (e.g., "average blood pressure across 300 patients is 128") is reconstructed from the shares. Individual patient records remain completely private.',
    visual: '📈 Result: Average BP = 128 mmHg (300 patients, 0 records exposed)',
    color: '#52B788',
  },
];

const HowItWorksModal = ({ isOpen, onClose }) => {
  const [step, setStep] = useState(0);

  if (!isOpen) return null;

  const current = STEPS[step];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" id="how-it-works-modal">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-md" onClick={onClose} />

      {/* Modal */}
      <div className="glass-card-strong relative z-10 w-full max-w-2xl p-6 md:p-8 page-enter">
        <button
          id="close-modal-btn"
          onClick={onClose}
          className="absolute top-4 right-4 text-seafoam/50 hover:text-pearl text-xl transition-colors w-8 h-8 flex items-center justify-center rounded-full hover:bg-white/5"
        >
          ✕
        </button>

        {/* Header */}
        <h2 className="font-heading text-2xl text-seafoam mb-1">
          How Secure Multi-Party Computation Works
        </h2>
        <p className="text-sm text-seafoam/50 mb-6">
          A simple explanation for healthcare professionals
        </p>

        {/* Progress bar */}
        <div className="flex gap-1 mb-6">
          {STEPS.map((_, i) => (
            <div
              key={i}
              className="h-1 rounded-full flex-1 transition-all duration-500 cursor-pointer"
              style={{
                background: i <= step ? current.color : 'rgba(168,218,220,0.15)',
                opacity: i <= step ? 1 : 0.4,
              }}
              onClick={() => setStep(i)}
            />
          ))}
        </div>

        {/* Content */}
        <div className="flex items-start gap-5 mb-4 page-enter" key={step}>
          <div
            className="flex-shrink-0 w-14 h-14 rounded-2xl flex items-center justify-center text-3xl"
            style={{ background: `${current.color}20`, border: `1px solid ${current.color}30` }}
          >
            {current.icon}
          </div>
          <div className="flex-1">
            <h3 className="font-heading text-xl text-pearl mb-2">
              Step {step + 1}: {current.title}
            </h3>
            <p className="text-sm text-seafoam/70 leading-relaxed mb-4">
              {current.description}
            </p>
            {/* Visual representation */}
            <div className="bg-ocean-darkest/60 border border-seafoam/10 rounded-xl p-3 text-xs font-mono text-seafoam/50 text-center">
              {current.visual}
            </div>
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center justify-between mt-6 pt-4 border-t border-seafoam/10">
          <button
            onClick={() => setStep(Math.max(0, step - 1))}
            disabled={step === 0}
            className="btn-secondary text-sm disabled:opacity-20 disabled:cursor-not-allowed"
          >
            ← Previous
          </button>
          <div className="flex gap-2">
            {STEPS.map((_, i) => (
              <button
                key={i}
                onClick={() => setStep(i)}
                className={`w-2.5 h-2.5 rounded-full transition-all duration-300 ${
                  i === step
                    ? 'scale-125'
                    : i < step
                    ? ''
                    : ''
                }`}
                style={{
                  background: i === step ? current.color : i < step ? '#1A7A8A' : 'rgba(168,218,220,0.2)',
                  boxShadow: i === step ? `0 0 8px ${current.color}80` : 'none',
                }}
              />
            ))}
          </div>
          <button
            onClick={() => (step < STEPS.length - 1 ? setStep(step + 1) : onClose())}
            className="btn-primary text-sm"
          >
            {step < STEPS.length - 1 ? 'Next →' : 'Got It ✓'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default HowItWorksModal;
