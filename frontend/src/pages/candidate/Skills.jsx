import { useState, useEffect } from "react";
import { skillsAPI } from "../../services/api";
import "../Dashboard.css";

export default function Skills() {
  const [gaps, setGaps] = useState(null);
  const [courses, setCourses] = useState([]);
  const [targetRole, setTargetRole] = useState("");
  const [loading, setLoading] = useState(true);
  const [coursesLoading, setCoursesLoading] = useState(true);

  const loadGaps = async (role = "") => {
    setLoading(true);
    try {
      const g = await skillsAPI.gaps(role);
      setGaps(g);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGaps();
    skillsAPI.courses()
      .then(setCourses)
      .catch(() => {})
      .finally(() => setCoursesLoading(false));
  }, []);

  return (
    <div className="dashboard">
      <div className="dash-header">
        <h1> <span className="gradient-text">Skill Gap Analysis</span></h1>
        <p>See what skills you need and get AI-recommended courses</p>
      </div>

      {/* Role filter */}
      <div className="card" style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", gap: 12 }}>
          <input
            className="field input"
            style={{ flex: 1, padding: "12px 16px", borderRadius: 12, border: "1.5px solid rgba(255,255,255,0.1)", background: "rgba(255,255,255,0.05)", color: "#fff", fontSize: 14, outline: "none", fontFamily: "Inter, sans-serif" }}
            placeholder="Enter target role (e.g. frontend developer)"
            value={targetRole}
            onChange={(e) => setTargetRole(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && loadGaps(targetRole)}
          />
          <button className="btn-primary" onClick={() => loadGaps(targetRole)}>Analyze</button>
        </div>
      </div>

      {/* Gaps */}
      {loading ? (
        <div className="dash-loading">Analyzing skills...</div>
      ) : gaps ? (
        <>
          <div className="dash-stats">
            <div className="stat-card">
              <div className="stat-icon"></div>
              <div className="stat-info">
                <span className="stat-value">{gaps.readiness_percent}%</span>
                <span className="stat-label">Role Readiness</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon"></div>
              <div className="stat-info">
                <span className="stat-value">{gaps.strong_skills?.length || 0}</span>
                <span className="stat-label">Strong Skills</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon"></div>
              <div className="stat-info">
                <span className="stat-value">{gaps.missing_skills?.length || 0}</span>
                <span className="stat-label">Gaps</span>
              </div>
            </div>
          </div>

          <div className="dash-section" style={{ marginTop: 28 }}>
            <h2>Target Role: <span className="gradient-text">{gaps.target_role}</span></h2>
            <div className="skill-bars">
              <div className="skill-group">
                <h4> You have these</h4>
                <div className="skill-tags green">
                  {(gaps.strong_skills || []).map((s, i) => <span key={i} className="skill-tag">{s}</span>)}
                </div>
              </div>
              <div className="skill-group">
                <h4> Skills to learn</h4>
                <div className="skill-tags red">
                  {(gaps.missing_skills || []).map((s, i) => <span key={i} className="skill-tag">{s}</span>)}
                </div>
              </div>
            </div>
          </div>
        </>
      ) : null}

      {/* Courses */}
      <div className="dash-section" style={{ marginTop: 32 }}>
        <h2> AI-Recommended Courses</h2>
        {coursesLoading ? (
          <div className="dash-loading">Loading courses...</div>
        ) : (
          <div className="match-cards">
            {courses.map((item, i) => {
              const courseList = item.courses || [item];
              return courseList.map((c, j) => (
                <div key={`${i}-${j}`} className="match-card">
                  <div className="match-score-badge" style={{ background: "rgba(0,212,255,0.15)", color: "#00d4ff" }}>
                    {item.skill || c.skill || "Skill"}
                  </div>
                  <h3 style={{ paddingRight: 100 }}>{c.name}</h3>
                  <p className="match-skills">{c.provider}</p>
                  {c.difficulty && <p className="match-missing">Level: {c.difficulty}</p>}
                  {c.reason && <p className="match-insight"> {c.reason}</p>}
                  <a href={c.url} target="_blank" rel="noreferrer" className="btn-primary" style={{ display: "block", width: "100%", marginTop: 14, textAlign: "center", textDecoration: "none" }}>
                    View Course →
                  </a>
                </div>
              ));
            })}
            {courses.length === 0 && <p className="empty-state">No skill gaps detected — you're all set!</p>}
          </div>
        )}
      </div>
    </div>
  );
}
