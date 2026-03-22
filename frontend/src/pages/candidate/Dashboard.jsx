import { useState, useEffect } from "react";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { candidatesAPI, matchingAPI, skillsAPI, jobsAPI, feedbackAPI } from "../../services/api";
import ProfileSetup from "./ProfileSetup";
import "./CandidateDash.css";

const TABS = ["Overview", "Job Matches", "Skill Analysis", "Courses", "Resume Checker", "Career Path", "Feedback"];

export default function CandidateDashboard() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [tab, setTab] = useState("Overview");
  const [profile, setProfile] = useState(null);
  const [matches, setMatches] = useState([]);
  const [gaps, setGaps] = useState(null);
  const [courses, setCourses] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [feedback, setFeedback] = useState([]);
  const [allJobs, setAllJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showSetup, setShowSetup] = useState(false);
  const [careerPath, setCareerPath] = useState(null);
  const [cpLoading, setCpLoading] = useState(false);

  // Resume upload state
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState("");

  // Skills target role
  const [targetRole, setTargetRole] = useState("");
  const [gapsLoading, setGapsLoading] = useState(false);

  // Apply state
  const [applying, setApplying] = useState({});
  const [applyMsg, setApplyMsg] = useState({});

  // Bookmark + modal state
  const [savedJobs, setSavedJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);

  // Resume checker
  const [dragOver, setDragOver] = useState(false);
  const [saveResume, setSaveResume] = useState(true);
  const [resumeTargetRole, setResumeTargetRole] = useState("");

  const loadAll = async () => {
    const [p, m, g, c, a, f, j, sv] = await Promise.allSettled([
      candidatesAPI.getProfile(),
      matchingAPI.jobMatches(),
      skillsAPI.gaps(),
      skillsAPI.courses(),
      candidatesAPI.getResumeAnalysis(),
      feedbackAPI.myFeedback(),
      jobsAPI.listOpen(),
      jobsAPI.getSaved(),
    ]);
    if (p.status === "fulfilled") {
      setProfile(p.value);
      if (!p.value.profile_complete) setShowSetup(true);
    }
    if (m.status === "fulfilled") setMatches(m.value);
    if (g.status === "fulfilled") setGaps(g.value);
    if (c.status === "fulfilled") setCourses(c.value);
    if (a.status === "fulfilled") setAnalysis(a.value);
    if (f.status === "fulfilled") setFeedback(f.value);
    if (j.status === "fulfilled") setAllJobs(j.value);
    if (sv.status === "fulfilled") setSavedJobs(sv.value);
    setLoading(false);
  };

  useEffect(() => { loadAll(); }, []);

  const handleProfileDone = () => {
    setShowSetup(false);
    loadAll();
  };

  const _mapResult = (result) => ({
    parsed_skills: result.analysis?.skills || [],
    parsed_education: result.analysis?.education || "Not detected",
    parsed_experience: result.analysis?.experience || [],
    ats_score: result.ats?.ats_score ?? result.ats?.score ?? null,
    ai_detection_score: result.ats?.ai_detection_score ?? null,
    suggestions: result.ats?.suggestions || [],
    formatting_issues: result.ats?.formatting_issues || [],
    overall_assessment: result.ats?.overall_assessment || "",
    section_scores: result.ats?.section_scores || {},
    keyword_analysis: result.ats?.keyword_analysis || {},
    role_fit: result.ats?.role_fit || {},
  });

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true); setUploadMsg("");
    try {
      const result = await candidatesAPI.uploadResume(file);
      setAnalysis(_mapResult(result));
      setUploadMsg(" Resume analyzed successfully!");
    } catch (err) { setUploadMsg(" " + err.message); }
    finally { setUploading(false); }
  };

  const handleSavedResumeAnalyze = async () => {
    setUploading(true); setUploadMsg("");
    try {
      const result = await candidatesAPI.reanalyzeResume(resumeTargetRole);
      setAnalysis(_mapResult(result));
      setUploadMsg(" Saved resume analyzed" + (resumeTargetRole ? ` for "${resumeTargetRole}"` : "") + "!");
    } catch (err) { setUploadMsg(" " + err.message); }
    finally { setUploading(false); }
  };

  const loadGaps = async (role) => {
    setGapsLoading(true);
    try {
      const g = await skillsAPI.gaps(role);
      setGaps(g);
      const c = await skillsAPI.courses();
      setCourses(c);
    } catch {}
    finally { setGapsLoading(false); }
  };

  const handleApply = async (jobId) => {
    setApplying(p => ({...p, [jobId]: true}));
    try {
      await jobsAPI.apply(jobId);
      setApplyMsg(p => ({...p, [jobId]: " Applied!"}));
    } catch (err) { setApplyMsg(p => ({...p, [jobId]: err.message})); }
    finally { setApplying(p => ({...p, [jobId]: false})); }
  };

  const handleLogout = () => { logout(); navigate("/"); };

  const toggleSave = async (jobId) => {
    if (savedJobs.includes(jobId)) {
      await jobsAPI.unsave(jobId).catch(() => {});
      setSavedJobs(prev => prev.filter(id => id !== jobId));
    } else {
      await jobsAPI.save(jobId).catch(() => {});
      setSavedJobs(prev => [...prev, jobId]);
    }
  };

  if (loading) return <div className="dash-loader">Loading your dashboard...</div>;

  return (
    <div className="cdash">
      {/* Profile Setup Modal */}
      {showSetup && <ProfileSetup profile={profile} onComplete={handleProfileDone} />}

      {/* Header */}
      <header className="cdash-header">
        <div>
          <h1 className="cdash-title">Career Readiness Dashboard</h1>
          <p className="cdash-sub">Welcome back! Track your progress and find your next opportunity.</p>
        </div>
        <div className="cdash-header-actions">
          <button className="edit-profile-btn" onClick={() => setShowSetup(true)}> Edit Profile</button>
          <button className="logout-btn" onClick={handleLogout}> Logout</button>
        </div>
      </header>

      {/* Tabs */}
      <div className="cdash-tabs">
        {TABS.map(t => (
          <button key={t} className={`cdash-tab ${tab === t ? "active" : ""}`} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </div>

      {/* ═══ OVERVIEW ═══ */}
      {tab === "Overview" && (() => {
        const skillCount = profile?.skills?.length || 0;
        const hasResume = !!analysis;
        const appliedCount = matches.length;
        const courseCount = courses.reduce((acc, c) => acc + (c.courses?.length || 1), 0);
        const readiness = gaps?.readiness_percent || 0;
        const profileScore = Math.min(100, (profile?.skills?.length ? 30 : 0) + (profile?.career_goal ? 25 : 0) + (hasResume ? 25 : 0) + (profile?.education ? 20 : 0));
        const resumeScore = analysis?.ats_score || 0;
        const jobScore = Math.min(100, appliedCount * 15);
        const learningScore = Math.min(100, courseCount * 12);
        // Simple streak based on profile data presence
        const streakDays = (hasResume ? 2 : 0) + (skillCount > 0 ? 1 : 0) + (appliedCount > 0 ? 2 : 0) + (courseCount > 0 ? 2 : 0);
        return (
        <div>
          {/* Welcome Banner */}
          <div className="ov-welcome-card cdash-card">
            <div className="ov-welcome-left">
              <h2 style={{margin: "0 0 4px"}}> Welcome back{profile?.full_name ? `, ${profile.full_name.split(" ")[0]}` : ""}!</h2>
              <p style={{margin: "0 0 12px", color: "#888", fontSize: 14}}>
                {profile?.career_goal ? `Working toward: ${profile.career_goal}` : "Set your career goal to get personalized guidance"}
              </p>
              <div className="ov-profile-bar-wrap">
                <div className="ov-profile-bar-label">
                  <span>Profile Completion</span>
                  <span style={{fontWeight: 700, color: "#6366f1"}}>{profileScore}%</span>
                </div>
                <div className="sb-bar-track"><div className="sb-bar-fill" style={{width: `${profileScore}%`, background: "linear-gradient(90deg, #6366f1, #818cf8)"}}></div></div>
              </div>
            </div>
            <div className="ov-welcome-stats">
              <div className="ov-wstat"><span className="ov-wstat-val">{skillCount}</span><span className="ov-wstat-lab">Skills</span></div>
              <div className="ov-wstat"><span className="ov-wstat-val">{appliedCount}</span><span className="ov-wstat-lab">Job Matches</span></div>
              <div className="ov-wstat"><span className="ov-wstat-val">{courseCount}</span><span className="ov-wstat-lab">Courses</span></div>
              <div className="ov-wstat"><span className="ov-wstat-val">{feedback.length}</span><span className="ov-wstat-lab">Feedback</span></div>
            </div>
          </div>

          <div className="cdash-grid-2" style={{marginTop: 20}}>
            {/* Career Readiness Chart */}
            <div className="cdash-card">
              <h3> Career Readiness</h3>
              <div className="ov-chart">
                {[
                  {label: "Skills", value: readiness, color: "#6366f1"},
                  {label: "Resume", value: resumeScore, color: "#10b981"},
                  {label: "Jobs", value: jobScore, color: "#f59e0b"},
                  {label: "Learning", value: learningScore, color: "#ec4899"},
                ].map((bar, i) => (
                  <div key={i} className="ov-bar-item">
                    <span className="ov-bar-label">{bar.label}</span>
                    <div className="ov-bar-track">
                      <div className="ov-bar-fill" style={{width: `${bar.value}%`, background: bar.color}}></div>
                    </div>
                    <span className="ov-bar-val">{bar.value}%</span>
                  </div>
                ))}
              </div>
              <div style={{marginTop: 16, display: "flex", justifyContent: "space-between", alignItems: "center"}}>
                <span style={{fontSize: 14, color: "#888"}}>Overall readiness</span>
                <span style={{fontSize: 22, fontWeight: 700, color: "#6366f1"}}>{Math.round((readiness + resumeScore + jobScore + learningScore) / 4)}%</span>
              </div>
            </div>

            {/* Learning Streak */}
            <div className="cdash-card">
              <h3> Activity Streak</h3>
              <div className="ov-streak-wrap">
                <div className="ov-streak-number">{streakDays}</div>
                <div className="ov-streak-meta">
                  <span style={{fontWeight: 600, fontSize: 16}}>Day Streak</span>
                  <span style={{color: "#888", fontSize: 13}}>Keep building your career!</span>
                </div>
              </div>
              <div className="ov-streak-grid">
                {[...Array(7)].map((_, i) => (
                  <div key={i} className={`ov-streak-dot ${i < streakDays ? "active" : ""}`}>{["M","T","W","T","F","S","S"][i]}</div>
                ))}
              </div>
              <div className="ov-quick-stats">
                <div className="ov-qs"><span className="ov-qs-icon"></span> Resume {hasResume ? "" : ""}</div>
                <div className="ov-qs"><span className="ov-qs-icon"></span> Skills: {skillCount}</div>
                <div className="ov-qs"><span className="ov-qs-icon"></span> Courses: {courseCount}</div>
              </div>
            </div>
          </div>

          <div className="cdash-grid-2" style={{marginTop: 20}}>
            {/* Top Job Matches */}
            <div className="cdash-card">
              <h3> Top Job Matches</h3>
              {matches.slice(0, 4).map((m, i) => (
                <div key={i} className="ov-job-item">
                  <div className="ov-job-info">
                    <strong>{m.job.title}</strong>
                    <span className="ov-job-skills">{(m.explanation?.matched_skills || []).slice(0, 3).join(", ")}</span>
                  </div>
                  <div className="ov-job-score-wrap">
                    <div className="ov-job-score-bar">
                      <div className="ov-job-score-fill" style={{width: `${m.score}%`, background: m.score >= 70 ? "#16a34a" : m.score >= 40 ? "#f59e0b" : "#ef4444"}}></div>
                    </div>
                    <span className="ov-job-score-text">{m.score}%</span>
                  </div>
                </div>
              ))}
              {matches.length === 0 && <p className="empty">No matches yet. Build your profile to see job matches!</p>}
              {matches.length > 4 && <button className="ov-see-more" onClick={() => setTab("Job Matches")}>See all {matches.length} matches →</button>}
            </div>

            {/* Top Course Recommendations */}
            <div className="cdash-card">
              <h3> Top Recommendations</h3>
              {courses.slice(0, 3).map((item, i) => {
                const c = item.courses ? item.courses[0] : item;
                return (
                  <div key={i} className="ov-course-item">
                    <div className="ov-course-icon"></div>
                    <div className="ov-course-info">
                      <strong>{c.name}</strong>
                      <span className="ov-course-meta">{c.provider} {item.skill ? `· ${item.skill}` : ""}</span>
                    </div>
                    <a href={c.url} target="_blank" rel="noreferrer" className="ov-course-link">Open →</a>
                  </div>
                );
              })}
              {courses.length === 0 && <p className="empty">Run a Skill Analysis to get course recommendations!</p>}
              {courses.length > 3 && <button className="ov-see-more" onClick={() => setTab("Courses")}>See all courses →</button>}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="cdash-card" style={{marginTop: 20}}>
            <h3> Quick Actions</h3>
            <div className="ov-actions-grid">
              <button className="ov-action-card" onClick={() => setTab("Skill Analysis")}>
                <span className="ov-action-icon"></span>
                <span className="ov-action-title">Analyze Skills</span>
                <span className="ov-action-desc">Find your skill gaps</span>
              </button>
              <button className="ov-action-card" onClick={() => setTab("Resume Checker")}>
                <span className="ov-action-icon"></span>
                <span className="ov-action-title">Check Resume</span>
                <span className="ov-action-desc">ATS compatibility scan</span>
              </button>
              <button className="ov-action-card" onClick={() => setTab("Career Path")}>
                <span className="ov-action-icon"></span>
                <span className="ov-action-title">Career Path</span>
                <span className="ov-action-desc">View your progress</span>
              </button>
              <button className="ov-action-card" onClick={() => setTab("Job Matches")}>
                <span className="ov-action-icon"></span>
                <span className="ov-action-title">Browse Jobs</span>
                <span className="ov-action-desc">Find opportunities</span>
              </button>
            </div>
          </div>

          {/* Skills at a Glance */}
          {profile?.skills?.length > 0 && (
            <div className="cdash-card" style={{marginTop: 20}}>
              <h3> Your Skills</h3>
              <div className="tag-list blue">
                {profile.skills.map((s, i) => <span key={i} className="stag">{s}</span>)}
              </div>
            </div>
          )}
        </div>
        );
      })()}

      {/* ═══ JOB MATCHES ═══ */}
      {tab === "Job Matches" && (
        <div className="cdash-cards-list">
          {allJobs.map(job => (
            <div key={job.id} className="cdash-card job-row">
              <div className="job-row-main">
                <div>
                  <h3 style={{margin: "0 0 6px"}}>{job.title}</h3>
                  <p className="job-desc">{job.description ? (job.description.length > 120 ? job.description.slice(0, 120) + "..." : job.description) : "No description"}</p>
                  <div className="job-tags">
                    {(job.required_skills || []).slice(0, 5).map((s, i) => <span key={i} className="jtag">{s}</span>)}
                    {(job.required_skills || []).length > 5 && <span className="jtag">+{job.required_skills.length - 5}</span>}
                  </div>
                  <div style={{display: "flex", gap: 10, flexWrap: "wrap", marginTop: 8, fontSize: 12}}>
                    {job.job_type && <span style={{color: "#6366f1", fontWeight: 600}}> {job.job_type}</span>}
                    {job.work_mode && <span style={{color: "#6366f1"}}> {job.work_mode}</span>}
                    {job.location && <span style={{color: "#888"}}> {job.location}</span>}
                    {job.salary_range && <span style={{color: "#16a34a", fontWeight: 600}}> {job.salary_range}</span>}
                  </div>
                </div>
                <div className="job-row-right">
                  <span className="exp-badge">{job.experience_min}+ yrs</span>
                </div>
              </div>
              <div className="job-actions">
                <button className="view-job-btn" onClick={() => setSelectedJob(job)}> View Job Posting</button>
                <button className={`save-job-btn ${savedJobs.includes(job.id) ? "saved" : ""}`} onClick={() => toggleSave(job.id)}>
                  {savedJobs.includes(job.id) ? " Saved" : " Save for Later"}
                </button>
              </div>
            </div>
          ))}
          {allJobs.length === 0 && <p className="empty">No open jobs right now</p>}
        </div>
      )}

      {/* ═══ JOB DETAIL MODAL ═══ */}
      {selectedJob && (
        <div className="job-modal-overlay" onClick={() => setSelectedJob(null)}>
          <div className="job-modal" onClick={e => e.stopPropagation()}>
            <button className="job-modal-close" onClick={() => setSelectedJob(null)}></button>
            <h2>{selectedJob.title}</h2>
            <div className="job-modal-meta">
              <span className="exp-badge">{selectedJob.experience_min}+ years experience</span>
              <span className="jtag">{selectedJob.vacancies} {selectedJob.vacancies === 1 ? "vacancy" : "vacancies"}</span>
              <span className="jtag">{selectedJob.status}</span>
              {selectedJob.job_type && <span className="jtag" style={{background: "#eef2ff", color: "#6366f1"}}> {selectedJob.job_type}</span>}
              {selectedJob.work_mode && <span className="jtag" style={{background: "#eef2ff", color: "#6366f1"}}> {selectedJob.work_mode}</span>}
              {selectedJob.location && <span className="jtag"> {selectedJob.location}</span>}
              {selectedJob.salary_range && <span className="jtag" style={{background: "#ecfdf5", color: "#16a34a"}}> {selectedJob.salary_range}</span>}
            </div>
            <div className="job-modal-section">
              <h4>Description</h4>
              <p>{selectedJob.description || "No description provided."}</p>
            </div>
            {selectedJob.requirements && (
              <div className="job-modal-section">
                <h4> Requirements</h4>
                <p style={{whiteSpace: "pre-line"}}>{selectedJob.requirements}</p>
              </div>
            )}
            <div className="job-modal-section">
              <h4>Required Skills</h4>
              <div className="job-tags">
                {(selectedJob.required_skills || []).map((s, i) => <span key={i} className="jtag">{s}</span>)}
              </div>
            </div>
            {selectedJob.external_link && (
              <div className="job-modal-section">
                <h4>More Info</h4>
                <a href={selectedJob.external_link} target="_blank" rel="noreferrer" className="job-external-link">
                   View Original Job Posting →
                </a>
              </div>
            )}
            <div className="job-modal-actions">
              {applyMsg[selectedJob.id]
                ? <span className="apply-status">{applyMsg[selectedJob.id]}</span>
                : <button className="apply-btn" onClick={() => handleApply(selectedJob.id)} disabled={!!applying[selectedJob.id]}>
                    {applying[selectedJob.id] ? "Applying..." : " Apply Now"}
                  </button>
              }
              <button className={`save-job-btn ${savedJobs.includes(selectedJob.id) ? "saved" : ""}`} onClick={() => toggleSave(selectedJob.id)}>
                {savedJobs.includes(selectedJob.id) ? " Saved" : " Save for Later"}
              </button>
              <button className="job-modal-close-btn" onClick={() => setSelectedJob(null)}>Close</button>
            </div>
          </div>
        </div>
      )}

      {/* ═══ SKILL ANALYSIS ═══ */}
      {tab === "Skill Analysis" && (
        <div>
          <div className="cdash-card" style={{marginBottom: 20}}>
            <div className="role-input-row">
              <input
                className="role-input"
                placeholder="Enter target role (e.g. frontend developer)"
                value={targetRole}
                onChange={e => setTargetRole(e.target.value)}
                onKeyDown={e => e.key === "Enter" && loadGaps(targetRole)}
              />
              <button className="analyze-btn" onClick={() => loadGaps(targetRole)} disabled={gapsLoading}>
                {gapsLoading ? " Analyzing..." : " Analyze"}
              </button>
            </div>
          </div>

          {gapsLoading && (
            <div className="cdash-card" style={{textAlign: "center", padding: 40}}>
              <div className="analysis-spinner"></div>
              <p style={{color: "#888", marginTop: 16}}>AI is analyzing your skills against the target role...</p>
            </div>
          )}

          {!gapsLoading && gaps && (
            <>
              {/* Row 1: Radar Chart + Skill Breakdown */}
              <div className="cdash-grid-2">
                {/* Radar Chart */}
                <div className="cdash-card">
                  <h3>Your Skills Portfolio</h3>
                  {(() => {
                    const radarSkills = gaps.radar_skills || [];
                    if (radarSkills.length === 0) return <p className="empty">No radar data</p>;
                    const n = radarSkills.length;
                    const cx = 150, cy = 140, r = 100;
                    const angleStep = (2 * Math.PI) / n;
                    const getPoint = (i, value) => {
                      const angle = angleStep * i - Math.PI / 2;
                      const dist = (value / 100) * r;
                      return [cx + dist * Math.cos(angle), cy + dist * Math.sin(angle)];
                    };
                    const yourPoints = radarSkills.map((s, i) => getPoint(i, s.your_level));
                    const reqPoints = radarSkills.map((s, i) => getPoint(i, s.required_level));
                    const yourPath = yourPoints.map((p, i) => (i === 0 ? "M" : "L") + p[0] + "," + p[1]).join(" ") + " Z";
                    const reqPath = reqPoints.map((p, i) => (i === 0 ? "M" : "L") + p[0] + "," + p[1]).join(" ") + " Z";
                    const labelPoints = radarSkills.map((s, i) => {
                      const angle = angleStep * i - Math.PI / 2;
                      return [cx + (r + 24) * Math.cos(angle), cy + (r + 24) * Math.sin(angle)];
                    });
                    return (
                      <div style={{display: "flex", flexDirection: "column", alignItems: "center"}}>
                        <svg width="300" height="300" viewBox="0 0 300 300">
                          {/* Grid rings */}
                          {[20, 40, 60, 80, 100].map(v => {
                            const pts = radarSkills.map((_, i) => getPoint(i, v));
                            return <polygon key={v} points={pts.map(p => p.join(",")).join(" ")} fill="none" stroke="#e5e7eb" strokeWidth="1" />;
                          })}
                          {/* Axis lines */}
                          {radarSkills.map((_, i) => {
                            const [x, y] = getPoint(i, 100);
                            return <line key={i} x1={cx} y1={cy} x2={x} y2={y} stroke="#e5e7eb" strokeWidth="1" />;
                          })}
                          {/* Required area */}
                          <path d={reqPath} fill="rgba(168,85,247,0.15)" stroke="#a855f7" strokeWidth="2" />
                          {/* Your skills area */}
                          <path d={yourPath} fill="rgba(99,102,241,0.25)" stroke="#6366f1" strokeWidth="2.5" />
                          {/* Dots */}
                          {yourPoints.map((p, i) => <circle key={i} cx={p[0]} cy={p[1]} r="4" fill="#6366f1" />)}
                          {/* Labels */}
                          {labelPoints.map((p, i) => (
                            <text key={i} x={p[0]} y={p[1]} textAnchor="middle" dominantBaseline="middle" fontSize="11" fill="#555" fontWeight="500">
                              {radarSkills[i].skill}
                            </text>
                          ))}
                        </svg>
                        <div className="skill-legend" style={{marginTop: 8}}>
                          <div><span className="dot blue"></span> Your Skills</div>
                          <div><span className="dot purple"></span> Required Skills</div>
                        </div>
                      </div>
                    );
                  })()}
                </div>

                {/* Skill Breakdown */}
                <div className="cdash-card">
                  <h3>Skill Breakdown</h3>
                  <div className="skill-breakdown-list">
                    {(gaps.skill_breakdown || []).slice(0, 10).map((s, i) => (
                      <div key={i} className="sb-item">
                        <div className="sb-header">
                          <span className="sb-name">{s.name}</span>
                          <span className={`sb-level sb-${s.level}`}>{s.level}</span>
                        </div>
                        <div className="sb-bar-row">
                          <div className="sb-bar-track">
                            <div className="sb-bar-fill" style={{width: `${s.score || 60}%`}}></div>
                          </div>
                          <span className="sb-years">{s.years}y</span>
                        </div>
                      </div>
                    ))}
                    {(gaps.skill_breakdown || []).length === 0 && <p className="empty">No skill data yet</p>}
                  </div>
                </div>
              </div>

              {/* Row 2: Stats */}
              <div className="cdash-stats-row" style={{marginTop: 20}}>
                <div className="cstat"><span className="cstat-val">{gaps.readiness_percent}%</span><span className="cstat-lab">Readiness for {gaps.target_role}</span></div>
                <div className="cstat"><span className="cstat-val">{gaps.strong_skills?.length || 0}</span><span className="cstat-lab">Strong Skills</span></div>
                <div className="cstat"><span className="cstat-val">{gaps.missing_skills?.length || 0}</span><span className="cstat-lab">Skill Gaps</span></div>
              </div>

              {/* Row 3: Job Comparisons */}
              <div className="cdash-card" style={{marginTop: 20}}>
                <h3>Skill Gaps by Target Role</h3>
                <div className="job-comp-list">
                  {(gaps.job_comparisons || []).map((jc, i) => (
                    <div key={i} className="job-comp-item">
                      <h4 className="jc-position">{jc.position}</h4>
                      <div className="jc-cols">
                        <div className="jc-col">
                          <span className="jc-label green"> Strength Areas</span>
                          <div className="jc-tags">
                            {(jc.strengths || []).map((s, j) => <span key={j} className="stag" style={{background: "#ecfdf5", color: "#16a34a", border: "1px solid #bbf7d0"}}>{s}</span>)}
                            {(jc.strengths || []).length === 0 && <span style={{color: "#aaa", fontSize: 13}}>—</span>}
                          </div>
                        </div>
                        <div className="jc-col">
                          <span className="jc-label red"> Missing Skills</span>
                          <div className="jc-tags">
                            {(jc.missing || []).map((s, j) => <span key={j} className="stag" style={{background: "#fef2f2", color: "#dc2626", border: "1px solid #fecaca"}}>{s}</span>)}
                            {(jc.missing || []).length === 0 && <span style={{color: "#aaa", fontSize: 13}}>—</span>}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                  {(gaps.job_comparisons || []).length === 0 && <p className="empty">No job comparisons available</p>}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* ═══ COURSES ═══ */}
      {tab === "Courses" && (
        <div>
          {gaps && (
            <div className="cdash-card" style={{marginBottom: 20}}>
              <p style={{margin: 0, fontSize: 14, color: "#555"}}>
                 Showing courses for skill gaps based on your target role: <strong style={{color: "#6366f1"}}>{gaps.target_role || "Software Engineer"}</strong>
                {gaps.career_goal && <span> — Career goal: <em>{gaps.career_goal}</em></span>}
              </p>
            </div>
          )}
          <div className="cdash-cards-grid">
            {courses.map((item, i) => {
              const list = item.courses || [item];
              return list.map((c, j) => (
                <div key={`${i}-${j}`} className="cdash-card course-card">
                  <div className="course-top">
                    <span className="course-skill">{item.skill || c.skill || "Skill"}</span>
                    <div className="course-badges">
                      {c.difficulty && <span className="course-diff">{c.difficulty}</span>}
                      {c.reason && c.reason.toLowerCase().includes("free") && <span className="course-free">FREE</span>}
                    </div>
                  </div>
                  <h3>{c.name}</h3>
                  <p className="course-provider">{c.provider}</p>
                  {c.reason && <p className="course-reason"> {c.reason}</p>}
                  <a href={c.url} target="_blank" rel="noreferrer" className="course-link">Open Course →</a>
                </div>
              ));
            })}
            {courses.length === 0 && <p className="empty">No course recommendations yet. Run a Skill Analysis with your target role first!</p>}
          </div>
        </div>
      )}

      {/* ═══ RESUME CHECKER ═══ */}
      {tab === "Resume Checker" && (
        <div>
          <div className="cdash-card" style={{marginBottom: 20}}>
            <h3 style={{margin: "0 0 4px"}}>Resume Checker & ATS Analyzer</h3>
            <p style={{margin: "0 0 20px", color: "#888", fontSize: 14}}>Upload your resume to get instant feedback on ATS compatibility, keyword optimization, and formatting.</p>

            {/* Drag & Drop Upload Zone */}
            <div
              className={`rc-dropzone ${dragOver ? "dragover" : ""}`}
              onDragOver={e => { e.preventDefault(); setDragOver(true); }}
              onDragLeave={() => setDragOver(false)}
              onDrop={e => { e.preventDefault(); setDragOver(false); const f = e.dataTransfer.files[0]; if (f && f.name.endsWith(".pdf")) setFile(f); }}
              onClick={() => document.getElementById("rc-file-input").click()}
            >
              <div className="rc-drop-icon"></div>
              <p className="rc-drop-title">{file ? ` ${file.name}` : "Drop your resume here"}</p>
              <p className="rc-drop-or">or</p>
              <button type="button" className="rc-browse-btn" onClick={e => { e.stopPropagation(); document.getElementById("rc-file-input").click(); }}>Browse Files</button>
              <p className="rc-drop-hint">Supports PDF (Max 10MB)</p>
              <input id="rc-file-input" type="file" accept=".pdf" onChange={e => { if (e.target.files[0]) setFile(e.target.files[0]); }} hidden />
            </div>

            {/* Save to DB toggle */}
            <div className="rc-save-toggle">
              <label className="rc-toggle-label">
                <input type="checkbox" checked={saveResume} onChange={e => setSaveResume(e.target.checked)} />
                <span className="rc-toggle-slider"></span>
                Save resume to database for future job applications
              </label>
            </div>

            {/* Target Role + Actions */}
            <div className="rc-actions-row">
              <input
                className="role-input"
                placeholder="Target role for analysis (optional, e.g. Frontend Developer)"
                value={resumeTargetRole}
                onChange={e => setResumeTargetRole(e.target.value)}
                style={{flex: 1}}
              />
              <button className="analyze-btn" onClick={handleUpload} disabled={!file || uploading}>
                {uploading ? " Analyzing..." : " Analyze New Resume"}
              </button>
              <button className="rc-saved-btn" onClick={handleSavedResumeAnalyze} disabled={uploading}>
                {uploading ? "..." : " Use Saved Resume"}
              </button>
            </div>
            {uploadMsg && <p style={{marginTop: 12, fontSize: 14, color: uploadMsg.startsWith("") ? "#16a34a" : "#dc2626"}}>{uploadMsg}</p>}
          </div>

          {uploading && (
            <div className="cdash-card" style={{textAlign: "center", padding: 40}}>
              <div className="analysis-spinner"></div>
              <p style={{color: "#888", marginTop: 16}}>AI is analyzing your resume...</p>
            </div>
          )}

          {!uploading && analysis && (
            <>
              {/* Stats Row */}
              <div className="cdash-stats-row">
                <div className="cstat"><span className="cstat-val">{analysis.ats_score ?? "—"}</span><span className="cstat-lab">ATS Score</span></div>
                <div className="cstat"><span className="cstat-val">{analysis.ai_detection_score ?? "—"}</span><span className="cstat-lab">AI Detection %</span></div>
                <div className="cstat"><span className="cstat-val">{analysis.parsed_skills?.length || 0}</span><span className="cstat-lab">Skills Found</span></div>
                {analysis.role_fit?.fit_score != null && (
                  <div className="cstat"><span className="cstat-val">{analysis.role_fit.fit_score}</span><span className="cstat-lab">Role Fit</span></div>
                )}
              </div>

              {/* Section Scores */}
              {analysis.section_scores && Object.keys(analysis.section_scores).length > 0 && (
                <div className="cdash-card" style={{marginTop: 16}}>
                  <h3> Section Scores</h3>
                  <div className="rc-section-scores">
                    {Object.entries(analysis.section_scores).map(([key, val]) => (
                      <div key={key} className="rc-sec-item">
                        <div className="rc-sec-header">
                          <span className="rc-sec-name">{key.replace(/_/g, " ")}</span>
                          <span className="rc-sec-val">{val}/100</span>
                        </div>
                        <div className="sb-bar-track"><div className="sb-bar-fill" style={{width: `${val}%`, background: val >= 70 ? "linear-gradient(90deg, #16a34a, #4ade80)" : val >= 40 ? "linear-gradient(90deg, #f59e0b, #fbbf24)" : "linear-gradient(90deg, #dc2626, #f87171)"}}></div></div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div className="cdash-grid-2" style={{marginTop: 16}}>
                {/* Keywords */}
                <div className="cdash-card">
                  <h3> Keyword Analysis</h3>
                  {analysis.keyword_analysis?.strong_keywords?.length > 0 && (
                    <div style={{marginBottom: 12}}>
                      <span className="jc-label green"> Strong Keywords</span>
                      <div className="jc-tags">{analysis.keyword_analysis.strong_keywords.map((k, i) => <span key={i} className="stag" style={{background: "#ecfdf5", color: "#16a34a", border: "1px solid #bbf7d0"}}>{k}</span>)}</div>
                    </div>
                  )}
                  {analysis.keyword_analysis?.missing_keywords?.length > 0 && (
                    <div>
                      <span className="jc-label red"> Missing Keywords</span>
                      <div className="jc-tags">{analysis.keyword_analysis.missing_keywords.map((k, i) => <span key={i} className="stag" style={{background: "#fef2f2", color: "#dc2626", border: "1px solid #fecaca"}}>{k}</span>)}</div>
                    </div>
                  )}
                  {(!analysis.keyword_analysis || (!analysis.keyword_analysis.strong_keywords?.length && !analysis.keyword_analysis.missing_keywords?.length)) && (
                    <div>
                      <h4 style={{fontSize: 14, color: "#888", margin: "0 0 8px"}}> Extracted Skills</h4>
                      <div className="tag-list blue">{(analysis.parsed_skills || []).map((s, i) => <span key={i} className="stag">{s}</span>)}</div>
                    </div>
                  )}
                </div>

                {/* Suggestions */}
                <div className="cdash-card">
                  <h3> Improvement Suggestions</h3>
                  <ul className="sugg-list">
                    {(analysis.suggestions || []).map((s, i) => <li key={i}>{typeof s === "string" ? s : JSON.stringify(s)}</li>)}
                  </ul>
                </div>
              </div>

              {/* Role Fit */}
              {analysis.role_fit && analysis.role_fit.target_role && (
                <div className="cdash-card" style={{marginTop: 16, borderLeft: "4px solid #6366f1"}}>
                  <h3> Role Fit: {analysis.role_fit.target_role}</h3>
                  <div className="cdash-grid-2" style={{marginTop: 12}}>
                    <div>
                      <span className="jc-label green"> Matching Keywords</span>
                      <div className="jc-tags">{(analysis.role_fit.matching_keywords || []).map((k, i) => <span key={i} className="stag" style={{background: "#ecfdf5", color: "#16a34a", border: "1px solid #bbf7d0"}}>{k}</span>)}</div>
                    </div>
                    <div>
                      <span className="jc-label red"> Missing for Role</span>
                      <div className="jc-tags">{(analysis.role_fit.missing_keywords || []).map((k, i) => <span key={i} className="stag" style={{background: "#fef2f2", color: "#dc2626", border: "1px solid #fecaca"}}>{k}</span>)}</div>
                    </div>
                  </div>
                  {analysis.role_fit.role_suggestions?.length > 0 && (
                    <ul className="sugg-list" style={{marginTop: 12}}>
                      {analysis.role_fit.role_suggestions.map((s, i) => <li key={i}>{s}</li>)}
                    </ul>
                  )}
                </div>
              )}

              {/* Overall Assessment */}
              {analysis.overall_assessment && (
                <div className="cdash-card" style={{marginTop: 16}}>
                  <h3> Overall Assessment</h3>
                  <p style={{fontSize: 14, color: "#555", lineHeight: 1.7, margin: 0}}>{analysis.overall_assessment}</p>
                </div>
              )}

              {/* Formatting Issues */}
              {analysis.formatting_issues && analysis.formatting_issues.length > 0 && (
                <div className="cdash-card" style={{marginTop: 16, borderLeft: "4px solid #f59e0b"}}>
                  <h3> Formatting Issues</h3>
                  <ul className="sugg-list">
                    {analysis.formatting_issues.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
            </>
          )}
        </div>
      )}

      {/* ═══ CAREER PATH ═══ */}
      {tab === "Career Path" && (
        <div>
          {!careerPath && !cpLoading && (
            <div className="cdash-card" style={{textAlign: "center", padding: 40}}>
              <h3 style={{margin: "0 0 12px"}}> Your Career Path</h3>
              <p style={{color: "#888", marginBottom: 16}}>Generate your personalized career progress path based on your profile, resume, skills, and job applications.</p>
              <button className="analyze-btn" onClick={async () => {
                setCpLoading(true);
                try { const r = await skillsAPI.careerPath(); setCareerPath(r); } catch {}
                finally { setCpLoading(false); }
              }}> Generate Career Path</button>
            </div>
          )}

          {cpLoading && (
            <div className="cdash-card" style={{textAlign: "center", padding: 40}}>
              <div className="analysis-spinner"></div>
              <p style={{color: "#888", marginTop: 16}}>AI is analyzing your career trajectory...</p>
            </div>
          )}

          {!cpLoading && careerPath && (
            <>
              {/* Overall Progress */}
              <div className="cdash-card cp-overview">
                <div className="cp-progress-ring-wrap">
                  <svg className="cp-ring" viewBox="0 0 120 120">
                    <circle cx="60" cy="60" r="50" fill="none" stroke="#e5e7eb" strokeWidth="10" />
                    <circle cx="60" cy="60" r="50" fill="none" stroke="#6366f1" strokeWidth="10"
                      strokeDasharray={`${(careerPath.overall_progress / 100) * 314} 314`}
                      strokeLinecap="round" transform="rotate(-90 60 60)" />
                  </svg>
                  <div className="cp-ring-text">
                    <span className="cp-ring-pct">{careerPath.overall_progress}%</span>
                    <span className="cp-ring-label">Progress</span>
                  </div>
                </div>
                <div className="cp-overview-info">
                  <h2 style={{margin: "0 0 4px", color: "#1a1a2e"}}> {careerPath.career_goal}</h2>
                  <p style={{margin: "0 0 8px", color: "#6366f1", fontWeight: 600, fontSize: 14}}>Stage: {careerPath.current_stage}</p>
                  <p style={{margin: 0, color: "#888", fontSize: 14}}> Estimated: {careerPath.estimated_timeline}</p>
                </div>
              </div>

              {/* Milestones Timeline */}
              <div className="cdash-card" style={{marginTop: 20}}>
                <h3> Career Milestones</h3>
                <div className="cp-timeline">
                  {(careerPath.milestones || []).map((m, i) => (
                    <div key={i} className={`cp-milestone ${m.status}`}>
                      <div className="cp-ms-dot">{m.icon || ""}</div>
                      <div className="cp-ms-content">
                        <div className="cp-ms-header">
                          <strong>{m.title}</strong>
                          <span className={`cp-ms-badge ${m.status}`}>
                            {m.status === "completed" ? " Done" : m.status === "in_progress" ? " In Progress" : " Not Started"}
                          </span>
                        </div>
                        <p className="cp-ms-desc">{m.description}</p>
                        <div className="sb-bar-track" style={{marginTop: 6}}>
                          <div className="sb-bar-fill" style={{
                            width: `${m.progress}%`,
                            background: m.status === "completed" ? "linear-gradient(90deg, #16a34a, #4ade80)" :
                              m.status === "in_progress" ? "linear-gradient(90deg, #6366f1, #818cf8)" : "#e5e7eb"
                          }}></div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="cdash-grid-2" style={{marginTop: 20}}>
                {/* Next Steps */}
                <div className="cdash-card">
                  <h3> Next Steps</h3>
                  <ul className="sugg-list">
                    {(careerPath.next_steps || []).map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>

                {/* Strengths & Improve */}
                <div className="cdash-card">
                  <h3> Assessment</h3>
                  <div style={{marginBottom: 12}}>
                    <span className="jc-label green"> Strengths</span>
                    <div className="jc-tags">
                      {(careerPath.strengths || []).map((s, i) => <span key={i} className="stag" style={{background: "#ecfdf5", color: "#16a34a", border: "1px solid #bbf7d0"}}>{s}</span>)}
                    </div>
                  </div>
                  <div>
                    <span className="jc-label red"> Areas to Improve</span>
                    <div className="jc-tags">
                      {(careerPath.areas_to_improve || []).map((s, i) => <span key={i} className="stag" style={{background: "#fef2f2", color: "#dc2626", border: "1px solid #fecaca"}}>{s}</span>)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Career Insights */}
              {careerPath.career_insights && (
                <div className="cdash-card" style={{marginTop: 20, borderLeft: "4px solid #6366f1"}}>
                  <h3> Career Insights</h3>
                  <p style={{fontSize: 14, color: "#555", lineHeight: 1.7, margin: 0}}>{careerPath.career_insights}</p>
                </div>
              )}

              <div style={{textAlign: "center", marginTop: 20}}>
                <button className="analyze-btn" onClick={async () => {
                  setCpLoading(true);
                  try { const r = await skillsAPI.careerPath(); setCareerPath(r); } catch {}
                  finally { setCpLoading(false); }
                }}> Refresh Career Path</button>
              </div>
            </>
          )}
        </div>
      )}

      {/* ═══ FEEDBACK ═══ */}
      {tab === "Feedback" && (
        <div className="cdash-cards-list">
          {feedback.map(f => (
            <div key={f.id} className={`cdash-card feedback-card ${f.type}`}>
              <div className="fb-head">
                <span className={`fb-badge ${f.type}`}>{f.type}</span>
                <span className="fb-date">{new Date(f.created_at).toLocaleDateString()}</span>
              </div>
              <p className="fb-msg">{f.message}</p>
            </div>
          ))}
          {feedback.length === 0 && <p className="empty">No feedback received yet.</p>}
        </div>
      )}
    </div>
  );
}
