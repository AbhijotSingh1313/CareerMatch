import { useState, useEffect } from "react";
import { jobsAPI, matchingAPI, feedbackAPI } from "../../services/api";
import "../Dashboard.css";

export default function Candidates() {
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [shortlist, setShortlist] = useState(null);
  const [loading, setLoading] = useState(false);
  const [shortlisting, setShortlisting] = useState(false);
  const [statusMsg, setStatusMsg] = useState({});

  useEffect(() => { jobsAPI.myJobs().then(setJobs).catch(() => {}); }, []);

  const handleSelectJob = async (jobId) => {
    setSelectedJob(jobId); setShortlist(null); setCandidates([]);
    if (!jobId) return;
    setLoading(true);
    try {
      const matches = await matchingAPI.candidateMatches(jobId);
      setCandidates(matches);
    } catch {}
    finally { setLoading(false); }
  };

  const handleShortlist = async () => {
    if (!selectedJob) return;
    setShortlisting(true); setShortlist(null);
    try {
      const result = await matchingAPI.shortlist(selectedJob);
      setShortlist(result);
    } catch {}
    finally { setShortlisting(false); }
  };

  const updateStatus = async (applicationId, status) => {
    try {
      await feedbackAPI.updateApplication(applicationId, status);
      setStatusMsg((p) => ({ ...p, [applicationId]: ` ${status}` }));
    } catch (err) {
      setStatusMsg((p) => ({ ...p, [applicationId]: `Error: ${err.message}` }));
    }
  };

  return (
    <div className="dashboard">
      <div className="dash-header">
        <h1> <span className="gradient-text">Candidate Matching</span></h1>
        <p>AI-powered candidate ranking and shortlisting</p>
      </div>

      {/* Job selector */}
      <div className="card" style={{ marginBottom: 28, display: "flex", gap: 12, alignItems: "center" }}>
        <select
          style={{ flex: 1, padding: "12px 16px", borderRadius: 12, border: "1.5px solid rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.05)", color: "#fff", fontSize: 14, outline: "none", fontFamily: "Inter, sans-serif" }}
          value={selectedJob}
          onChange={(e) => handleSelectJob(e.target.value)}
        >
          <option value="">Select a job posting...</option>
          {jobs.map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
        </select>
        <button className="btn-primary" onClick={handleShortlist} disabled={!selectedJob || shortlisting}>
          {shortlisting ? "AI Shortlisting..." : " AI Shortlist"}
        </button>
      </div>

      {/* AI Shortlist result */}
      {shortlist && (
        <div className="dash-section">
          <h2> AI Shortlist Results</h2>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <div>
              <h4 style={{ color: "#66bb6a", marginBottom: 12 }}> Shortlisted</h4>
              {(shortlist.shortlisted || []).map((c, i) => (
                <div key={i} className="card" style={{ marginBottom: 12, padding: "16px 20px" }}>
                  <p style={{ color: "#fff", fontWeight: 600 }}>{c.candidate_name}</p>
                  <p style={{ color: "rgba(255,255,255,0.55)", fontSize: 13, marginTop: 6 }}>{c.reason}</p>
                </div>
              ))}
            </div>
            <div>
              <h4 style={{ color: "#ff5252", marginBottom: 12 }}> Not shortlisted</h4>
              {(shortlist.rejected || []).map((c, i) => (
                <div key={i} className="card" style={{ marginBottom: 12, padding: "16px 20px" }}>
                  <p style={{ color: "#fff", fontWeight: 600 }}>{c.candidate_name}</p>
                  <p style={{ color: "rgba(255,255,255,0.55)", fontSize: 13, marginTop: 6 }}>{c.reason}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* All ranked candidates */}
      {loading ? (
        <div className="dash-loading">Ranking candidates with AI...</div>
      ) : candidates.length > 0 ? (
        <div className="dash-section">
          <h2> All Candidates — Ranked by Match</h2>
          <div className="match-cards">
            {candidates.map((item, i) => (
              <div key={i} className="match-card">
                <span className="match-score-badge">{item.score}%</span>
                <h3>{item.candidate.full_name}</h3>
                <p className="match-skills">{item.candidate.email}</p>
                <p className="match-skills" style={{ marginTop: 4 }}>
                  Matched: {item.explanation.matched_skills.join(", ") || "—"}
                </p>
                {item.explanation.missing_skills.length > 0 && (
                  <p className="match-missing">Missing: {item.explanation.missing_skills.join(", ")}</p>
                )}
              </div>
            ))}
          </div>
        </div>
      ) : selectedJob && !loading ? (
        <p className="empty-state">No candidates found for this job.</p>
      ) : null}
    </div>
  );
}
