export default function buildMindMapData() {
  return {
    nodes: [
      { id: "niche", label: "AI tools" },
      { id: "problem", label: "Потеря промптов" },
      { id: "idea", label: "Библиотека промптов" }
    ],
    edges: [
      ["niche", "problem"],
      ["problem", "idea"]
    ]
  };
}
