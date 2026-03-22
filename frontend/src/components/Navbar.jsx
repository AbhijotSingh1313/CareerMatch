import { Link, useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import ThemeToggle from "./ThemeToggle";
import "./Navbar.css";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (!user) return null;

  const isCandidate = user.role === "candidate";
  const base = isCandidate ? "/candidate" : "/recruiter";

  const candidateLinks = [
    { path: `${base}`, label: "Dashboard", icon: "" },
    { path: `${base}/resume`, label: "Resume", icon: "" },
    { path: `${base}/jobs`, label: "Jobs", icon: "" },
    { path: `${base}/skills`, label: "Skills", icon: "" },
    { path: `${base}/feedback`, label: "Feedback", icon: "" },
  ];

  const recruiterLinks = [
    { path: `${base}`, label: "Dashboard", icon: "" },
    { path: `${base}/jobs`, label: "My Jobs", icon: "" },
    { path: `${base}/candidates`, label: "Candidates", icon: "" },
    { path: `${base}/feedback`, label: "Feedback", icon: "" },
  ];

  const links = isCandidate ? candidateLinks : recruiterLinks;

  return (
    <nav className="navbar">
      <div className="nav-brand">
        <Link to={base}>
          <span className="nav-logo"></span>
          <span className="nav-title">CareerMatch AI</span>
        </Link>
      </div>

      <div className="nav-links">
        {links.map((link) => (
          <Link
            key={link.path}
            to={link.path}
            className={`nav-link ${location.pathname === link.path ? "active" : ""}`}
          >
            <span className="nav-link-icon">{link.icon}</span>
            <span>{link.label}</span>
          </Link>
        ))}
      </div>

      <div className="nav-user">
        <div className="nav-user-info">
          <span className="nav-user-name">{user.full_name}</span>
          <span className="nav-user-role">{user.role}</span>
        </div>
        <ThemeToggle />
        <button onClick={handleLogout} className="nav-logout">
          Logout
        </button>
      </div>
    </nav>
  );
}
