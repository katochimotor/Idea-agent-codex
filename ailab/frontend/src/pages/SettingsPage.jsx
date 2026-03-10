import { useEffect, useState } from "react";
import { fetchProviderSettings, saveProviderSettings, testProviderConnection } from "../api/settings_api";

const PROVIDER_LABELS = {
  codex_cli: "Codex CLI",
  openai: "OpenAI API",
  anthropic: "Anthropic"
};

export default function SettingsPage() {
  const [provider, setProvider] = useState("codex_cli");
  const [apiKey, setApiKey] = useState("");
  const [providers, setProviders] = useState([]);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [testing, setTesting] = useState(false);
  const [saving, setSaving] = useState(false);
  const [theme, setTheme] = useState(() => window.localStorage.getItem("ailab-theme") || "light");

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("ailab-theme", theme);
  }, [theme]);

  async function loadSettings() {
    const payload = await fetchProviderSettings();
    setProviders(payload.providers);
    setProvider(payload.active_provider || payload.providers[0]?.provider || "codex_cli");
  }

  useEffect(() => {
    loadSettings().catch((error) => {
      setErrorMessage(error.message || "Не удалось загрузить настройки провайдера.");
    });
  }, []);

  async function handleTest() {
    setTesting(true);
    setStatusMessage("");
    setErrorMessage("");
    try {
      const result = await testProviderConnection({
        provider,
        api_key: apiKey.trim() || null
      });
      setStatusMessage(result.message || "Подключение успешно проверено.");
      await loadSettings();
    } catch (error) {
      setErrorMessage(error.message || "Проверка подключения не удалась.");
    } finally {
      setTesting(false);
    }
  }

  async function handleSave() {
    setSaving(true);
    setStatusMessage("");
    setErrorMessage("");
    try {
      const result = await saveProviderSettings({
        provider,
        api_key: apiKey.trim() || null
      });
      setStatusMessage(`Сохранено: ${result.label} (${result.model_name})`);
      setApiKey("");
      await loadSettings();
    } catch (error) {
      setErrorMessage(error.message || "Не удалось сохранить настройки.");
    } finally {
      setSaving(false);
    }
  }

  const selectedProviderConfig = providers.find((item) => item.provider === provider);

  return (
    <section className="panel settings-panel">
      <div className="page-header">
        <div>
          <h1>Настройки AI</h1>
          <p>Выберите провайдера, проверьте подключение и сохраните активную конфигурацию. Для Codex CLI API key не нужен.</p>
        </div>
      </div>

      <div className="settings-form">
        <label className="settings-field">
          <span>Провайдер</span>
          <select value={provider} onChange={(event) => setProvider(event.target.value)}>
            <option value="codex_cli">Codex CLI</option>
            <option value="openai">OpenAI API</option>
            <option value="anthropic">Anthropic</option>
          </select>
        </label>

        <label className="settings-field">
          <span>API key</span>
          <input
            type="password"
            value={apiKey}
            onChange={(event) => setApiKey(event.target.value)}
            placeholder={provider === "codex_cli" ? "Для Codex CLI ключ не требуется" : "Вставьте API key"}
            disabled={provider === "codex_cli"}
          />
        </label>

        <label className="settings-field">
          <span>Тема</span>
          <select value={theme} onChange={(event) => setTheme(event.target.value)}>
            <option value="light">Light</option>
            <option value="dark">Dark</option>
          </select>
        </label>

        <div className="settings-hint">
          <strong>Сохранённая конфигурация:</strong>{" "}
          {selectedProviderConfig?.provider === "codex_cli"
            ? "Codex CLI используется локально без API key."
            : selectedProviderConfig?.has_api_key
            ? `${selectedProviderConfig.label} (${selectedProviderConfig.api_key_hint})`
            : "для этого провайдера ключ ещё не сохранён"}
        </div>

        <div className="settings-actions">
          <button className="secondary-button" type="button" onClick={handleTest} disabled={testing || saving}>
            {testing ? "Проверка..." : "Проверить подключение"}
          </button>
          <button className="primary-button" type="button" onClick={handleSave} disabled={saving || testing}>
            {saving ? "Сохранение..." : "Сохранить"}
          </button>
        </div>

        {statusMessage ? <p className="settings-success">{statusMessage}</p> : null}
        {errorMessage ? <p className="job-error">{errorMessage}</p> : null}
      </div>

      <div className="settings-provider-list">
        {providers.map((item) => (
          <div key={item.provider} className="settings-provider-card">
            <div className="panel-header">
              <strong>{PROVIDER_LABELS[item.provider] || item.label}</strong>
              {item.is_active ? <span className="tag">Активен</span> : <span className="soft-tag">Неактивен</span>}
            </div>
            <p>Модель: {item.model_name}</p>
            <p>Ключ: {item.has_api_key ? item.api_key_hint : "не сохранён"}</p>
            <p>Последняя проверка: {item.last_tested_at ? new Date(item.last_tested_at).toLocaleString() : "ещё не проверялся"}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
