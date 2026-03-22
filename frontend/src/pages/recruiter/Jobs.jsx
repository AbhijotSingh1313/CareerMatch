import { useState, useEffect } from "react";
import { jobsAPI } from "../../services/api";
import "../Dashboard.css";

const emptyJob = { title: "", description: "", required_skills: "", experience_min: 0, vacancies: 1, ats_required: false, external_link: "", job_type: "full-time", work_mode: "onsite", location: "", salary_range: "", requirements: "" };

export default function RecruiterJobs() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(emptyJob);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [editingId, setEditingId] = useState(null);

  const load = () => jobsAPI.myJobs().then(setJobs).catch(() => {}).finally(() => setLoading(false));
  useEffect(() => { load(); }, []);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setForm((p) => ({ ...p, [name]: type === "checkbox" ? checked : value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); setError(""); setSubmitting(true);
    try {
      const skills = form.required_skills.split(",").map((s) => s.trim()).filter(Boolean);
      const payload = { ...form, required_skills: skills, experience_min: Number(form.experience_min), vacancies: Number(form.vacancies) };
      if (!payload.external_link) delete payload.external_link;
      if (!payload.location) delete payload.location;
      if (!payload.salary_range) delete payload.salary_range;
      if (!payload.requirements) delete payload.requirements;

      if (editingId) {
        await jobsAPI.update(editingId, payload);
      } else {
        await jobsAPI.create(payload);
      }
      setForm(emptyJob); setShowForm(false); setEditingId(null); load();
    } catch (err) { setError(err.message); }
    finally { setSubmitting(false); }
  };

  const startEdit = (job) => {
    setForm({
      title: job.title || "",
      description: job.description || "",
      required_skills: (job.required_skills || []).join(", "),
      experience_min: job.experience_min || 0,
      vacancies: job.vacancies || 1,
      ats_required: job.ats_required || false,
      external_link: job.external_link || "",
      job_type: job.job_type || "full-time",
      work_mode: job.work_mode || "onsite",
      location: job.location || "",
      salary_range: job.salary_range || "",
      requirements: job.requirements || "",
    });
    setEditingId(job.id);
    setShowForm(true);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const cancelForm = () => { setShowForm(false); setEditingId(null); setForm(emptyJob); };

  const handleStatus = async (id, status) => {
    try { await jobsAPI.updateStatus(id, status); load(); } catch {}
  };

  const handleDelete = async (id) => {
    if (!confirm("Are you sure?")) return;
    try { await jobsAPI.remove(id); load(); } catch {}
  };

  if (loading) return <div className="dash-loading">Loading jobs...</div>;

  return (
    <div className="dashboard">
      <div className="dash-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h1> <span className="gradient-text">My Job Postings</span></h1>
          <p>{jobs.length} job{jobs.length !== 1 ? "s" : ""} posted</p>
        </div>
        <button className="btn-primary" onClick={() => showForm ? cancelForm() : setShowForm(true)}>
          {showForm ? " Cancel" : "+ New Job"}
        </button>
      </div>

      {/* Create / Edit Job Form */}
      {showForm && (
        <div className="card" style={{ marginBottom: 28 }}>
          <h2 style={{ color: "#fff", marginBottom: 20 }}>{editingId ? " Edit Job" : "Create New Job"}</h2>
          {error && <div className="alert alert-error">{error}</div>}
          <form onSubmit={handleSubmit}>
            <div className="field"><label>Job Title *</label><input name="title" value={form.title} onChange={handleChange} placeholder="e.g. React Developer" required /></div>
            <div className="field"><label>Description</label><textarea name="description" value={form.description} onChange={handleChange} placeholder="Job responsibilities..." rows={4} /></div>
            <div className="field"><label>Requirements</label><textarea name="requirements" value={form.requirements} onChange={handleChange} placeholder="• Bachelor's degree in CS&#10;• 2+ years experience&#10;• Strong communication skills" rows={3} /></div>
            <div className="field"><label>Required Skills (comma-separated)</label><input name="required_skills" value={form.required_skills} onChange={handleChange} placeholder="React, Node.js, SQL..." /></div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
              <div className="field">
                <label>Job Type</label>
                <select name="job_type" value={form.job_type} onChange={handleChange}>
                  <option value="full-time">Full-time</option>
                  <option value="part-time">Part-time</option>
                  <option value="contract">Contract</option>
                  <option value="internship">Internship</option>
                  <option value="freelance">Freelance</option>
                </select>
              </div>
              <div className="field">
                <label>Work Mode</label>
                <select name="work_mode" value={form.work_mode} onChange={handleChange}>
                  <option value="onsite">Onsite</option>
                  <option value="remote">Remote</option>
                  <option value="hybrid">Hybrid</option>
                </select>
              </div>
              <div className="field"><label>Location</label><input name="location" value={form.location} onChange={handleChange} placeholder="e.g. San Francisco, CA" /></div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 16 }}>
              <div className="field"><label>Min. Experience (years)</label><input name="experience_min" type="number" min="0" value={form.experience_min} onChange={handleChange} /></div>
              <div className="field"><label>Vacancies</label><input name="vacancies" type="number" min="1" value={form.vacancies} onChange={handleChange} /></div>
              <div className="field"><label>Salary Range</label><input name="salary_range" value={form.salary_range} onChange={handleChange} placeholder="e.g. $80k - $120k" /></div>
            </div>
            <div className="field"><label>External Link (optional)</label><input name="external_link" value={form.external_link} onChange={handleChange} placeholder="https://careers.company.com/job/123" /></div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
              <input type="checkbox" id="ats" name="ats_required" checked={form.ats_required} onChange={handleChange} />
              <label htmlFor="ats" style={{ color: "rgba(255,255,255,0.65)", fontSize: 14 }}>Require ATS score</label>
            </div>
            <div style={{ display: "flex", gap: 10 }}>
              <button type="submit" className="btn-primary" disabled={submitting}>
                {submitting ? (editingId ? "Saving..." : "Creating...") : (editingId ? " Save Changes" : "Create Job Posting")}
              </button>
              {editingId && <button type="button" className="btn-secondary" onClick={cancelForm}>Cancel</button>}
            </div>
          </form>
        </div>
      )}

      {/* Job List */}
      <div className="match-cards">
        {jobs.map((job) => (
          <div key={job.id} className="match-card">
            <span className={`match-score-badge ${job.status !== "open" ? "closed" : ""}`}>{job.status}</span>
            <h3>{job.title}</h3>
            <p className="match-skills">{job.description || "No description"}</p>
            {job.requirements && <p style={{ color: "rgba(255,255,255,0.5)", fontSize: 12, marginTop: 4 }}> {job.requirements.substring(0, 100)}{job.requirements.length > 100 ? "..." : ""}</p>}
            <div className="job-meta" style={{ display: "flex", gap: 12, marginTop: 8, flexWrap: "wrap" }}>
              <span style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}> {job.experience_min}y+ exp</span>
              <span style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}> {job.vacancies} opening(s)</span>
              {job.job_type && <span style={{ color: "#818cf8", fontSize: 12 }}> {job.job_type}</span>}
              {job.work_mode && <span style={{ color: "#818cf8", fontSize: 12 }}> {job.work_mode}</span>}
              {job.location && <span style={{ color: "rgba(255,255,255,0.4)", fontSize: 12 }}> {job.location}</span>}
              {job.salary_range && <span style={{ color: "#4ade80", fontSize: 12 }}> {job.salary_range}</span>}
              {job.external_link && <a href={job.external_link} target="_blank" rel="noreferrer" style={{ color: "#818cf8", fontSize: 12, textDecoration: "none" }}> External Link</a>}
            </div>
            <div style={{ display: "flex", gap: 8, marginTop: 16, flexWrap: "wrap" }}>
              <button className="btn-secondary" style={{ fontSize: 12, padding: "6px 14px" }} onClick={() => startEdit(job)}> Edit</button>
              {job.status === "open" && <button className="btn-secondary" style={{ fontSize: 12, padding: "6px 14px" }} onClick={() => handleStatus(job.id, "closed")}>Close</button>}
              {job.status === "closed" && <button className="btn-secondary" style={{ fontSize: 12, padding: "6px 14px" }} onClick={() => handleStatus(job.id, "open")}>Reopen</button>}
              <button className="btn-danger" style={{ fontSize: 12, padding: "6px 14px" }} onClick={() => handleDelete(job.id)}>Delete</button>
            </div>
          </div>
        ))}
        {jobs.length === 0 && <p className="empty-state">No jobs yet. Create your first job posting!</p>}
      </div>
    </div>
  );
}
