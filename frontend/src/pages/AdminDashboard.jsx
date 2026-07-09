import { useEffect, useState, useCallback } from "react";
import Topbar from "../components/Topbar";
import client from "../api/client";

export default function AdminDashboard() {
  const [tab, setTab] = useState("overview");
  const [analytics, setAnalytics] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [users, setUsers] = useState([]);

  const [docTitle, setDocTitle] = useState("");
  const [docFile, setDocFile] = useState(null);
  const [docMsg, setDocMsg] = useState("");

  const [taskForm, setTaskForm] = useState({ title: "", description: "", assigned_to: "", document_id: "" });
  const [taskMsg, setTaskMsg] = useState("");

  const [statusFilter, setStatusFilter] = useState("");

  const loadAll = useCallback(async () => {
    const [a, d, t, u] = await Promise.all([
      client.get("/analytics"),
      client.get("/documents"),
      client.get("/tasks", { params: statusFilter ? { status: statusFilter } : {} }),
      client.get("/users"),
    ]);
    setAnalytics(a.data);
    setDocuments(d.data);
    setTasks(t.data);
    setUsers(u.data);
  }, [statusFilter]);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const handleUpload = async (e) => {
    e.preventDefault();
    setDocMsg("");
    if (!docFile) {
      setDocMsg("Choose a .txt file first.");
      return;
    }
    const formData = new FormData();
    formData.append("title", docTitle);
    formData.append("file", docFile);
    try {
      await client.post("/documents", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setDocMsg("Document added to the knowledge base.");
      setDocTitle("");
      setDocFile(null);
      e.target.reset();
      loadAll();
    } catch (err) {
      setDocMsg(err?.response?.data?.detail || "Upload failed.");
    }
  };

  const handleCreateTask = async (e) => {
    e.preventDefault();
    setTaskMsg("");
    try {
      await client.post("/tasks", {
        title: taskForm.title,
        description: taskForm.description || null,
        assigned_to: taskForm.assigned_to ? Number(taskForm.assigned_to) : null,
        document_id: taskForm.document_id ? Number(taskForm.document_id) : null,
      });
      setTaskMsg("Task created and assigned.");
      setTaskForm({ title: "", description: "", assigned_to: "", document_id: "" });
      loadAll();
    } catch (err) {
      setTaskMsg(err?.response?.data?.detail || "Could not create task.");
    }
  };

  return (
    <div className="app-shell">
      <Topbar />

      {analytics && (
        <div className="stat-strip">
          <div className="stat-cell">
            <div className="stat-value">{analytics.total_tasks}</div>
            <div className="stat-label">Total tasks</div>
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
            <div className="stat-label">Documents</div>
          </div>
          <div className="stat-cell">
            <div className="stat-value">{analytics.total_users}</div>
            <div className="stat-label">Users</div>
          </div>
        </div>
      )}

      <div className="tab-row">
        {["overview", "documents", "tasks"].map((t) => (
          <button
            key={t}
            className={`tab-btn ${tab === t ? "active" : ""}`}
            onClick={() => setTab(t)}
          >
            {t}
          </button>
        ))}
      </div>

      {tab === "overview" && analytics && (
        <div className="panel">
          <h3>Most searched queries</h3>
          {analytics.most_searched_queries.length === 0 ? (
            <div className="empty-state">No searches logged yet.</div>
          ) : (
            <div className="card-grid">
              {analytics.most_searched_queries.map((q, i) => (
                <div className="index-card" key={i}>
                  <div className="index-card-title">&ldquo;{q.query}&rdquo;</div>
                  <div className="index-card-meta">
                    <span>searched</span>
                    <span className="stamp stamp-pending">{q.count}×</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "documents" && (
        <>
          <div className="panel">
            <h3>Add a document to the knowledge base</h3>
            <form onSubmit={handleUpload}>
              <div className="form-row">
                <div className="field">
                  <label htmlFor="docTitle">Title</label>
                  <input
                    id="docTitle"
                    value={docTitle}
                    onChange={(e) => setDocTitle(e.target.value)}
                    required
                  />
                </div>
                <div className="field">
                  <label htmlFor="docFile">File (.txt)</label>
                  <input
                    id="docFile"
                    type="file"
                    accept=".txt,.md"
                    onChange={(e) => setDocFile(e.target.files[0])}
                    required
                  />
                </div>
              </div>
              {docMsg && <p className="helper-text">{docMsg}</p>}
              <button className="btn btn-primary" type="submit">
                Upload &amp; embed
              </button>
            </form>
          </div>

          <div className="section-header">
            <span className="section-title">Knowledge base</span>
            <span className="section-index">{documents.length} document(s)</span>
          </div>
          {documents.length === 0 ? (
            <div className="empty-state">No documents uploaded yet.</div>
          ) : (
            <div className="card-grid">
              {documents.map((doc) => (
                <div className="index-card" key={doc.id}>
                  <div className="index-card-head">
                    <span className="index-card-title">{doc.title}</span>
                  </div>
                  <div className="index-card-body">{doc.content_preview?.slice(0, 140)}…</div>
                  <div className="index-card-meta">
                    <span>{doc.filename}</span>
                    <span>#{doc.id}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {tab === "tasks" && (
        <>
          <div className="panel">
            <h3>Create &amp; assign a task</h3>
            <form onSubmit={handleCreateTask}>
              <div className="form-row">
                <div className="field">
                  <label htmlFor="taskTitle">Title</label>
                  <input
                    id="taskTitle"
                    value={taskForm.title}
                    onChange={(e) => setTaskForm({ ...taskForm, title: e.target.value })}
                    required
                  />
                </div>
                <div className="field">
                  <label htmlFor="assignTo">Assign to</label>
                  <select
                    id="assignTo"
                    value={taskForm.assigned_to}
                    onChange={(e) => setTaskForm({ ...taskForm, assigned_to: e.target.value })}
                  >
                    <option value="">— Unassigned —</option>
                    {users
                      .filter((u) => u.role === "user")
                      .map((u) => (
                        <option key={u.id} value={u.id}>
                          {u.username}
                        </option>
                      ))}
                  </select>
                </div>
              </div>
              <div className="form-row">
                <div className="field">
                  <label htmlFor="taskDesc">Description</label>
                  <textarea
                    id="taskDesc"
                    value={taskForm.description}
                    onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
                  />
                </div>
                <div className="field">
                  <label htmlFor="relatedDoc">Related document</label>
                  <select
                    id="relatedDoc"
                    value={taskForm.document_id}
                    onChange={(e) => setTaskForm({ ...taskForm, document_id: e.target.value })}
                  >
                    <option value="">— None —</option>
                    {documents.map((d) => (
                      <option key={d.id} value={d.id}>
                        {d.title}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              {taskMsg && <p className="helper-text">{taskMsg}</p>}
              <button className="btn btn-primary" type="submit">
                Create task
              </button>
            </form>
          </div>

          <div className="section-header">
            <span className="section-title">All tasks</span>
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
          </div>
          {tasks.length === 0 ? (
            <div className="empty-state">No tasks match this filter.</div>
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
                    <span>assigned #{t.assigned_to ?? "—"}</span>
                    <span>#{t.id}</span>
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
