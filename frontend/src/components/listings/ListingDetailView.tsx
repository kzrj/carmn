import { formatMileage, formatPriceMnt } from "../../lib/format";
import { buildListingBreadcrumbs } from "../../lib/breadcrumbs";
import { getLocale, pickName } from "../../lib/i18n";
import { t } from "../../lib/labels";
import Breadcrumbs from "../layout/Breadcrumbs";
import LocalDateTime from "../LocalDateTime";
import type { ListingDetail } from "../../types";

type Props = {
  item: ListingDetail;
};

function SpecRow({ label, value }: { label: string; value: string }) {
  if (!value || value === "—") return null;
  return (
    <div className="spec-row">
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}

export default function ListingDetailView({ item }: Props) {
  const locale = getLocale();
  const title = `${pickName(item.brand.name, locale)} ${pickName(item.model.name, locale)}, ${item.year}`;
  const photos =
    item.photos.length > 0
      ? item.photos.map((p) => p.image)
      : item.primary_photo
        ? [item.primary_photo]
        : [];

  return (
    <article className="listing-detail">
      <Breadcrumbs items={buildListingBreadcrumbs(item, locale)} />

      <div className="listing-detail-layout">
        <div className="listing-gallery">
          {photos.length > 0 ? (
            photos.map((src, i) => (
              <img key={src + i} src={src} alt={`${title} ${i + 1}`} className="listing-gallery-img" />
            ))
          ) : (
            <div className="listing-card-no-photo listing-gallery-placeholder">—</div>
          )}
        </div>

        <div className="listing-detail-main">
          <h1>{title}</h1>
          {item.trim && <p className="muted">{pickName(item.trim.name, locale)}</p>}
          <p className="listing-detail-price">{formatPriceMnt(item.price)}</p>
          <p className="muted">
            {pickName(item.city.name, locale)} ·{" "}
            <LocalDateTime
              value={item.published_at}
              locale={locale === "mn" ? "mn-MN" : locale === "ru" ? "ru-RU" : "en-US"}
            />
          </p>

          {item.description && (
            <section className="detail-section">
              <h2>{t("description", locale)}</h2>
              <p className="listing-description">{item.description}</p>
            </section>
          )}

          <section className="detail-section">
            <h2>{t("specs", locale)}</h2>
            <dl className="spec-list">
              <SpecRow label={t("year", locale)} value={String(item.year)} />
              <SpecRow label={t("mileage", locale)} value={formatMileage(item.mileage)} />
              <SpecRow label={t("price", locale)} value={formatPriceMnt(item.price)} />
              <SpecRow label="Fuel" value={item.fuel ? pickName(item.fuel.name, locale) : "—"} />
              <SpecRow label="Transmission" value={item.transmission ? pickName(item.transmission.name, locale) : "—"} />
              <SpecRow label="Drive" value={item.drive ? pickName(item.drive.name, locale) : "—"} />
              <SpecRow label="Body" value={item.body_type ? pickName(item.body_type.name, locale) : "—"} />
              <SpecRow label="Color" value={item.color ? pickName(item.color.name, locale) : "—"} />
              <SpecRow label="Steering" value={item.steering} />
              <SpecRow label="Engine" value={item.engine_volume ? `${item.engine_volume} L` : "—"} />
              <SpecRow label="Power" value={item.power_hp ? `${item.power_hp} hp` : "—"} />
              <SpecRow label="Import" value={item.import_country ? pickName(item.import_country.name, locale) : "—"} />
            </dl>
          </section>

          <section className="detail-section">
            <h2>{t("seller", locale)}</h2>
            <p>{item.user.seller_profile.display_name || item.user.phone}</p>
            <p className="muted">{item.seller_type}</p>
          </section>
        </div>
      </div>
    </article>
  );
}
