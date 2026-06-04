import { FormEvent, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { getLocale } from "../lib/i18n";
import { t } from "../lib/labels";
import { authActions, authStore } from "../store/authStore";

export default function LoginPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const locale = getLocale();
  const { loading, error } = authStore.useStore((s) => s);
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await authActions.login(phone, password);
      const next = searchParams.get("next");
      navigate(next && next.startsWith("/") ? next : "/");
    } catch {
      /* error in store */
    }
  };

  return (
    <div className="auth-page page-pad">
      <h1>{t("login", locale)}</h1>
      <form className="auth-form card" onSubmit={onSubmit}>
        <label>
          Phone
          <input value={phone} onChange={(e) => setPhone(e.target.value)} required autoComplete="tel" />
        </label>
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {t("login", locale)}
        </button>
      </form>
      <p className="muted">
        <Link to="/register">{t("register", locale)}</Link>
      </p>
    </div>
  );
}
