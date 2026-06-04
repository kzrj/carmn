import { Link } from "react-router-dom";
import { formatMileage, formatPriceMnt } from "../../lib/format";
import { getLocale, pickName } from "../../lib/i18n";
import LocalDateTime from "../LocalDateTime";
import type { ListingListItem } from "../../types";

type Props = {
  item: ListingListItem;
};

export default function ListingCard({ item }: Props) {
  const locale = getLocale();
  const title = `${pickName(item.brand.name, locale)} ${pickName(item.model.name, locale)}, ${item.year}`;

  return (
    <Link to={`/listing/${item.id}`} className="listing-card">
      <div className="listing-card-photo">
        {item.primary_photo ? (
          <img src={item.primary_photo} alt={title} loading="lazy" />
        ) : (
          <div className="listing-card-no-photo">—</div>
        )}
      </div>
      <div className="listing-card-body">
        <h3 className="listing-card-title">{title}</h3>
        <p className="listing-card-meta">
          {formatMileage(item.mileage)} · {pickName(item.city.name, locale)}
        </p>
        <p className="listing-card-price">{formatPriceMnt(item.price)}</p>
        <p className="listing-card-date muted">
          <LocalDateTime value={item.published_at} locale={locale === "mn" ? "mn-MN" : locale === "ru" ? "ru-RU" : "en-US"} />
        </p>
      </div>
    </Link>
  );
}
