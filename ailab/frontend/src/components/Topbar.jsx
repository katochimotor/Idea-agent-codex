import { Link } from "react-router-dom";

export default function Topbar() {
  return (
    <header className="topbar">
      <div>
        <div className="eyebrow">Local-first research dashboard</div>
        <h2>AI Idea Research Lab</h2>
      </div>
      <Link className="secondary-button" to="/settings">
        Настройки
      </Link>
    </header>
  );
}
