import { useAuth } from "../context/AuthContext";

export default function Topbar() {
  const { auth, logout } = useAuth();

  return (
    <div className="topbar">
      <div className="brand">
        <span className="brand-mark">Atlas</span>
        <span className="brand-tag">Task &amp; Knowledge System</span>
      </div>
      {auth && (
        <div className="topbar-right">
          <span className="role-chip">{auth.role} · {auth.username}</span>
          <button className="btn btn-outline" onClick={logout}>
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}
