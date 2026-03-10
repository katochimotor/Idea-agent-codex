import IdeaCard from "./IdeaCard";

export default function IdeaList({ ideas, onCreateProject, creatingProjectId = null }) {
  if (!ideas.length) {
    return (
      <div className="panel">
        <h3>Идей пока нет</h3>
        <p>Запустите поиск, чтобы загрузить реальные идеи из базы.</p>
      </div>
    );
  }

  return (
    <div className="idea-grid">
      {ideas.map((idea) => (
        <IdeaCard
          key={idea.id}
          idea={{ ...idea, creating_project: creatingProjectId === idea.id }}
          onCreateProject={onCreateProject}
        />
      ))}
    </div>
  );
}
