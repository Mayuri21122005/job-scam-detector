import { useState, useEffect } from "react";
import ReactSpeedometer from "react-d3-speedometer";

function App() {
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [aiStatus, setAiStatus] = useState("🧠 AI Ready");

  useEffect(() => {
    if (loading) {
      const msgs = [
        "🧠 AI Engine Processing...",
        "🔍 Scanning patterns...",
        "⚡ Detecting anomalies..."
      ];
      let i = 0;
      const interval = setInterval(() => {
        setAiStatus(msgs[i % msgs.length]);
        i++;
      }, 800);
      return () => clearInterval(interval);
    }
  }, [loading]);

  const analyze = async () => {
    if (!text && !url) {
      alert("Please enter job text or URL");
      return;
    }

    try {
      setLoading(true);

      const res = await fetch("http://127.0.0.1:5000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text, url })
      });

      const data = await res.json();

      setResult({
        prediction: data.prediction,
        risk_level: data.risk_level,
        risk_score: data.risk_score,
        company_status: data.company_status,
        primary_reason: data.primary_reason,
        confidence_note: data.confidence_note,
        risk_breakdown: data.risk_breakdown
      });

    } catch (err) {
      alert("Backend connection failed");
    } finally {
      setLoading(false);
    }
  };

  const Bar = ({ label, value, color }) => (
    <div style={{ marginBottom: "12px" }}>
      <p>{label}: {value}%</p>
      <div style={{ background: "#1f304c", height: "8px", borderRadius: "5px" }}>
        <div style={{
          width: `${Math.min(value, 100)}%`,
          background: color,
          height: "100%",
          borderRadius: "5px",
          transition: "0.5s"
        }} />
      </div>
    </div>
  );

  const getRiskColor = (level) => {
    if (level?.includes("High")) return "#ef4444";
    if (level?.includes("Medium")) return "#facc15";
    return "#22c55e";
  };

  return (
    <div style={{
      minHeight: "100vh",
      padding: "30px",
      color: "white",
      background: `
        radial-gradient(circle at 20% 30%, rgba(59,130,246,0.2), transparent),
        radial-gradient(circle at 80% 70%, rgba(239,68,68,0.2), transparent),
        linear-gradient(-45deg, #0d2075, #0f172a, #010824)
      `,
      backgroundSize: "400% 400%",
      animation: "bgMove 10s infinite alternate"
    }}>

      <style>{`
        @keyframes bgMove {
          0% { background-position: 0% 50%; }
          100% { background-position: 100% 50%; }
        }
      `}</style>

      <h1 style={{ textAlign: "center" }}>
        🧠 Fake Job Detection Using AI
      </h1>

      {/* INPUT */}
      <div style={{
        background: "rgba(255,255,255,0.05)",
        padding: "20px",
        borderRadius: "12px",
        maxWidth: "900px",
        margin: "auto"
      }}>
        <h3>Scan a Job Posting</h3>

        <input
          placeholder="Paste job link..."
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
        />

        <textarea
          placeholder="Paste job description..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          style={{ width: "100%", padding: "10px" }}
        />

        <button onClick={analyze} style={{
          marginTop: "10px",
          width: "100%",
          padding: "10px",
          background: "#3b82f6",
          border: "none",
          color: "white"
        }}>
          {loading ? "Analyzing..." : "Analyze Job"}
        </button>

        {loading && <p style={{ color: "#3b82f6" }}>{aiStatus}</p>}
      </div>

      {/* RESULT */}
      {result && (
        <>
          {(() => {
            const isHigh = result.risk_score > 70;

            return (
              <div style={{
                marginTop: "50px",
                textAlign: "center",
                padding: "25px",
                borderRadius: "12px",
                background: isHigh
                  ? "linear-gradient(135deg, rgba(239,68,68,0.2), rgba(2,6,23,0.8))"
                  : "linear-gradient(135deg, rgba(34,197,94,0.2), rgba(2,6,23,0.8))",
                border: isHigh
                  ? "1px solid rgba(239,68,68,0.4)"
                  : "1px solid rgba(34,197,94,0.4)",
                boxShadow: isHigh
                  ? "0 0 50px rgba(239,68,68,0.7)"
                  : "0 0 50px rgba(34,197,94,0.7)"
              }}>
                <h2 style={{
                  color: getRiskColor(result.risk_level),
                  fontSize: "42px",
                  fontWeight: "bold"
                }}>
                  {result.prediction}
                </h2>

                <p>{result.risk_level}</p>

                <p>Risk Score: {result.risk_score}%</p>

                <p style={{ color: "#38bdf8" }}>
                  AI Confidence: {result.risk_breakdown.ml.toFixed(2)}%
                </p>

                {/* 🔥 NEW */}
                {result.confidence_note && (
                  <p style={{ color: "#facc15" }}>
                    {result.confidence_note}
                  </p>
                )}

                <h3>Final Decision</h3>
                <p>
                  This job is classified as <b>{result.prediction}</b> based on AI + rule analysis.
                </p>

                {/* 🔥 NEW */}
                <p style={{ color:"#38bdf8", fontSize:"13px" }}>
                  ⚡ Hybrid Detection Engine Active • ML + Heuristic Analysis
                </p>
              </div>
            );
          })()}

          <p style={{ textAlign: "center", color: "#22c55e" }}>
            ✔ AI + Rule-Based Analysis Completed
          </p>

          {/* DASHBOARD */}
          <div style={{ display: "flex", gap: "30px", marginTop: "30px", flexWrap: "wrap" }}>

            <div style={{ flex: 1, minWidth: "250px" }}>
              <h3>Trust Score</h3>
              <ReactSpeedometer
                maxValue={100}
                value={result.risk_score}
                currentValueText={
                  result.risk_score > 70 ? "High Risk 🚨" :
                  result.risk_score > 30 ? "Medium Risk ⚠️" :
                  "Low Risk ✅"
                }
              />
            </div>

            <div style={{ flex: 1, minWidth: "250px" }}>
              <h3>Risk Factors</h3>
              <Bar label="AI" value={result.risk_breakdown.ml} color="#3b82f6" />
              <Bar label="Keyword" value={result.risk_breakdown.keyword} color="#ef4444" />
              <Bar label="Email" value={result.risk_breakdown.email} color="#f97316" />
              <Bar label="URL" value={result.risk_breakdown.url} color="#eab308" />
            </div>

            <div style={{ flex: 1, minWidth: "250px" }}>
              <h3>Analysis</h3>

              <p>
                <b>Company:</b>{" "}
                <span style={{
                  color: result.company_status.includes("Verified")
                    ? "#22c55e"
                    : "#facc15"
                }}>
                  {result.company_status}
                </span>
              </p>

              <p><b>Reason:</b> {result.primary_reason}</p>
            </div>

          </div>
        </>
      )}
    </div>
  );
}

export default App;