export default function TrendGraph({ trends = [] }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <h3>Тренды</h3>
      </div>
      <div className="trend-list">
        {trends.map((trend) => (
          <div key={trend} className="trend-pill">
            {trend}
          </div>
        ))}
      </div>
    </section>
  );
}
