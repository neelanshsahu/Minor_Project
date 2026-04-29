import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ComputationTheater from './pages/ComputationTheater';
import Results from './pages/Results';
import Audit from './pages/Audit';

/**
 * NavBar — Top navigation with glassmorphism styling.
 * Hidden on the login/landing page.
 */
const NavBar = () => {
  const location = useLocation();
  if (location.pathname === '/') return null;

  const links = [
    { path: '/dashboard', label: 'Dashboard', emoji: '📊' },
    { path: '/theater', label: 'Theater', emoji: '🎭' },
    { path: '/results', label: 'Results', emoji: '📈' },
    { path: '/audit', label: 'Audit', emoji: '📋' },
  ];

  return (
    <nav
      id="main-nav"
      className="fixed top-0 left-0 right-0 z-50 glass-card-strong"
      style={{ borderRadius: 0, borderTop: 'none', borderLeft: 'none', borderRight: 'none' }}
    >
      <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        {/* Logo */}
        <Link
          to="/"
          className="flex items-center gap-2.5 text-pearl hover:text-seafoam transition-colors no-underline"
        >
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-teal to-calm-green flex items-center justify-center text-sm shadow-md shadow-teal/20">
            🔒
          </div>
          <span className="font-heading text-lg hidden md:block">MediVault</span>
        </Link>

        {/* Navigation Links */}
        <div className="flex items-center gap-1 md:gap-3">
          {links.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`nav-link px-2.5 md:px-3 py-1.5 rounded-lg text-xs md:text-sm no-underline transition-all ${location.pathname === link.path
                  ? 'active bg-teal/10 text-seafoam'
                  : 'hover:bg-ocean-deep/40'
                }`}
            >
              <span className="md:mr-1">{link.emoji}</span>
              <span className="hidden md:inline">{link.label}</span>
            </Link>
          ))}
        </div>

        {/* Synthetic Data Badge */}
        <div className="hidden lg:flex items-center gap-1.5 text-xs text-yellow-400/60 bg-yellow-400/5 px-3 py-1.5 rounded-full border border-yellow-400/10">
          <span>⚠️</span>
          <span>Synthetic Data</span>
        </div>
      </div>
    </nav>
  );
};

/**
 * App — Root component with routing.
 */
function App() {
  return (
    <Router>
      <div className="min-h-screen" style={{ background: '#051E28' }}>
        <NavBar />
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/dashboard" element={<div style={{ paddingTop: '64px' }}><Dashboard /></div>} />
          <Route path="/theater" element={<div style={{ paddingTop: '64px' }}><ComputationTheater /></div>} />
          <Route path="/results" element={<div style={{ paddingTop: '64px' }}><Results /></div>} />
          <Route path="/audit" element={<div style={{ paddingTop: '64px' }}><Audit /></div>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
