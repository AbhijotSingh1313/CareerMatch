import { useState, useEffect } from "react";
import { candidatesAPI } from "../../services/api";
import "./ProfileSetup.css";

export default function ProfileSetup({ profile, onComplete }) {
  const [form, setForm] = useState({
    full_name: "",
    current_position: "",
    experience_years: "",
    education: "",
    skills: "",
    career_goal: "",
    preferred_companies: "",
  });
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [step, setStep] = useState(1);
  const [validationMsg, setValidationMsg] = useState("");

  // Prefill from existing profile when editing
  useEffect(() => {
    if (profile) {
      setForm({
        full_name: profile.full_name || "",
        current_position: profile.current_position || "",
        experience_years: profile.experience_years ?? "",
        education: profile.education || "",
        skills: (profile.skills || []).join(", "),
        career_goal: profile.career_goal || "",
        preferred_companies: (profile.preferred_companies || []).join(", "),
      });
    }
  }, [profile]);

  const handleChange = (e) => {
    setForm(p => ({ ...p, [e.target.name]: e.target.value }));
  };

  const handleSave = async () => {
    setSaving(true); setError("");
    try {
      const payload = {
        full_name: form.full_name,
        current_position: form.current_position || null,
        experience_years: form.experience_years ? Number(form.experience_years) : null,
        education: form.education || null,
        skills: form.skills ? form.skills.split(",").map(s => s.trim()).filter(Boolean) : null,
        career_goal: form.career_goal || null,
        preferred_companies: form.preferred_companies ? form.preferred_companies.split(",").map(s => s.trim()).filter(Boolean) : null,
      };
      await candidatesAPI.updateProfile(payload);

      // Upload resume if file selected
      if (file) {
        setUploading(true);
        await candidatesAPI.uploadResume(file);
        setUploading(false);
      }

      onComplete();
    } catch (err) { setError(err.message); }
    finally { setSaving(false); }
  };

  return (
    <div className="profile-setup-overlay">
      <div className="profile-setup-modal">
        <div className="ps-header">
          <h1>{profile?.profile_complete ? " Edit Profile" : " Set Up Your Profile"}</h1>
          <p>{profile?.profile_complete ? "Update your details below" : "Tell us about yourself to get personalized matches"}</p>
        </div>

        {/* Step Indicator */}
        <div className="ps-steps">
          <div className={`ps-step ${step >= 1 ? "active" : ""}`}><span>1</span> Basic Info</div>
          <div className="ps-step-line"></div>
          <div className={`ps-step ${step >= 2 ? "active" : ""}`}><span>2</span> Skills & Goals</div>
          <div className="ps-step-line"></div>
          <div className={`ps-step ${step >= 3 ? "active" : ""}`}><span>3</span> Resume</div>
        </div>

        {error && <div className="ps-error">{error}</div>}

        {/* Step 1: Basic Info */}
        {step === 1 && (
          <div className="ps-form">
            <div className="ps-field">
              <label>Full Name *</label>
              <input name="full_name" value={form.full_name} onChange={handleChange} placeholder="John Doe" required />
            </div>
            <div className="ps-field">
              <label>Current Position</label>
              <input name="current_position" value={form.current_position} onChange={handleChange} placeholder="e.g. Junior Frontend Developer" />
            </div>
            <div className="ps-row">
              <div className="ps-field">
                <label>Experience (years)</label>
                <input name="experience_years" type="number" min="0" step="0.5" value={form.experience_years} onChange={handleChange} placeholder="2" />
              </div>
              <div className="ps-field">
                <label>Education</label>
                <input name="education" value={form.education} onChange={handleChange} placeholder="B.S. Computer Science" />
              </div>
            </div>
            <div className="ps-actions">
              {profile?.profile_complete && (
                <button className="ps-btn-secondary" onClick={onComplete}>Cancel</button>
              )}
              <button className="ps-btn-primary" onClick={() => {
                if (!form.full_name.trim()) { setValidationMsg("Please enter your full name"); return; }
                setValidationMsg(""); setStep(2);
              }}>Next →</button>
            </div>
            {validationMsg && <div className="ps-validation">{validationMsg}</div>}
          </div>
        )}

        {/* Step 2: Skills & Goals */}
        {step === 2 && (
          <div className="ps-form">
            <div className="ps-field">
              <label>Skills (comma-separated) *</label>
              <textarea name="skills" value={form.skills} onChange={handleChange} placeholder="React, Python, Machine Learning, SQL, Git..." rows={3} />
              <span className="ps-hint">List your technical and soft skills, separated by commas</span>
            </div>
            <div className="ps-field">
              <label>Career Goal *</label>
              <textarea name="career_goal" value={form.career_goal} onChange={handleChange} placeholder="I want to become a full-stack developer and work at a product-based company..." rows={3} />
            </div>
            <div className="ps-field">
              <label>Preferred Companies (optional)</label>
              <input name="preferred_companies" value={form.preferred_companies} onChange={handleChange} placeholder="Google, Microsoft, Startup..." />
            </div>
            <div className="ps-actions">
              <button className="ps-btn-secondary" onClick={() => { setValidationMsg(""); setStep(1); }}>← Back</button>
              <button className="ps-btn-primary" onClick={() => {
                if (!form.skills.trim()) { setValidationMsg("Please enter at least one skill"); return; }
                if (!form.career_goal.trim()) { setValidationMsg("Please enter your career goal"); return; }
                setValidationMsg(""); setStep(3);
              }}>Next →</button>
            </div>
            {validationMsg && <div className="ps-validation">{validationMsg}</div>}
          </div>
        )}

        {/* Step 3: Resume */}
        {step === 3 && (
          <div className="ps-form">
            <div className="ps-field">
              <label>Upload Resume (PDF)</label>
              <label className="ps-file-drop" htmlFor="ps-resume">
                <span className="ps-file-icon"></span>
                <span>{file ? file.name : "Click to choose a PDF file"}</span>
                <input id="ps-resume" type="file" accept=".pdf" onChange={e => setFile(e.target.files[0])} hidden />
              </label>
              <span className="ps-hint">Optional — you can upload later from the Resume Checker tab</span>
            </div>

            {/* Summary */}
            <div className="ps-summary">
              <h3>Profile Summary</h3>
              <div className="ps-summary-items">
                <div><strong>Name:</strong> {form.full_name || "—"}</div>
                <div><strong>Position:</strong> {form.current_position || "—"}</div>
                <div><strong>Experience:</strong> {form.experience_years ? `${form.experience_years} years` : "—"}</div>
                <div><strong>Skills:</strong> {form.skills || "—"}</div>
                <div><strong>Goal:</strong> {form.career_goal || "—"}</div>
              </div>
            </div>

            <div className="ps-actions">
              <button className="ps-btn-secondary" onClick={() => setStep(2)}>← Back</button>
              <button
                className="ps-btn-primary save"
                onClick={handleSave}
                disabled={saving || uploading}
              >
                {saving ? (uploading ? "Uploading resume..." : "Saving...") : " Save Profile"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
