import React, { useEffect, useRef } from 'react';

/**
 * WaveBackground — Animated ocean-dawn background with particle effects.
 * Fixed position, renders behind all content. Uses canvas for particles
 * and layered SVG waves for the ocean effect.
 */
const WaveBackground = () => {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animId;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // Create ambient particles (simulate underwater light particles)
    const particles = Array.from({ length: 50 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 2.5 + 0.5,
      speedX: (Math.random() - 0.5) * 0.3,
      speedY: -Math.random() * 0.4 - 0.1,
      opacity: Math.random() * 0.3 + 0.05,
      pulseSpeed: Math.random() * 0.02 + 0.01,
      pulsePhase: Math.random() * Math.PI * 2,
    }));

    // Ambient glow orbs (larger, slower, blurred)
    const orbs = Array.from({ length: 5 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      size: Math.random() * 60 + 30,
      speedX: (Math.random() - 0.5) * 0.15,
      speedY: (Math.random() - 0.5) * 0.1,
      hue: Math.random() > 0.5 ? '168,218,220' : '82,183,136',
      opacity: Math.random() * 0.04 + 0.01,
    }));

    let frame = 0;
    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      frame++;

      // Draw ambient glow orbs
      orbs.forEach((o) => {
        o.x += o.speedX;
        o.y += o.speedY;
        if (o.x < -80) o.x = canvas.width + 80;
        if (o.x > canvas.width + 80) o.x = -80;
        if (o.y < -80) o.y = canvas.height + 80;
        if (o.y > canvas.height + 80) o.y = -80;

        const gradient = ctx.createRadialGradient(o.x, o.y, 0, o.x, o.y, o.size);
        gradient.addColorStop(0, `rgba(${o.hue},${o.opacity})`);
        gradient.addColorStop(1, `rgba(${o.hue},0)`);
        ctx.beginPath();
        ctx.arc(o.x, o.y, o.size, 0, Math.PI * 2);
        ctx.fillStyle = gradient;
        ctx.fill();
      });

      // Draw rising particles
      particles.forEach((p) => {
        p.x += p.speedX;
        p.y += p.speedY;
        if (p.y < -10) {
          p.y = canvas.height + 10;
          p.x = Math.random() * canvas.width;
        }
        if (p.x < -10) p.x = canvas.width + 10;
        if (p.x > canvas.width + 10) p.x = -10;

        const pulse = Math.sin(frame * p.pulseSpeed + p.pulsePhase) * 0.5 + 0.5;
        const alpha = p.opacity * (0.5 + pulse * 0.5);
        const size = p.size * (0.8 + pulse * 0.4);

        ctx.beginPath();
        ctx.arc(p.x, p.y, size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(168,218,220,${alpha})`;
        ctx.fill();
      });

      animId = requestAnimationFrame(draw);
    };
    draw();

    return () => {
      cancelAnimationFrame(animId);
      window.removeEventListener('resize', resize);
    };
  }, []);

  return (
    <div className="wave-bg">
      {/* Canvas particle layer */}
      <canvas
        ref={canvasRef}
        style={{ position: 'absolute', inset: 0, zIndex: 1, pointerEvents: 'none' }}
      />

      {/* Gradient overlay for depth */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          zIndex: 0,
          background: 'radial-gradient(ellipse at 50% 0%, rgba(26,122,138,0.08) 0%, transparent 60%)',
        }}
      />

      {/* SVG Wave Layers — wrapped in a container so nth-child targets correctly */}
      <div style={{ position: 'absolute', inset: 0, zIndex: 0, overflow: 'hidden', pointerEvents: 'none' }}>
        <svg className="wave-layer" style={{ bottom: 0 }} viewBox="0 0 1440 320" preserveAspectRatio="none">
          <defs>
            <linearGradient id="wave1Grad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#1A7A8A" />
              <stop offset="100%" stopColor="#2494A6" />
            </linearGradient>
          </defs>
          <path
            fill="url(#wave1Grad)"
            d="M0,224L48,218.7C96,213,192,203,288,186.7C384,171,480,149,576,160C672,171,768,213,864,218.7C960,224,1056,192,1152,170.7C1248,149,1344,139,1392,133.3L1440,128L1440,320L0,320Z"
          />
        </svg>
        <svg className="wave-layer" style={{ bottom: '-20px' }} viewBox="0 0 1440 320" preserveAspectRatio="none">
          <path
            fill="#0D3B4F"
            d="M0,160L48,176C96,192,192,224,288,213.3C384,203,480,149,576,138.7C672,128,768,160,864,181.3C960,203,1056,213,1152,197.3C1248,181,1344,139,1392,117.3L1440,96L1440,320L0,320Z"
          />
        </svg>
        <svg className="wave-layer" style={{ bottom: '-40px' }} viewBox="0 0 1440 320" preserveAspectRatio="none">
          <path
            fill="#082A38"
            d="M0,256L48,240C96,224,192,192,288,192C384,192,480,224,576,234.7C672,245,768,235,864,213.3C960,192,1056,160,1152,165.3C1248,171,1344,213,1392,234.7L1440,256L1440,320L0,320Z"
          />
        </svg>
        <svg className="wave-layer" style={{ bottom: '-60px' }} viewBox="0 0 1440 320" preserveAspectRatio="none">
          <path
            fill="#051E28"
            d="M0,288L48,272C96,256,192,224,288,218.7C384,213,480,235,576,245.3C672,256,768,256,864,240C960,224,1056,192,1152,186.7C1248,181,1344,203,1392,213.3L1440,224L1440,320L0,320Z"
          />
        </svg>
      </div>
    </div>
  );
};

export default WaveBackground;
