const API_BASE = import.meta.env.VITE_API_BASE || "http://127.0.0.1:8000";

function getToken() {
  return localStorage.getItem("access_token");
}

async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    ...(options.headers || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || JSON.stringify(err));
  }

  return res.json();
}

// ─── Auth ───
export const authAPI = {
  signup: (data) => request("/auth/signup", { method: "POST", body: JSON.stringify(data) }),
  login: (data) => request("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  me: () => request("/auth/me"),
};

// ─── Candidates ───
export const candidatesAPI = {
  getProfile: () => request("/candidates/profile"),
  updateProfile: (data) => request("/candidates/profile", { method: "PUT", body: JSON.stringify(data) }),
  uploadResume: (file) => {
    const formData = new FormData();
    formData.append("file", file);
    return request("/candidates/resume/upload", { method: "POST", body: formData });
  },
  getResumeAnalysis: () => request("/candidates/resume/analysis"),
  reanalyzeResume: (targetRole = "") => request(`/candidates/resume/reanalyze?target_role=${encodeURIComponent(targetRole)}`, { method: "POST" }),
  chat: (message, history = []) => request("/candidates/chat", { method: "POST", body: JSON.stringify({ message, history }) }),
};

// ─── Recruiters ───
export const recruitersAPI = {
  getProfile: () => request("/recruiters/profile"),
  updateProfile: (data) => request("/recruiters/profile", { method: "PUT", body: JSON.stringify(data) }),
};

// ─── Jobs ───
export const jobsAPI = {
  listOpen: () => request("/jobs/"),
  getJob: (id) => request(`/jobs/${id}`),
  create: (data) => request("/jobs/", { method: "POST", body: JSON.stringify(data) }),
  myJobs: () => request("/jobs/my-jobs"),
  update: (id, data) => request(`/jobs/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  remove: (id) => request(`/jobs/${id}`, { method: "DELETE" }),
  updateStatus: (id, status) => request(`/jobs/${id}/status?status=${status}`, { method: "PUT" }),
  apply: (id) => request(`/jobs/${id}/apply`, { method: "POST" }),
  save: (id) => request(`/jobs/${id}/save`, { method: "POST" }),
  unsave: (id) => request(`/jobs/${id}/save`, { method: "DELETE" }),
  getSaved: () => request("/jobs/saved"),
};

// ─── Matching ───
export const matchingAPI = {
  jobMatches: () => request("/matching/jobs"),
  candidateMatches: (jobId) => request(`/matching/candidates/${jobId}`),
  compareCandidates: (jobId, ids) => request(`/matching/compare/${jobId}`, { method: "POST", body: JSON.stringify(ids) }),
  shortlist: (jobId, max = 5, threshold = 30) => request(`/matching/shortlist/${jobId}?max_candidates=${max}`),
};

// ─── Skills ───
export const skillsAPI = {
  gaps: (role = "") => request(`/skills/gaps?target_role=${encodeURIComponent(role)}`),
  courses: () => request("/skills/courses"),
  careerPath: () => request("/skills/career-path"),
};

// ─── Feedback ───
export const feedbackAPI = {
  send: (data) => request("/feedback/send", { method: "POST", body: JSON.stringify(data) }),
  myFeedback: () => request("/feedback/my-feedback"),
  updateApplication: (appId, status) =>
    request(`/feedback/applications/${appId}`, { method: "PUT", body: JSON.stringify({ status }) }),
  jobApplications: (jobId) => request(`/feedback/applications/${jobId}`),
  batchUpdate: (applicationIds, status) =>
    request("/feedback/applications/batch-update", { method: "POST", body: JSON.stringify({ application_ids: applicationIds, status }) }),
  sendEmail: (data) =>
    request("/feedback/applications/send-email", { method: "POST", body: JSON.stringify(data) }),
  downloadResume: async (candidateId, candidateName) => {
    const token = getToken();
    const res = await fetch(`${API_BASE}/feedback/resume/${candidateId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("No resume found");
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `resume_${(candidateName || "candidate").replace(/\s+/g, "_")}.txt`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  },
};
