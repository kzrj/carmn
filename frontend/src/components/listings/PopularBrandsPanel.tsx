import { Link } from "react-router-dom";
import { useState } from "react";
import { getLocale, pickName } from "../../lib/i18n";
import { t } from "../../lib/labels";
import type { Brand } from "../../types";

const COLLAPSED_COUNT = 16;

type Props = {
  brands: Brand[];
};

export default function PopularBrandsPanel({ brands }: Props) {
  const locale = getLocale();
  const [expanded, setExpanded] = useState(false);
  const canExpand = brands.length > COLLAPSED_COUNT;
  const visible = expanded || !canExpand ? brands : brands.slice(0, COLLAPSED_COUNT);

  if (brands.length === 0) return null;

  return (
    <section className="popular-brands card">
      <div className="popular-brands-grid">
        {visible.map((brand) => (
          <Link key={brand.id} to={`/${brand.slug}`} className="popular-brand-item">
            {brand.icon ? (
              <img src={brand.icon} alt="" className="popular-brand-icon" loading="lazy" />
            ) : (
              <span className="popular-brand-icon popular-brand-icon-placeholder" aria-hidden />
            )}
            <span className="popular-brand-name">{pickName(brand.name, locale)}</span>
          </Link>
        ))}
      </div>
      {canExpand && !expanded && (
        <button type="button" className="popular-brands-expand" onClick={() => setExpanded(true)}>
          {t("showAll", locale)}
          <span className="popular-brands-chevron" aria-hidden>
            ▾
          </span>
        </button>
      )}
    </section>
  );
}
