import IdeaCard from "./IdeaCard";

export default function IdeaList({ ideas, onCreateProject }) {
  return (
    <div className="idea-grid">
      {ideas.map((idea) => (
        <IdeaCard key={idea.id} idea={idea} onCreateProject={onCreateProject} />
      ))}
    </div>
  );
}
