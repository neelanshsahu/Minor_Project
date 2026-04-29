import axios from 'axios';

// Use relative URL so Vite's dev proxy handles routing to the backend.
// In production, the API should be served from the same origin or configured via env.
const API_BASE = '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ===== Session Management =====

export const initSession = async (numParties = 3, threshold = 2, recordsPerParty = 100) => {
  const { data } = await api.post('/init-session', {
    num_parties: numParties,
    threshold,
    records_per_party: recordsPerParty,
  });
  return data;
};

export const getSession = async (sessionId) => {
  const { data } = await api.get(`/session/${sessionId}`);
  return data;
};

export const listSessions = async () => {
  const { data } = await api.get('/sessions');
  return data;
};

// ===== Share Operations =====

export const uploadShares = async (sessionId, partyId, field = 'age') => {
  const { data } = await api.post('/upload-shares', {
    session_id: sessionId,
    party_id: partyId,
    field,
  });
  return data;
};

// ===== Computation =====

export const computeAggregate = async (sessionId, operation = 'average', field = 'age') => {
  const { data } = await api.get('/compute-aggregate', {
    params: { session_id: sessionId, operation, field },
  });
  return data;
};

export const getResult = async (sessionId) => {
  const { data } = await api.get('/get-result', {
    params: { session_id: sessionId },
  });
  return data;
};

// ===== Protocol Simulation =====

export const simulateProtocol = async (numParties = 3, recordsPerParty = 20, field = 'age') => {
  const { data } = await api.post(`/simulate-protocol?num_parties=${numParties}&records_per_party=${recordsPerParty}&field=${field}`);
  return data;
};

// ===== Audit & Reports =====

export const getAuditLog = async (sessionId = null, limit = 100) => {
  const params = { limit };
  if (sessionId) params.session_id = sessionId;
  const { data } = await api.get('/audit-log', { params });
  return data;
};

export const getEvaluationReport = async (format = 'json') => {
  const { data } = await api.get('/evaluation-report', {
    params: { format },
  });
  return data;
};

// ===== Report Storage =====

export const saveReport = async (reportData, reportName = null) => {
  const { data } = await api.post('/save-report', {
    report_data: reportData,
    report_name: reportName,
  });
  return data;
};

export const listReports = async () => {
  const { data } = await api.get('/reports');
  return data;
};

export const downloadReport = async (filename) => {
  const { data } = await api.get(`/reports/${filename}`);
  return data;
};

// ===== ZKP =====

export const generateZKP = async (value, proofType = 'threshold', options = {}) => {
  const { data } = await api.post('/zkp/generate', {
    value,
    proof_type: proofType,
    ...options,
  });
  return data;
};

export const verifyZKP = async (proof) => {
  const { data } = await api.post('/zkp/verify', proof);
  return data;
};

// ===== Garbled Circuit =====

export const runGarbledCircuit = async (value, thresholdValue = 140, bitWidth = 8) => {
  const { data } = await api.post('/garbled-circuit', {
    value,
    threshold_value: thresholdValue,
    bit_width: bitWidth,
  });
  return data;
};

// ===== Security Metrics =====

export const getSecurityMetrics = async () => {
  const { data } = await api.get('/security-metrics');
  return data;
};

// ===== Data Summary =====

export const getDataSummary = async (sessionId) => {
  const { data } = await api.get(`/data-summary/${sessionId}`);
  return data;
};

export default api;
