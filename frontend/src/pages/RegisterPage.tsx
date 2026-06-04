import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { getLocale } from "../lib/i18n";
import { t } from "../lib/labels";
import { authActions, authStore } from "../store/authStore";

export default function RegisterPage() {
  const navigate = useNavigate();
  const locale = getLocale();
  const { loading, error } = authStore.useStore((s) => s);
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [sellerType, setSellerType] = useState("private");

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await authActions.register({ phone, password, seller_type: sellerType, display_name: displayName });
      navigate("/");
    } catch {
      /* error in store */
    }
  };

  return (
    <div className="auth-page page-pad">
      <h1>{t("register", locale)}</h1>
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
            minLength={6}
            autoComplete="new-password"
          />
        </label>
        <label>
          Name
          <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
        </label>
        <label>
          Seller type
          <select value={sellerType} onChange={(e) => setSellerType(e.target.value)}>
            <option value="private">Private</option>
            <option value="owner">Owner</option>
            <option value="company">Company</option>
          </select>
        </label>
        {error && <p className="error">{error}</p>}
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {t("register", locale)}
        </button>
      </form>
      <p className="muted">
        <Link to="/login">{t("login", locale)}</Link>
      </p>
    </div>
  );
}
