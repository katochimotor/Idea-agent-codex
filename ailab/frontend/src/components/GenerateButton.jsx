export default function GenerateButton({ onClick, loading = false, polling = false }) {
  return (
    <button className="primary-button" type="button" onClick={onClick} disabled={loading}>
      {polling ? "Pipeline работает..." : loading ? "Запуск..." : "Найти идеи"}
    </button>
  );
}
