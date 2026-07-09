import { useEffect, useState, useCallback } from "react";
import Topbar from "../components/Topbar";
import client from "../api/client";

export default function UserDashboard() {
  const [tab, setTab] = useState("search");
  const [query, setQuery] = useState("");
  const [results, setResults] = useState(null);
  const [searching, setSearching] = useState(false);

  const [tasks, setTasks] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [analytics, setAnalytics] = useState(null);

  const loadTasks = useCallback(async () => {
    const { data } = await client.get("/tasks", {
      params: statusFilter ? { status: statusFilter } : {},
    });
    setTasks(data);
  }, [statusFilter]);

  useEffect(() => {
    loadTasks();
    client.get("/analytics").then((r) => setAnalytics(r.data));
  }, [loadTasks]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setSearching(true);
    try {
      const { data } = await client.post("/search", { query, top_k: 5 });
      setResults(data);
    } finally {
      setSearching(false);
    }
  };

  const markComplete = async (task) => {
    const nextStatus = task.status === "completed" ? "pending" : "completed";
    await client.patch(`/tasks/${task.id}`, { status: nextStatus });
    loadTasks();
  };

  return (
    <div className="app-shell">
      <Topbar />

      {analytics && (
        <div className="stat-strip">
          <div className="stat-cell">
            <div className="stat-value">{analytics.total_tasks}</div>
            <div className="stat-label">My tasks</div>
          </div>
          <div className="stat-cell">
            <div className="stat-value">{analytics.completed_tasks}</div>
            <div className="stat-label">Completed</div>
          </div>
          <div className="stat-cell">
            <div className="stat-value">{analytics.pending_tasks}</div>
            <div className="stat-label">Pending</div>
          </div>
          <div className="stat-cell">
            <div className="stat-value">{analytics.total_documents}</div>
            <div className="stat-label">Documents available</div>
          </div>
        </div>
      )}

      <div className="tab-row">
        {["search", "tasks"].map((t) => (
          <button
            key={t}
            className={`tab-btn ${tab === t ? "active" : ""}`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "search" && (
        <>
          <form className="search-bar" onSubmit={handleSearch}>
            <input
              placeholder="Ask the knowledge base something…"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button className="btn btn-primary" type="submit" disabled={searching}>
              {searching ? "Searching…" : "Search"}
            </button>
          </form>

          {results === null && (
            <div className="empty-state">Run a search to see semantically matched documents.</div>
          )}
          {results && results.length === 0 && (
            <div className="empty-state">No matching documents found.</div>
          )}
          {results &&
            results.map((r, i) => (
              <div className="search-result" key={i}>
                <div className="search-result-head">
                  <span className="search-result-title">{r.title}</span>
                  <span className="search-score">match {(r.score * 100).toFixed(1)}%</span>
                </div>
                <div className="search-result-snippet">{r.snippet}…</div>
              </div>
            ))}
        </>
      )}

      {tab === "tasks" && (
        <>
          <div className="filter-row">
            <select
              className="status-select"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          {tasks.length === 0 ? (
            <div className="empty-state">No tasks assigned to you yet.</div>
          ) : (
            <div className="card-grid">
              {tasks.map((t) => (
                <div className="index-card" key={t.id}>
                  <div className="index-card-head">
                    <span className="index-card-title">{t.title}</span>
                    <span className={`stamp ${t.status === "completed" ? "stamp-completed" : "stamp-pending"}`}>
                      {t.status}
                    </span>
                  </div>
                  {t.description && <div className="index-card-body">{t.description}</div>}
                  <div className="index-card-meta">
                    <span>#{t.id}</span>
                    <button className="btn btn-outline" onClick={() => markComplete(t)}>
                      {t.status === "completed" ? "Mark pending" : "Mark complete"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
}
