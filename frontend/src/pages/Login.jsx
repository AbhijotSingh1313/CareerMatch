import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate, Link, useParams } from "react-router-dom";
import "./Auth.css";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { role: urlRole } = useParams();
  const role = urlRole === "recruiter" ? "recruiter" : "candidate";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const user = await login(email, password);
      navigate(user.role === "recruiter" ? "/recruiter" : "/candidate");
    } catch (err) {
      setError(err.message);
    } finally { setLoading(false); }
  };

  return (
    <div className="auth-split">
      {/* Left Panel */}
      <div className={`auth-left ${role}`}>
        <Link to="/" className="back-link">← Back to Home</Link>
        <div className="auth-left-content">
          <div className="auth-left-icon">
            {role === "candidate" ? "" : ""}
          </div>
          <h1>
            {role === "candidate"
              ? "Land Your Dream Job with AI"
              : "Find Top Talent with AI Matching"}
          </h1>
          <p>
            {role === "candidate"
              ? "Get personalized job matches, identify skill gaps, and follow a guided learning path to your ideal career."
              : "Leverage intelligent candidate matching, skill assessments, and data-driven insights to hire smarter and faster."}
          </p>
        </div>
        <div className="auth-left-features">
          {role === "candidate" ? (
            <>
              <div className="auth-feature"><span className="auth-feature-dot candidate-dot"></span> Smart job matching engine</div>
              <div className="auth-feature"><span className="auth-feature-dot candidate-dot"></span> Personalized learning paths</div>
              <div className="auth-feature"><span className="auth-feature-dot candidate-dot"></span> Career progression roadmap</div>
            </>
          ) : (
            <>
              <div className="auth-feature"><span className="auth-feature-dot recruiter-dot"></span> AI-powered candidate scoring</div>
              <div className="auth-feature"><span className="auth-feature-dot recruiter-dot"></span> Skill gap visualization</div>
              <div className="auth-feature"><span className="auth-feature-dot recruiter-dot"></span> Side-by-side comparisons</div>
            </>
          )}
        </div>
      </div>

      {/* Right Panel */}
      <div className="auth-right">
        <div className="auth-form-container">
          <h2>Welcome back</h2>
          <p className="auth-sub">Sign in to continue to your dashboard</p>

          {error && <div className="auth-error">{error}</div>}

          <form onSubmit={handleSubmit}>
            <div className="auth-field">
              <label>{role === "recruiter" ? "Company Email" : "Personal Email"}</label>
              <div className="auth-input-wrap">
                <span className="input-icon"></span>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={role === "recruiter" ? "you@company.com" : "you@example.com"}
                  required
                />
              </div>
            </div>
            <div className="auth-field">
              <label>Password</label>
              <div className="auth-input-wrap">
                <span className="input-icon"></span>
                <input
                  type={showPw ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  required
                />
                <button type="button" className="pw-toggle" onClick={() => setShowPw(!showPw)}>
                  {showPw ? "" : ""}
                </button>
              </div>
            </div>
            <button type="submit" className={`auth-submit-btn ${role}`} disabled={loading}>
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <p className="auth-switch">
            Don't have an account? <Link to={`/signup/${role}`}>Sign Up</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
