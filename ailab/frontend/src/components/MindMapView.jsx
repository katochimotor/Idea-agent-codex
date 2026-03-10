function buildNodes(ideas) {
  return ideas.slice(0, 6).flatMap((idea) => [
    {
      id: `problem-${idea.id}`,
      label: `Проблема: ${idea.summary}`
    },
    {
      id: `idea-${idea.id}`,
      label: `Идея: ${idea.title}`
    }
  ]);
}

export default function MindMapView({ ideas = [] }) {
  const nodes = buildNodes(ideas);

  return (
    <section className="panel">
      <div className="panel-header">
        <h3>Mind Map</h3>
      </div>
      <div className="mindmap">
        {nodes.length ? (
          nodes.map((node) => (
            <div key={node.id} className="mindmap-node" title={node.label}>
              {node.label}
            </div>
          ))
        ) : (
          <p className="panel-subtitle">После загрузки идей здесь появятся связи проблема → идея.</p>
        )}
      </div>
    </section>
  );
}
