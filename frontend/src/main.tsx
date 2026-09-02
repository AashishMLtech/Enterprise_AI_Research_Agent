import { FormEvent, StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const API_URL = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

type ResearchReport = {
  status: "complete" | "insufficient_evidence" | "blocked";
  summary: string;
  claims?: { claim_id: string; text: string; confidence: string }[];
  evidence?: { evidence_id: string; source_id: string; text: string }[];
  limitations?: string[];
};

function App() {
  const [question, setQuestion] = useState("");
  const [industry, setIndustry] = useState("default");
  const [depth, setDepth] = useState("balanced");
  const [report, setReport] = useState<ResearchReport | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function submitResearch(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setReport(null);
    setIsLoading(true);

    try {
      const response = await fetch(`${API_URL}/api/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question, industry, depth }),
      });

      if (!response.ok) {
        const detail = await response.json().catch(() => null);
        throw new Error(detail?.detail ?? `Request failed (${response.status})`);
      }

      setReport(await response.json());
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Unable to reach the research API.");
    } finally {
      setIsLoading(false);
    }
  }

  function clearWorkspace() {
    setQuestion("");
    setReport(null);
    setError("");
  }

  return (
    <main>
      <nav className="topbar"><span className="brand-mark">◆</span><span>RESEARCH / WORKSPACE</span><span className="topbar-status"><i /> SYSTEM READY</span></nav>
      <header className="hero">
        <div>
          <p className="eyebrow"><span className="signal-dot" /> Evidence-first intelligence</p>
          <h1>Enterprise <em>Research</em> Agent</h1>
          <p className="intro">A guarded workspace for research that can show where every important claim came from.</p>
        </div>
        <div className="hero-mark" aria-hidden="true"><span>RA</span></div>
      </header>
      <form className="workspace" onSubmit={submitResearch}>
        <div className="section-heading"><span className="section-number">01</span><div><p className="section-kicker">Research input</p><h2>What would you like to investigate?</h2></div></div>
        <label className="question-label">
          Research question <span>Required</span>
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="What would you like to investigate?"
            required
            minLength={3}
          />
        </label>
        <div className="examples"><span>Try an example</span><button type="button" onClick={() => { setIndustry("banking"); setQuestion("What are the main risks affecting digital banking adoption?"); }}>Digital banking risks</button><button type="button" onClick={() => { setIndustry("retail"); setQuestion("How is inventory technology changing modern retail?"); }}>Retail inventory</button></div>
        <div className="controls">
          <label>
            Industry
            <select value={industry} onChange={(event) => setIndustry(event.target.value)}>
              <option value="default">Default</option>
              <option value="banking">Banking</option>
              <option value="retail">Retail</option>
            </select>
          </label>
          <label>
            Depth
            <select value={depth} onChange={(event) => setDepth(event.target.value)}>
              <option value="balanced">Balanced</option>
              <option value="fast">Fast</option>
              <option value="deep">Deep</option>
            </select>
          </label>
        </div>
        <div className="action-row"><button className="primary-action" type="submit" disabled={isLoading}><span>{isLoading ? "Researching..." : "Start research"}</span><b>→</b></button><button className="secondary-action" type="button" onClick={clearWorkspace}>Clear workspace</button></div>
      </form>
      {error && <p className="message error">{error}</p>}
      {report && (
        <section className="report" aria-live="polite">
          <div className="report-header">
            <p className="eyebrow"><span className="signal-dot" /> {report.status.replace("_", " ")}</p>
            <span className="report-label">Research brief</span>
          </div>
          <h2>Research explanation</h2>
          <p className="summary">{report.summary}</p>
          {report.claims && report.claims.length > 0 && (
            <>
              <h2>Key findings</h2>
              <ul className="claims">
              {report.claims.map((claim) => <li key={claim.claim_id}><span className="claim-marker" /> <span>{claim.text}</span><strong>{claim.confidence}</strong></li>)}
              </ul>
            </>
          )}
          {report.limitations && report.limitations.length > 0 && (
            <>
              <h2>Limitations</h2>
              <p className="limitations">{report.limitations.join(" ")}</p>
            </>
          )}
          {report.evidence && report.evidence.length > 0 && (
            <div className="sources">
              <h2>Sources</h2>
              <ul>
                {report.evidence.map((item) => (
                  <li key={item.evidence_id}>
                    <a href={item.source_id} target="_blank" rel="noreferrer">{item.source_id}</a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}
    </main>
  );
}

createRoot(document.getElementById("root")!).render(<StrictMode><App /></StrictMode>);
