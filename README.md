# 🔒 MediVault — Secure Health Data Collaboration

> A full-stack **Secure Multi-Party Computation (SMPC)** system for confidential healthcare data sharing. Multiple healthcare parties can collaboratively compute aggregate statistics on patient data **without ever revealing individual records**.

![Status](https://img.shields.io/badge/status-fully%20offline-brightgreen)
![Python](https://img.shields.io/badge/python-3.9+-blue)
![React](https://img.shields.io/badge/react-18-61dafb)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React + Vite)                  │
│  ┌──────────┐  ┌───────────┐  ┌─────────┐  ┌───────┐          │
│  │  Login   │  │ Dashboard │  │ Theater │  │Results│  │Audit│  │
│  └──────────┘  └───────────┘  └─────────┘  └───────┘          │
│         │              │             │           │              │
│         └──────────────┴─────────────┴───────────┘              │
│                          Axios API Client                       │
└──────────────────────────────┬──────────────────────────────────┘
                               │ HTTP (localhost:8000)
┌──────────────────────────────┴──────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────┐   │
│  │  SMPC Modules   │  │  Synthetic Data  │  │  Evaluation  │   │
│  │  ├ secret_share  │  │  └ generator.py  │  │  ├ benchmarks│   │
│  │  ├ aggregation   │  └──────────────────┘  │  └ report_gen│   │
│  │  ├ garbled_circ  │                        └──────────────┘   │
│  │  ├ homomorphic   │                                           │
│  │  └ zkp           │                                           │
│  └─────────────────┘                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## ⚙️ SMPC Modules

### 1. 🔑 Shamir's Secret Sharing (`secret_sharing.py`)
- Splits patient data (age, vitals, diagnosis codes) into **n shares**
- Reconstructs only when **k-of-n** parties participate
- Operates over GF(2¹²⁷ - 1) finite field
- Functions: `split_secret()`, `reconstruct_secret()`, `verify_share()`, `split_record()`

### 2. 📈 Secure Aggregation (`aggregation.py`)
- Computes **sum, average, count** on encrypted shares WITHOUT decrypting
- Leverages the additive homomorphism of Shamir shares
- Functions: `secure_sum()`, `secure_average()`, `secure_count()`, `compute_frequency_distribution()`

### 3. ⚡ Garbled Circuit Simulation (`garbled_circuit.py`)
- Simulates garbled circuits for comparison operations
- Example: "Is avg blood pressure > 140?" without revealing individual values
- Functions: `create_garbled_circuit()`, `evaluate_circuit()`, `compare_threshold()`

### 4. 🔢 Homomorphic Encryption (`homomorphic.py`)
- Encrypts numerical patient data (supports TenSEAL CKKS / simulated fallback)
- Performs addition and multiplication on ciphertext
- Decrypts only the final result
- Functions: `he_encrypt()`, `he_add()`, `he_multiply()`, `he_decrypt()`

### 5. 🛡️ Zero-Knowledge Proofs (`zkp.py`)
- Prove a patient's age is above 18 without revealing exact age
- Prove diagnosis code falls in a valid range without revealing code
- Schnorr-like discrete log commitment scheme
- Functions: `generate_proof()`, `verify_proof()`

---

## 🌊 UI Design

The UI theme evokes a **calm, serene ocean at dawn**:

| Token | Color | Usage |
|-------|-------|-------|
| Deep Ocean | `#0D3B4F` | Card backgrounds |
| Teal | `#1A7A8A` | Primary accents |
| Seafoam | `#A8DADC` | Text, borders |
| Pearl White | `#F1FAEE` | Body text |
| Calm Green | `#52B788` | Success states |

**Design features:**
- Glassmorphism cards with `backdrop-filter: blur(12px)`
- Animated SVG wave layers + canvas particle system
- Pulsing node animations during computation
- Encryption shield glow effects
- Ripple loading states (no spinners)
- Dark mode only
- Typography: Inter (body) + DM Serif Display (headings)

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/init-session` | Initialize SMPC session with N parties |
| `POST` | `/api/upload-shares` | Party uploads their encrypted shares |
| `GET` | `/api/compute-aggregate` | Trigger secure aggregation |
| `GET` | `/api/get-result` | Return final decrypted aggregate result |
| `GET` | `/api/audit-log` | Fetch all computation event logs |
| `GET` | `/api/evaluation-report` | Fetch performance benchmarks |
| `POST` | `/api/simulate-protocol` | Run full SMPC protocol end-to-end |
| `POST` | `/api/zkp/generate` | Generate a zero-knowledge proof |
| `POST` | `/api/zkp/verify` | Verify a zero-knowledge proof |
| `POST` | `/api/garbled-circuit` | Run garbled circuit comparison |
| `GET` | `/api/security-metrics` | Get security evaluation metrics |

---

## 📁 Folder Structure

```
medivault/
├── frontend/                   # React + Vite + TailwindCSS
│   ├── src/
│   │   ├── pages/              # Login, Dashboard, ComputationTheater, Results, Audit
│   │   ├── components/         # WaveBackground, NodeGraph, EncryptionShield, Charts, HowItWorksModal
│   │   ├── api/                # Axios client (client.js)
│   │   ├── App.jsx             # Root component with routing
│   │   ├── main.jsx            # Entry point
│   │   └── index.css           # Ocean-dawn design system
│   ├── index.html              # HTML with SEO meta tags
│   ├── package.json
│   ├── tailwind.config.js      # Custom theme tokens
│   └── vite.config.js          # Dev server + API proxy
├── backend/                    # Python FastAPI
│   ├── smpc/                   # SMPC protocol modules
│   │   ├── secret_sharing.py   # Shamir's (k,n) threshold scheme
│   │   ├── aggregation.py      # Secure sum/average/count
│   │   ├── garbled_circuit.py  # Garbled circuit simulation
│   │   ├── homomorphic.py      # HE (TenSEAL / simulated)
│   │   └── zkp.py              # Zero-knowledge proofs
│   ├── data/
│   │   └── synthetic_generator.py  # Faker-based patient data
│   ├── evaluation/
│   │   ├── benchmarks.py       # Performance benchmarks
│   │   └── report_generator.py # HTML/JSON report output
│   ├── main.py                 # FastAPI entry point
│   └── requirements.txt
├── notebooks/                  # Jupyter notebooks (conceptual)
│   └── smpc_concepts.ipynb
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies API to localhost:8000)
npm run dev
```

### 3. Open in Browser

Navigate to **http://localhost:5173**

---

## 🔄 SMPC Protocol Flow

```
Step 1 → Each party generates local Shamir shares of their private data
Step 2 → Shares are exchanged over simulated secure channels (TLS mock)
Step 3 → Aggregation is computed directly on encrypted shares
Step 4 → Final result is reconstructed — only the aggregate is revealed
```

**Privacy guarantee:** Individual patient records are NEVER decrypted during computation.

---

## ⚠️ Important Notes

- **All patient data is SYNTHETIC/FAKE** — generated using Faker for demonstration
- The system works **fully offline** — no external API calls
- Homomorphic encryption uses a simulated backend by default; install `tenseal` for real HE
- This is an educational/research prototype, not production-ready

---

## 📊 Performance

The evaluation module benchmarks:
- **Secret Sharing:** Split/reconstruct time vs number of parties (3-10)
- **Secure Aggregation:** Sum/average time vs party count and data size
- **Garbled Circuits:** Circuit creation/evaluation time vs bit width (4-16)
- **Homomorphic Encryption:** Encrypt/add/decrypt time vs vector size
- **Zero-Knowledge Proofs:** Generation/verification time per proof type
- **Security Metrics:** Share entropy, reconstruction accuracy, info-theoretic guarantees

---

## 🛡️ Security Properties

| Property | Status |
|----------|--------|
| Information-theoretic security | ✅ Proven (Shamir's scheme) |
| k-1 share collusion resistance | ✅ Any k-1 shares reveal nothing |
| Reconstruction accuracy | ✅ 100% (exact over finite field) |
| Share randomness | ✅ High entropy verified |

---

*Built with ❤️ for secure healthcare collaboration*
