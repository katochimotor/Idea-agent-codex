import { NavLink } from "react-router-dom";

const links = [
  { to: "/", label: "Дашборд" },
  { to: "/ideas", label: "Идеи" },
  { to: "/projects", label: "Проекты" },
  { to: "/settings", label: "Настройки" }
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <span className="brand-kicker">AI IDEA LAB</span>
        <h1>Лаборатория идей</h1>
      </div>
      <nav className="nav-list">
        {links.map((link) => (
          <NavLink key={link.to} to={link.to} className="nav-link">
            {link.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
