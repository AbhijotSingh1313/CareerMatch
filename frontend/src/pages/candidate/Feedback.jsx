import { useState, useEffect } from "react";
import { feedbackAPI } from "../../services/api";
import "../Dashboard.css";

export default function CandidateFeedback() {
  const [feedback, setFeedback] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    feedbackAPI.myFeedback()
      .then(setFeedback)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const typeColor = {
    rejection: { bg: "rgba(255,82,82,0.08)", border: "rgba(255,82,82,0.25)", badge: "#ff5252" },
    selection: { bg: "rgba(76,175,80,0.08)", border: "rgba(76,175,80,0.25)", badge: "#66bb6a" },
    general: { bg: "rgba(108,99,255,0.08)", border: "rgba(108,99,255,0.25)", badge: "#a89dff" },
  };

  if (loading) return <div className="dash-loading">Loading feedback...</div>;

  return (
    <div className="dashboard">
      <div className="dash-header">
        <h1> <span className="gradient-text">Your Feedback</span></h1>
        <p>Messages and feedback from recruiters</p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {feedback.map((f) => {
          const colors = typeColor[f.type] || typeColor.general;
          return (
            <div key={f.id} className="card" style={{ background: colors.bg, border: `1px solid ${colors.border}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                <span style={{ padding: "4px 12px", borderRadius: 20, fontSize: 12, fontWeight: 600, color: colors.badge, background: "rgba(255,255,255,0.05)", textTransform: "capitalize" }}>
                  {f.type}
                </span>
                <span style={{ color: "rgba(255,255,255,0.35)", fontSize: 12 }}>
                  {new Date(f.created_at).toLocaleDateString()}
                </span>
              </div>
              <p style={{ color: "rgba(255,255,255,0.8)", fontSize: 15, lineHeight: 1.7 }}>{f.message}</p>
            </div>
          );
        })}
        {feedback.length === 0 && <p className="empty-state" style={{ marginTop: 40 }}>No feedback received yet.</p>}
      </div>
    </div>
  );
}
