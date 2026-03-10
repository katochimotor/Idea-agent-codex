export default function IdeaScore({ score, tooltip }) {
  return (
    <span className="idea-score" title={tooltip || "Score рассчитывается из спроса, конкуренции, реализуемости и потенциала монетизации."}>
      Score {score}
    </span>
  );
}
