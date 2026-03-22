import { Link } from "react-router-dom";
import ThemeToggle from "../components/ThemeToggle";
import "./Landing.css";

export default function Landing() {
  return (
    <div className="landing">
      <div className="landing-header">
        <ThemeToggle />
      </div>
      {/* Hero */}
      <section className="hero">
        <h1 className="hero-title">
          CareerMatch AI
        </h1>
        <p className="hero-subtitle">
          Stop applying blindly. Understand your readiness, identify skill gaps, and get
          personalized learning paths to land your dream job.
        </p>
      </section>

      {/* Role Cards */}
      <section className="role-cards">
        <div className="role-card candidate-card">
          <div className="role-card-icon"><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" /><circle cx="12" cy="7" r="4" /></svg></div>
          <h2>I'm a Job Seeker</h2>
          <p>Get AI-powered job matching, skill gap analysis, and personalized learning recommendations</p>
          <Link to="/login/candidate" className="role-card-btn candidate-btn">Get Started</Link>
        </div>
        <div className="role-card recruiter-card">
          <div className="role-card-icon"><svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M22 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg></div>
          <h2>I'm a Recruiter</h2>
          <p>Find the best candidates with intelligent matching and detailed skill assessments</p>
          <Link to="/login/recruiter" className="role-card-btn recruiter-btn">Get Started</Link>
        </div>
      </section>

      {/* Why Choose */}
      <section className="features-section">
        <h2 className="features-title">Why Choose Our Platform?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" /><path d="M12 8v8" /><path d="M8 12h8" /></svg></div>
            <h3>AI-Powered Matching</h3>
            <p>Intelligent algorithms analyze skills, experience, and career goals for perfect matches</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18" /><path d="M18 17V9" /><path d="M13 17V5" /><path d="M8 17v-3" /></svg></div>
            <h3>Skill Gap Analysis</h3>
            <p>Identify exactly what skills you need and get personalized recommendations</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" /><polyline points="14 2 14 8 20 8" /><line x1="16" x2="8" y1="13" y2="13" /><line x1="16" x2="8" y1="17" y2="17" /><line x1="10" x2="8" y1="9" y2="9" /></svg></div>
            <h3>Resume ATS Checker</h3>
            <p>Check your resume against ATS requirements and get AI-powered suggestions</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z" /><path d="M6 12v5c3 3 9 3 12 0v-5" /></svg></div>
            <h3>Learning Paths</h3>
            <p>Get curated course recommendations to bridge your skill gaps</p>
          </div>
        </div>
      </section>

      <footer className="landing-footer">
        <p>CareerMatch AI — Built for smarter hiring</p>
      </footer>
    </div>
  );
}
