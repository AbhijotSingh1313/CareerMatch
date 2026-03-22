import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link, useParams } from "react-router-dom";
import "./Auth.css";

export default function Signup() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const { role: urlRole } = useParams();
  const role = urlRole === "recruiter" ? "recruiter" : "candidate";

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (password.length < 6) { setError("Password must be at least 6 characters"); return; }
    setLoading(true);
    try {
      const user = await signup(email, password, fullName, role);
      navigate(user.role === "recruiter" ? "/recruiter" : "/candidate");
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  return (
    <div className="auth-split">
      <div className={`auth-left ${role}`}>
        <Link to="/" className="back-link">← Back to Home</Link>
        <div className="auth-left-content">
          <div className="auth-left-icon">
            {role === "candidate" ? "" : ""}
          </div>
          <h1>
            {role === "candidate"
              ? "Start Your Career Journey"
              : "Hire Smarter with AI"}
          </h1>
          <p>
            {role === "candidate"
              ? "Create your profile, upload your resume, and let AI find the perfect job matches for you."
              : "Post jobs, compare candidates with AI, and make data-driven hiring decisions."}
          </p>
        </div>
        <div className="auth-left-features">
          {role === "candidate" ? (
            <>
              <div className="auth-feature"><span className="auth-feature-dot candidate-dot"></span> AI resume analysis</div>
              <div className="auth-feature"><span className="auth-feature-dot candidate-dot"></span> Smart job matching</div>
              <div className="auth-feature"><span className="auth-feature-dot candidate-dot"></span> Skill gap insights</div>
            </>
          ) : (
            <>
              <div className="auth-feature"><span className="auth-feature-dot recruiter-dot"></span> AI candidate ranking</div>
              <div className="auth-feature"><span className="auth-feature-dot recruiter-dot"></span> Automated shortlisting</div>
              <div className="auth-feature"><span className="auth-feature-dot recruiter-dot"></span> Skill assessment tools</div>
            </>
          )}
        </div>
      </div>

      <div className="auth-right">
        <div className="auth-form-container">
          <h2>Create Account</h2>
          <p className="auth-sub">Join CareerMatch AI as a {role}</p>

          {error && <div className="auth-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="auth-field">
              <label>Full Name</label>
              <div className="auth-input-wrap">
                <span className="input-icon"></span>
                <input type="text" value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="John Doe" required />
              </div>
            </div>
            <div className="auth-field">
              <label>{role === "recruiter" ? "Company Email" : "Personal Email"}</label>
              <div className="auth-input-wrap">
                <span className="input-icon"></span>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder={role === "recruiter" ? "you@company.com" : "you@example.com"} required />
              </div>
            </div>
            <div className="auth-field">
              <label>Password</label>
              <div className="auth-input-wrap">
                <span className="input-icon"></span>
                <input type={showPw ? "text" : "password"} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Min 6 characters" required />
                <button type="button" className="pw-toggle" onClick={() => setShowPw(!showPw)}>{showPw ? "" : ""}</button>
              </div>
            </div>
            <button type="submit" className={`auth-submit-btn ${role}`} disabled={loading}>
              {loading ? "Creating account..." : "Create Account"}
            </button>
          </form>

          <p className="auth-switch">
            Already have an account? <Link to={`/login/${role}`}>Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
