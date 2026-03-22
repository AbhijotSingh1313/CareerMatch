import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { recruitersAPI, jobsAPI, matchingAPI, feedbackAPI } from "../../services/api";
import "./RecruiterDash.css";

const TABS = ["Overview", "Candidates", "Compare"];

const emptyJob = { title: "", description: "", required_skills: "", experience_min: 0, vacancies: 1, ats_required: false, external_link: "", job_type: "full-time", work_mode: "onsite", location: "", salary_range: "", requirements: "", ats_threshold: 30 };

export default function RecruiterDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState("Overview");
  const [profile, setProfile] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);

  // Job form
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyJob);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState("");
  const [editingId, setEditingId] = useState(null);

  // Candidates tab
  const [selectedJob, setSelectedJob] = useState("");
  const [candidates, setCandidates] = useState([]);
  const [candLoading, setCandLoading] = useState(false);
  const [shortlist, setShortlist] = useState(null);
  const [shortlisting, setShortlisting] = useState(false);

  // Compare tab
  const [compareJob, setCompareJob] = useState("");
  const [compareIds, setCompareIds] = useState([]);
  const [compareResult, setCompareResult] = useState(null);
  const [comparing, setComparing] = useState(false);
  const [applications, setApplications] = useState([]);
  const [compareCandidates, setCompareCandidates] = useState([]);
  const [compareLoading, setCompareLoading] = useState(false);

  // Candidate management
  const [viewCandidate, setViewCandidate] = useState(null);
  const [emailModal, setEmailModal] = useState(null);
  const [emailSending, setEmailSending] = useState(false);

  const loadJobs = () => jobsAPI.myJobs().then(setJobs).catch(() => {});

  useEffect(() => {
    async function load() {
      await Promise.allSettled([
        recruitersAPI.getProfile().then(setProfile),
        loadJobs(),
      ]);
      setLoading(false);
    }
    load();
  }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm(p => ({ ...p, [name]: type === "checkbox" ? checked : value }));
  };

  const handleCreateJob = async (e) => {
    e.preventDefault(); setFormError(""); setSubmitting(true);
    try {
      const skills = form.required_skills.split(",").map(s => s.trim()).filter(Boolean);
      const payload = { ...form, required_skills: skills, experience_min: Number(form.experience_min), vacancies: Number(form.vacancies), ats_threshold: Number(form.ats_threshold) };
      if (!payload.external_link) delete payload.external_link;
      if (!payload.location) delete payload.location;
      if (!payload.salary_range) delete payload.salary_range;
      if (!payload.requirements) delete payload.requirements;
      if (editingId) {
        await jobsAPI.update(editingId, payload);
      } else {
        await jobsAPI.create(payload);
      }
      setForm(emptyJob); setShowForm(false); setEditingId(null); loadJobs();
    } catch (err) { setFormError(err.message); }
    finally { setSubmitting(false); }
  };

  const startEdit = (job) => {
    setForm({
      title: job.title || "", description: job.description || "",
      required_skills: (job.required_skills || []).join(", "),
      experience_min: job.experience_min || 0, vacancies: job.vacancies || 1,
      ats_required: job.ats_required || false, external_link: job.external_link || "",
      job_type: job.job_type || "full-time", work_mode: job.work_mode || "onsite",
      location: job.location || "", salary_range: job.salary_range || "",
      requirements: job.requirements || "", ats_threshold: job.ats_threshold || 30,
    });
    setEditingId(job.id); setShowForm(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const cancelForm = () => { setShowForm(false); setEditingId(null); setForm(emptyJob); };

  const handleStatus = async (id, status) => { try { await jobsAPI.updateStatus(id, status); loadJobs(); } catch {} };
  const handleDelete = async (id) => { if (!confirm("Delete this job?")) return; try { await jobsAPI.remove(id); loadJobs(); } catch {} };

  const handleSelectJob = async (jobId) => {
    setSelectedJob(jobId); setCandidates([]); setShortlist(null);
    if (!jobId) return;
    setCandLoading(true);
    try {
      setCandidates(await matchingAPI.candidateMatches(jobId));
      try { setApplications(await feedbackAPI.jobApplications(jobId)); } catch {}
    } catch {}
    finally { setCandLoading(false); }
  };

  const handleShortlist = async () => {
    if (!selectedJob) return;
    setShortlisting(true); setShortlist(null);
    try { setShortlist(await matchingAPI.shortlist(selectedJob)); } catch {}
    finally { setShortlisting(false); }
  };

  const handleCompareJob = async (jobId) => {
    setCompareJob(jobId); setCompareIds([]); setCompareResult(null); setCompareCandidates([]);
    if (!jobId) return;
    setCompareLoading(true);
    try { setCompareCandidates(await matchingAPI.candidateMatches(jobId)); } catch {}
    finally { setCompareLoading(false); }
  };

  const toggleCompare = (id) => {
    setCompareIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const runCompare = async () => {
    if (compareIds.length < 2) return;
    setComparing(true); setCompareResult(null);
    try {
      const result = await matchingAPI.compareCandidates(compareJob, compareIds);
      setCompareResult(result);
      if (result.error) alert(result.error);
    } catch (err) { alert("Compare failed: " + err.message); }
    finally { setComparing(false); }
  };

  const handleLogout = () => { logout(); navigate("/"); };
  if (loading) return <div className="rdash-loader">Loading dashboard...</div>;

  return (
    <div className="rdash">
      <header className="rdash-header">
        <div>
          <h1 className="rdash-title">Recruiter Dashboard</h1>
          <p className="rdash-sub">{profile?.company_name || user.full_name} • {profile?.industry || "Technology"}</p>
        </div>
        <button className="logout-btn" onClick={handleLogout}> Logout</button>
      </header>

      <div className="rdash-tabs">
        {TABS.map(t => <button key={t} className={`rdash-tab ${tab === t ? "active" : ""}`} onClick={() => setTab(t)}>{t}{t === "Compare" ? ` (${compareIds.length})` : ""}</button>)}
      </div>

      {/* ═══ OVERVIEW ═══ */}
      {tab === "Overview" && (
        <div>
          <div className="rdash-topbar">
            <h2>Active Job Postings</h2>
            <button className="new-job-btn" onClick={() => showForm ? cancelForm() : setShowForm(true)}>
              {showForm ? " Cancel" : "+ New Job Posting"}
            </button>
          </div>

          {showForm && (
            <div className="rdash-card form-card">
              <h3 style={{margin: "0 0 16px"}}>{editingId ? " Edit Job" : "Create New Job"}</h3>
              {formError && <div className="form-error">{formError}</div>}
              <form onSubmit={handleCreateJob}>
                <div className="rfield"><label>Job Title *</label><input name="title" value={form.title} onChange={handleChange} placeholder="e.g. Data Scientist" required /></div>
                <div className="rfield"><label>Description</label><textarea name="description" value={form.description} onChange={handleChange} placeholder="Job responsibilities..." rows={3} /></div>
                <div className="rfield"><label>Requirements</label><textarea name="requirements" value={form.requirements} onChange={handleChange} placeholder="• Bachelor's degree&#10;• 2+ years experience" rows={3} /></div>
                <div className="rfield"><label>Required Skills (comma-separated)</label><input name="required_skills" value={form.required_skills} onChange={handleChange} placeholder="Python, ML, SQL..." /></div>
                <div className="rfield-row">
                  <div className="rfield">
                    <label>Job Type</label>
                    <select name="job_type" value={form.job_type} onChange={handleChange}>
                      <option value="full-time">Full-time</option>
                      <option value="part-time">Part-time</option>
                      <option value="contract">Contract</option>
                      <option value="internship">Internship</option>
                      <option value="freelance">Freelance</option>
                    </select>
                  </div>
                  <div className="rfield">
                    <label>Work Mode</label>
                    <select name="work_mode" value={form.work_mode} onChange={handleChange}>
                      <option value="onsite">Onsite</option>
                      <option value="remote">Remote</option>
                      <option value="hybrid">Hybrid</option>
                    </select>
                  </div>
                  <div className="rfield"><label>Location</label><input name="location" value={form.location} onChange={handleChange} placeholder="e.g. NYC" /></div>
                </div>
                <div className="rfield-row">
                  <div className="rfield"><label>Min Experience (years)</label><input name="experience_min" type="number" min="0" value={form.experience_min} onChange={handleChange} /></div>
                  <div className="rfield"><label>Vacancies</label><input name="vacancies" type="number" min="1" value={form.vacancies} onChange={handleChange} /></div>
                  <div className="rfield"><label>Salary Range</label><input name="salary_range" value={form.salary_range} onChange={handleChange} placeholder="$80k - $120k" /></div>
                  <div className="rfield">
                    <label>ATS Auto-Reject Threshold (%)</label>
                    <div style={{display: "flex", alignItems: "center", gap: 8}}>
                      <input name="ats_threshold" type="range" min="10" max="80" value={form.ats_threshold} onChange={handleChange} style={{flex: 1}} />
                      <span style={{fontWeight: 700, color: form.ats_threshold > 50 ? "#ef4444" : "#f59e0b", minWidth: 40, textAlign: "center"}}>{form.ats_threshold}%</span>
                    </div>
                    <span style={{fontSize: 11, color: "#888"}}>Candidates with ATS score below this are auto-rejected</span>
                  </div>
                </div>
                <div className="rfield"><label>External Link (optional)</label><input name="external_link" value={form.external_link} onChange={handleChange} placeholder="https://careers.company.com/job/123" /></div>
                <div style={{display: "flex", gap: 10, marginTop: 12}}>
                  <button type="submit" className="create-btn" disabled={submitting}>{submitting ? (editingId ? "Saving..." : "Creating...") : (editingId ? " Save Changes" : "Create Job")}</button>
                  {editingId && <button type="button" className="new-job-btn" onClick={cancelForm}>Cancel</button>}
                </div>
              </form>
            </div>
          )}

          {jobs.map(job => (
            <div key={job.id} className="rdash-card job-card-r">
              <div className="job-card-main">
                <div>
                  <h3>{job.title}</h3>
                  <p className="job-card-desc">{job.description || "No description"}</p>
                  {job.requirements && <p style={{fontSize: 12, color: "#888", marginTop: 4}}> {job.requirements.substring(0, 120)}{job.requirements.length > 120 ? "..." : ""}</p>}
                  <div className="job-skill-badges">
                    {(job.required_skills || []).map((s, i) => (
                      <span key={i} className="jbadge must">{s}</span>
                    ))}
                  </div>
                  <div style={{display: "flex", gap: 10, flexWrap: "wrap", marginTop: 8, fontSize: 12}}>
                    {job.job_type && <span style={{color: "#6366f1", fontWeight: 600}}> {job.job_type}</span>}
                    {job.work_mode && <span style={{color: "#6366f1"}}> {job.work_mode}</span>}
                    {job.location && <span style={{color: "#888"}}> {job.location}</span>}
                    {job.salary_range && <span style={{color: "#16a34a"}}> {job.salary_range}</span>}
                  </div>
                  {job.external_link && <a href={job.external_link} target="_blank" rel="noreferrer" style={{fontSize: 12, color: "#6366f1", textDecoration: "none", marginTop: 6, display: "inline-block"}}> External Link</a>}
                </div>
                <div className="job-card-right">
                  <span className="exp-pill">{job.experience_min}-{job.experience_min + 2} years</span>
                  <div className="job-actions">
                    <button className="action-edit" onClick={() => startEdit(job)}> Edit</button>
                    {job.status === "open"
                      ? <button className="action-edit" onClick={() => handleStatus(job.id, "closed")}>Close</button>
                      : <button className="action-edit" onClick={() => handleStatus(job.id, "open")}>Reopen</button>}
                    <button className="action-delete" onClick={() => handleDelete(job.id)}>Delete</button>
                  </div>
                </div>
              </div>
            </div>
          ))}
          {jobs.length === 0 && <p className="empty-r">No jobs posted yet. Create your first job posting!</p>}

          <h2 style={{ marginTop: 32, color: "#1a1a2e", fontSize: 18 }}>Top Matching Candidates</h2>
          <p className="empty-r">Select a job from the Candidates tab to see matches.</p>
        </div>
      )}

      {/* ═══ CANDIDATES ═══ */}
      {tab === "Candidates" && (() => {
        // Use per-job ATS threshold
        const currentJob = jobs.find(j => j.id === selectedJob);
        const THRESHOLD = currentJob?.ats_threshold || 30;
        const aboveThreshold = candidates.filter(c => (c.ats_score || 0) >= THRESHOLD);
        const belowThreshold = candidates.filter(c => (c.ats_score || 0) < THRESHOLD);
        return (
        <div>
          <div className="rdash-topbar">
            <select className="job-select" value={selectedJob} onChange={e => handleSelectJob(e.target.value)}>
              <option value="">Select a job posting...</option>
              {jobs.map(j => <option key={j.id} value={j.id}>{j.title}</option>)}
            </select>
            <button className="ai-btn" onClick={handleShortlist} disabled={!selectedJob || shortlisting}>
              {shortlisting ? " AI Shortlisting..." : " AI Shortlist"}
            </button>
          </div>

          {/* Per-Job ATS Threshold Info */}
          {selectedJob && (
            <div className="rdash-card" style={{marginBottom: 16, background: "#f8f9fb"}}>
              <div style={{display: "flex", alignItems: "center", gap: 16, flexWrap: "wrap"}}>
                <span style={{fontWeight: 600, fontSize: 14}}> ATS Auto-Reject Threshold: <span style={{color: "#6366f1", fontSize: 18}}>{THRESHOLD}%</span></span>
                <span style={{fontSize: 12, color: "#888"}}>(Set during job posting — edit the job to change)</span>
              </div>
              {belowThreshold.length > 0 && (
                <p style={{fontSize: 13, color: "#ef4444", marginTop: 8, marginBottom: 0}}>
                   {belowThreshold.length} candidate{belowThreshold.length > 1 ? "s" : ""} auto-rejected (ATS score below {THRESHOLD}%)
                </p>
              )}
            </div>
          )}



          {/* Candidate List (only above threshold) */}
          {candLoading ? <div className="rdash-loader">Ranking candidates...</div> : (
            <div className="cand-list">
              <h3 style={{margin: "0 0 12px"}}> All Candidates Above Threshold ({aboveThreshold.length})</h3>
              {aboveThreshold.map((item, i) => {
                const app = applications.find(a => a.candidate_id === item.candidate.id);
                return (
                <div key={i} className="rdash-card cand-card">
                  <div className="cand-main">
                    <div style={{flex: 1}}>
                      <h3 style={{margin: "0 0 4px"}}>{item.candidate.full_name}</h3>
                      <p className="cand-email">{item.candidate.email}</p>
                      <div className="cand-tags">
                        {item.explanation.matched_skills.map((s, j) => <span key={j} className="jbadge must">{s}</span>)}
                        {item.explanation.missing_skills.map((s, j) => <span key={j} className="jbadge miss">{s}</span>)}
                      </div>
                      <div style={{display: "flex", gap: 8, marginTop: 6, fontSize: 11}}>
                        <span style={{color: "#6366f1", fontWeight: 600}}>ATS: {item.ats_score || 0}%</span>
                        {app && <span style={{color: app.status === "accepted" ? "#16a34a" : app.status === "rejected" ? "#ef4444" : "#888", fontWeight: 600}}>Status: {app.status}</span>}
                      </div>
                    </div>
                    <div style={{display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6}}>
                      <span className="cand-score">{item.score}%</span>
                      <div style={{display: "flex", gap: 6}}>
                        <button className="action-edit" style={{fontSize: 11, padding: "4px 10px"}} onClick={() => setViewCandidate(item)}> View</button>
                        <button className="action-edit" style={{fontSize: 11, padding: "4px 10px", background: "#ecfdf5", color: "#16a34a"}}
                          onClick={() => setEmailModal({
                            candidate_email: app?.candidate_email || item.candidate.email,
                            candidate_name: item.candidate.full_name,
                            job_title: jobs.find(j => j.id === selectedJob)?.title || "",
                            status: "accepted",
                            appId: app?.id || null
                          })}></button>
                        <button className="action-delete" style={{fontSize: 11, padding: "4px 10px"}}
                          onClick={() => setEmailModal({
                            candidate_email: app?.candidate_email || item.candidate.email,
                            candidate_name: item.candidate.full_name,
                            job_title: jobs.find(j => j.id === selectedJob)?.title || "",
                            status: "rejected",
                            appId: app?.id || null
                          })}></button>
                      </div>
                    </div>
                  </div>
                </div>
                );
              })}
            </div>
          )}
          {selectedJob && !candLoading && candidates.length === 0 && <p className="empty-r">No candidates found.</p>}

          {/* Candidate Detail Modal */}
          {viewCandidate && (
            <div className="job-modal-overlay" onClick={() => setViewCandidate(null)}>
              <div className="job-modal" onClick={e => e.stopPropagation()} style={{maxWidth: 600}}>
                <button className="job-modal-close" onClick={() => setViewCandidate(null)}></button>
                <h2>{viewCandidate.candidate.full_name}</h2>
                <p style={{color: "#888", margin: "4px 0 12px"}}>{viewCandidate.candidate.email}</p>
                <div style={{display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16}}>
                  <span className="exp-pill">Score: {viewCandidate.score}%</span>
                  <span className="exp-pill">Skill Match: {viewCandidate.explanation.skill_match}%</span>
                  <span className="exp-pill">Exp Match: {viewCandidate.explanation.experience_match}%</span>
                </div>
                <div style={{marginBottom: 12}}>
                  <h4 style={{margin: "0 0 6px"}}> Matched Skills</h4>
                  <div className="cand-tags">{viewCandidate.explanation.matched_skills.map((s, i) => <span key={i} className="jbadge must">{s}</span>)}</div>
                </div>
                <div style={{marginBottom: 12}}>
                  <h4 style={{margin: "0 0 6px"}}> Missing Skills</h4>
                  <div className="cand-tags">{viewCandidate.explanation.missing_skills.map((s, i) => <span key={i} className="jbadge miss">{s}</span>)}</div>
                </div>
                {viewCandidate.candidate.career_goal && (
                  <p style={{fontSize: 14, color: "#555"}}><strong>Career Goal:</strong> {viewCandidate.candidate.career_goal}</p>
                )}
                {viewCandidate.candidate.experience_years != null && (
                  <p style={{fontSize: 14, color: "#555"}}><strong>Experience:</strong> {viewCandidate.candidate.experience_years} years</p>
                )}
                {viewCandidate.candidate.education && (
                  <p style={{fontSize: 14, color: "#555"}}><strong>Education:</strong> {viewCandidate.candidate.education}</p>
                )}
                <div style={{display: "flex", gap: 8, marginTop: 16}}>
                  <button className="create-btn" style={{fontSize: 12, padding: "8px 16px"}} onClick={async () => {
                    try {
                      await feedbackAPI.downloadResume(viewCandidate.candidate.id, viewCandidate.candidate.full_name);
                    } catch (err) { alert("Could not download resume: " + err.message); }
                  }}> Download Resume</button>
                  <button className="new-job-btn" onClick={() => setViewCandidate(null)}>Close</button>
                </div>
              </div>
            </div>
          )}

          {/* Email Modal */}
          {emailModal && (
            <div className="job-modal-overlay" onClick={() => setEmailModal(null)}>
              <div className="job-modal" onClick={e => e.stopPropagation()} style={{maxWidth: 550}}>
                <button className="job-modal-close" onClick={() => setEmailModal(null)}></button>
                <h2>{emailModal.status === "accepted" ? " Accept" : " Reject"} Candidate</h2>
                <p style={{color: "#888", margin: "4px 0 16px"}}>Send {emailModal.status} email to <strong>{emailModal.candidate_name}</strong> ({emailModal.candidate_email})</p>
                <div className="rfield">
                  <label>Custom Message (leave blank for default)</label>
                  <textarea
                    rows={5}
                    value={emailModal.customMsg || ""}
                    onChange={e => setEmailModal(prev => ({...prev, customMsg: e.target.value}))}
                    placeholder={emailModal.status === "accepted"
                      ? `Dear ${emailModal.candidate_name},\n\nCongratulations! We are pleased to inform you that your application for ${emailModal.job_title} has been accepted.\n\nInterview Date: [DATE]\nLocation: [LOCATION/LINK]\n\nBest regards`
                      : `Dear ${emailModal.candidate_name},\n\nThank you for your interest in ${emailModal.job_title}. After careful review, we have decided to proceed with other candidates.\n\nWe wish you all the best.`
                    }
                  />
                </div>
                <div style={{display: "flex", gap: 8, marginTop: 12}}>
                  <button className="create-btn" disabled={emailSending} onClick={async () => {
                    setEmailSending(true);
                    try {
                      // Update application status
                      if (emailModal.appId) {
                        await feedbackAPI.updateApplication(emailModal.appId, emailModal.status);
                      }
                      // Send email (real SMTP + in-app feedback)
                      const result = await feedbackAPI.sendEmail({
                        candidate_email: emailModal.candidate_email,
                        candidate_name: emailModal.candidate_name,
                        job_title: emailModal.job_title,
                        status: emailModal.status,
                        custom_message: emailModal.customMsg || null,
                      });
                      const emailNote = result.email_sent ? "Real email sent!" : `Email not sent (${result.email_error || "SMTP not configured"}) — saved as in-app feedback`;
                      alert(`${emailModal.status === "accepted" ? "Accepted" : "Rejected"}! ${emailNote}`);
                      setEmailModal(null);
                      handleSelectJob(selectedJob);
                    } catch (err) { alert("Error: " + err.message); }
                    finally { setEmailSending(false); }
                  }}>
                    {emailSending ? "Sending..." : `${emailModal.status === "accepted" ? "Accept & Send Email" : "Reject & Send Email"}`}
                  </button>
                  <button className="new-job-btn" onClick={() => setEmailModal(null)}>Cancel</button>
                </div>
              </div>
            </div>
          )}
        </div>
        );
      })()}

      {/* ═══ COMPARE ═══ */}
      {tab === "Compare" && (
        <div>
          <div className="rdash-topbar">
            <select className="job-select" value={compareJob} onChange={e => handleCompareJob(e.target.value)}>
              <option value="">Select a job to compare candidates...</option>
              {jobs.map(j => <option key={j.id} value={j.id}>{j.title}</option>)}
            </select>
            <button className="ai-btn" onClick={runCompare} disabled={compareIds.length < 2 || comparing}>
              {comparing ? "Comparing..." : ` AI Compare (${compareIds.length} selected)`}
            </button>
          </div>

          {compareLoading && <div className="rdash-loader">Loading candidates...</div>}

          {!compareLoading && compareCandidates.length > 0 && (
            <div className="rdash-card" style={{marginBottom: 20}}>
              <h3 style={{margin: "0 0 12px"}}>Select 2+ candidates to compare</h3>
              <p style={{fontSize: 12, color: "#888", margin: "0 0 12px"}}>Check the candidates you want AI to compare side by side</p>
              {compareCandidates.map((item, i) => (
                <label key={i} className="compare-check">
                  <input type="checkbox" checked={compareIds.includes(item.candidate.id)} onChange={() => toggleCompare(item.candidate.id)} />
                  <span style={{flex: 1}}>
                    <strong>{item.candidate.full_name}</strong>
                    <span style={{color: "#888", marginLeft: 8}}>({item.candidate.email})</span>
                  </span>
                  <span style={{display: "flex", gap: 8, flexShrink: 0}}>
                    <span className="jbadge must">Match: {item.score}%</span>
                    <span className="jbadge" style={{background: "#fef3c7", color: "#92400e"}}>ATS: {item.ats_score || 0}%</span>
                  </span>
                </label>
              ))}
            </div>
          )}

          {compareResult && compareResult.ranking && (
            <div className="rdash-card">
              <h3> AI Comparison Results</h3>
              {compareResult.ranking.map((r, i) => (
                <div key={i} className="compare-row">
                  <div className="compare-rank">#{r.rank}</div>
                  <div className="compare-info">
                    <strong>{r.candidate_name}</strong>
                    <span className={`rec-badge ${r.recommendation}`}>{r.recommendation}</span>
                    <p className="compare-reasoning">{r.reasoning}</p>
                    <div className="compare-tags">
                      {(r.strengths || []).map((s, j) => <span key={j} className="jbadge must">{s}</span>)}
                      {(r.weaknesses || []).map((s, j) => <span key={j} className="jbadge miss">{s}</span>)}
                    </div>
                  </div>
                  <span className="cand-score">{r.fit_score}%</span>
                </div>
              ))}
              {compareResult.comparison_summary && (
                <div className="compare-summary"><p>{compareResult.comparison_summary}</p></div>
              )}
            </div>
          )}

          {compareResult && compareResult.error && (
            <div className="rdash-card" style={{background: "#fef2f2", border: "1px solid #fecaca"}}>
              <p style={{color: "#dc2626"}}> {compareResult.error}</p>
            </div>
          )}

          {compareJob && !compareLoading && compareCandidates.length === 0 && <p className="empty-r">No candidates found for this job.</p>}
        </div>
      )}
    </div>
  );
}
