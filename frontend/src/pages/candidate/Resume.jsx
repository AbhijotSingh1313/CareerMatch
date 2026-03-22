import { useState, useEffect } from "react";
import { candidatesAPI } from "../../services/api";
import "../Dashboard.css";
import "./Resume.css";

export default function Resume() {
  const [analysis, setAnalysis] = useState(null);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    candidatesAPI.getResumeAnalysis()
      .then(setAnalysis)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) return;
    setUploading(true); setError(""); setSuccess("");
    try {
      const result = await candidatesAPI.uploadResume(file);
      setSuccess("Resume analyzed successfully!");
      // Reload analysis
      const fresh = await candidatesAPI.getResumeAnalysis();
      setAnalysis(fresh);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="dashboard">
      <div className="dash-header">
        <h1> <span className="gradient-text">Resume Analysis</span></h1>
        <p>Upload your resume for AI-powered feedback and ATS scoring</p>
      </div>

      {/* Upload Section */}
      <div className="card resume-upload-card">
        <h2>Upload Resume (PDF)</h2>
        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}
        <form onSubmit={handleUpload} className="upload-form">
          <label className="file-drop" htmlFor="resume-file">
            <span className="file-icon"></span>
            <span>{file ? file.name : "Click to choose a PDF"}</span>
            <input
              id="resume-file"
              type="file"
              accept=".pdf"
              onChange={(e) => setFile(e.target.files[0])}
              hidden
            />
          </label>
          <button type="submit" className="btn-primary" disabled={!file || uploading}>
            {uploading ? "Analyzing with AI..." : "Analyze Resume"}
          </button>
        </form>
      </div>

      {/* Results */}
      {loading && <div className="dash-loading">Loading analysis...</div>}

      {!loading && analysis && (
        <>
          {/* ATS Score */}
          <div className="dash-stats" style={{ marginTop: "28px" }}>
            <div className="stat-card">
              <div className="stat-icon"></div>
              <div className="stat-info">
                <span className="stat-value">{analysis.ats_score ?? "—"}</span>
                <span className="stat-label">ATS Score</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon"></div>
              <div className="stat-info">
                <span className="stat-value">{analysis.ai_detection_score ?? "—"}</span>
                <span className="stat-label">AI Detection %</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon"></div>
              <div className="stat-info">
                <span className="stat-value">{analysis.parsed_skills?.length ?? 0}</span>
                <span className="stat-label">Skills Found</span>
              </div>
            </div>
          </div>

          {/* Education & Experience */}
          <div className="dash-section" style={{ marginTop: "28px" }}>
            <h2> Education</h2>
            <div className="card"><p style={{ color: "rgba(255,255,255,0.7)" }}>{analysis.parsed_education || "Not detected"}</p></div>
          </div>

          {/* Skills */}
          <div className="dash-section">
            <h2> Extracted Skills</h2>
            <div className="skill-tags" style={{ flexWrap: "wrap" }}>
              {(analysis.parsed_skills || []).map((s, i) => (
                <span key={i} className="skill-tag" style={{ background: "rgba(108,99,255,0.12)", border: "1px solid rgba(108,99,255,0.3)", color: "#a89dff" }}>{s}</span>
              ))}
            </div>
          </div>

          {/* AI Suggestions */}
          {analysis.suggestions?.length > 0 && (
            <div className="dash-section">
              <h2> AI Suggestions</h2>
              <div className="card">
                <ul className="suggestions-list">
                  {Array.isArray(analysis.suggestions)
                    ? analysis.suggestions.map((s, i) => <li key={i}>{typeof s === "string" ? s : JSON.stringify(s)}</li>)
                    : null}
                </ul>
              </div>
            </div>
          )}
        </>
      )}

      {!loading && !analysis && (
        <p className="empty-state" style={{ marginTop: 40 }}>No resume uploaded yet. Upload a PDF to get started!</p>
      )}
    </div>
  );
}
