import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { getLocale } from "../lib/i18n";
import { t } from "../lib/labels";

export default function SellVinPage() {
  const locale = getLocale();
  const [vin, setVin] = useState("");
  const [stubShown, setStubShown] = useState(false);

  const onSubmit = (e: FormEvent) => {
    e.preventDefault();
    setStubShown(true);
  };

  return (
    <div className="sell-page page-pad">
      <h1>{t("postAdTitle", locale)}</h1>
      <p className="muted sell-hint">{t("postAdVinHint", locale)}</p>

      <form className="card sell-card" onSubmit={onSubmit}>
        <label className="field">
          <span className="field-label">{t("vin", locale)}</span>
          <input
            value={vin}
            onChange={(e) => setVin(e.target.value.toUpperCase())}
            placeholder={t("vinPlaceholder", locale)}
            maxLength={17}
          />
        </label>

        {stubShown && (
          <div className="sell-stub">
            <strong>{t("vinStubTitle", locale)}</strong>
            <p className="muted">{t("vinStubText", locale)}</p>
            <Link to="/sell/manual" className="btn btn-primary">
              {t("fillManual", locale)}
            </Link>
          </div>
        )}

        <div className="sell-actions">
          <button type="submit" className="btn btn-primary">
            {t("continue", locale)}
          </button>
          <Link to="/sell/manual" className="btn btn-ghost">
            {t("fillManual", locale)}
          </Link>
        </div>
      </form>
    </div>
  );
}
