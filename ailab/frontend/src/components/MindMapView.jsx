const mockNodes = [
  { id: "1", label: "AI tools" },
  { id: "2", label: "Проблема: потеря промптов" },
  { id: "3", label: "Идея: библиотека промптов" }
];

export default function MindMapView() {
  return (
    <section className="panel">
      <div className="panel-header">
        <h3>Mind Map</h3>
      </div>
      <div className="mindmap">
        {mockNodes.map((node) => (
          <div key={node.id} className="mindmap-node">
            {node.label}
          </div>
        ))}
      </div>
    </section>
  );
}
