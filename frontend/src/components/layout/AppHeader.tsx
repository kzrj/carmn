import { Link } from "react-router-dom";
import { getLocale, setLocale } from "../../lib/i18n";
import { t } from "../../lib/labels";
import { authActions, authStore } from "../../store/authStore";
import type { Locale } from "../../types";

const LOCALES: { value: Locale; label: string }[] = [
  { value: "mn", label: "Монгол" },
  { value: "ru", label: "Русский" },
  { value: "en", label: "English" },
];

export default function AppHeader() {
  const { user, initialized } = authStore.useStore((s) => s);
  const locale = getLocale();

  const onLocale = (l: Locale) => {
    setLocale(l);
    window.location.reload();
  };

  return (
    <header className="app-header">
      <div className="app-header-inner">
        <Link to="/" className="logo">
          <strong>drom.mn</strong>
          <span className="muted logo-sub">авто зах зээл</span>
        </Link>
        <div className="header-actions">
          <Link to="/sell" className="btn btn-primary">
            {t("postAd", locale)}
          </Link>
          <label className="locale-select">
            <span className="sr-only">Language</span>
            <select
              value={locale}
              onChange={(e) => onLocale(e.target.value as Locale)}
              aria-label="Language"
            >
              {LOCALES.map(({ value, label }) => (
                <option key={value} value={value}>
                  {label}
                </option>
              ))}
            </select>
          </label>
          {initialized && !user && (
            <>
              <Link to="/login" className="btn btn-ghost">
                {t("login", locale)}
              </Link>
              <Link to="/register" className="btn btn-primary">
                {t("register", locale)}
              </Link>
            </>
          )}
          {user && (
            <button type="button" className="btn btn-ghost" onClick={() => authActions.logout()}>
              {user.phone} · {t("logout", locale)}
            </button>
          )}
        </div>
      </div>
    </header>
  );
}
