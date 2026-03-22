import { useState, useEffect } from "react";
import { jobsAPI } from "../../services/api";
import "../Dashboard.css";

export default function CandidateJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [applying, setApplying] = useState({});
  const [messages, setMessages] = useState({});

  useEffect(() => {
    jobsAPI.listOpen()
      .then(setJobs)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleApply = async (jobId) => {
    setApplying((p) => ({ ...p, [jobId]: true }));
    try {
      await jobsAPI.apply(jobId);
      setMessages((p) => ({ ...p, [jobId]: { type: "success", text: "Application submitted!" } }));
    } catch (err) {
      setMessages((p) => ({ ...p, [jobId]: { type: "error", text: err.message } }));
    } finally {
      setApplying((p) => ({ ...p, [jobId]: false }));
    }
  };

  if (loading) return <div className="dash-loading">Loading jobs...</div>;

  return (
    <div className="dashboard">
      <div className="dash-header">
        <h1> <span className="gradient-text">Open Jobs</span></h1>
        <p>{jobs.length} open positions available</p>
      </div>

      <div className="match-cards">
        {jobs.map((job) => (
          <div key={job.id} className="match-card job-card">
            <span className="match-score-badge">{job.status}</span>
            <h3>{job.title}</h3>
            <p className="match-skills">{job.description || "No description provided."}</p>

            <div className="job-meta">
              <span> Min. {job.experience_min}y exp</span>
              <span> {job.vacancies} opening{job.vacancies !== 1 ? "s" : ""}</span>
              {job.ats_required && <span> ATS Required</span>}
            </div>

            {job.required_skills?.length > 0 && (
              <div className="skill-tags" style={{ marginTop: 12 }}>
                {job.required_skills.map((s, i) => (
                  <span key={i} className="skill-tag" style={{ background: "rgba(0,212,255,0.08)", border: "1px solid rgba(0,212,255,0.2)", color: "#00d4ff", fontSize: 12 }}>{s}</span>
                ))}
              </div>
            )}

            {messages[job.id] && (
              <div className={`alert alert-${messages[job.id].type}`} style={{ marginTop: 12, marginBottom: 0 }}>
                {messages[job.id].text}
              </div>
            )}

            <button
              className="btn-primary"
              style={{ width: "100%", marginTop: 16 }}
              onClick={() => handleApply(job.id)}
              disabled={!!applying[job.id] || messages[job.id]?.type === "success"}
            >
              {applying[job.id] ? "Applying..." : messages[job.id]?.type === "success" ? " Applied" : "Apply Now"}
            </button>
          </div>
        ))}
        {jobs.length === 0 && <p className="empty-state">No open jobs right now. Check back later!</p>}
      </div>
    </div>
  );
}
