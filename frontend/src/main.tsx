import { FormEvent, StrictMode, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

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
      const response = await fetch("/api/research", {
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

  return (
    <main>
      <p className="eyebrow">Evidence-first intelligence</p>
      <h1>Enterprise Research Agent</h1>
      <p className="intro">A guarded workspace for research that can show where every important claim came from.</p>
      <form className="workspace" onSubmit={submitResearch}>
        <label>
          Research question
          <textarea
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="What would you like to investigate?"
            required
            minLength={3}
          />
        </label>
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
        <button type="submit" disabled={isLoading}>
          {isLoading ? "Researching..." : "Start research"}
        </button>
      </form>
      {error && <p className="message error">{error}</p>}
      {report && (
        <section className="report" aria-live="polite">
          <p className="eyebrow">{report.status.replace("_", " ")}</p>
          <p className="summary">{report.summary}</p>
          {report.claims && report.claims.length > 0 && (
            <ul>
              {report.claims.map((claim) => <li key={claim.claim_id}>{claim.text} ({claim.confidence})</li>)}
            </ul>
          )}
          {report.limitations && report.limitations.length > 0 && <p className="limitations">{report.limitations.join(" ")}</p>}
          {report.evidence && report.evidence.length > 0 && (
            <div className="sources">
              <strong>Sources</strong>
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
