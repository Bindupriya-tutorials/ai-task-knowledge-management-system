import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="auth-wrap">
      <div className="auth-card" style={{ textAlign: "center" }}>
        <div className="auth-eyebrow">Entry 404</div>
        <h1>Not filed</h1>
        <p className="auth-sub">This card isn&rsquo;t in the catalog.</p>
        <Link className="btn btn-primary" to="/">
          Back home
        </Link>
      </div>
    </div>
  );
}
