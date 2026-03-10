export default function GenerateButton({ onClick, loading = false }) {
  return (
    <button className="primary-button" type="button" onClick={onClick} disabled={loading}>
      {loading ? "Генерация..." : "Найти идеи"}
    </button>
  );
}
