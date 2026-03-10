import { Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";
import Dashboard from "./pages/Dashboard";
import IdeaDetail from "./pages/IdeaDetail";
import IdeasPage from "./pages/IdeasPage";
import OpportunityDetailPage from "./pages/OpportunityDetailPage";
import ProjectsPage from "./pages/ProjectsPage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="app-content">
        <Topbar />
        <main className="page-container">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/ideas" element={<IdeasPage />} />
            <Route path="/ideas/:ideaId" element={<IdeaDetail />} />
            <Route path="/opportunities/:clusterId" element={<OpportunityDetailPage />} />
            <Route path="/projects" element={<ProjectsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}
