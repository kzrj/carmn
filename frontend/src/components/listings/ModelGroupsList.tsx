import { Link } from "react-router-dom";
import { formatGenerationLabel } from "../../lib/generationLabel";
import { formatCount, formatYearRange } from "../../lib/formatCount";
import { formatPriceMnt } from "../../lib/format";
import { getLocale, pickName } from "../../lib/i18n";
import { t } from "../../lib/labels";
import { modelGroupToLocation } from "../../lib/modelGroupLinks";
import type { ListingFilters, ListingModelGroup } from "../../types";

type Props = {
  groups: ListingModelGroup[];
  filters: ListingFilters;
};

function groupTitle(group: ListingModelGroup, locale: ReturnType<typeof getLocale>): string {
  const brand = pickName(group.brand.name, locale);
  const model = pickName(group.model.name, locale);
  const years = formatYearRange(group.year_from, group.year_to);
  if (group.trim) {
    const base = `${brand} ${model} · ${pickName(group.trim.name, locale)}`;
    return years ? `${base}, ${years}` : base;
  }
  if (group.generation) {
    return `${brand} ${model} · ${formatGenerationLabel(group.generation, locale)}`;
  }
  return years ? `${brand} ${model}, ${years}` : `${brand} ${model}`;
}

function ModelGroupPhotos({ photos, fallbackIcon }: { photos: string[]; fallbackIcon?: string | null }) {
  const slots = [
    photos[0] ?? fallbackIcon ?? null,
    photos[1] ?? null,
    photos[2] ?? null,
  ];

  return (
    <div className="model-group-photos" aria-hidden={photos.length === 0}>
      <div className="model-group-photos-main">
        {slots[0] ? (
          <img src={slots[0]} alt="" loading="lazy" />
        ) : (
          <span className="model-group-photos-placeholder" />
        )}
      </div>
      <div className="model-group-photos-side">
        {slots[1] ? (
          <img src={slots[1]} alt="" loading="lazy" />
        ) : (
          <span className="model-group-photos-placeholder" />
        )}
        {slots[2] ? (
          <img src={slots[2]} alt="" loading="lazy" />
        ) : (
          <span className="model-group-photos-placeholder" />
        )}
      </div>
    </div>
  );
}

export default function ModelGroupsList({ groups, filters }: Props) {
  const locale = getLocale();

  return (
    <ul className="model-groups-list">
      {groups.map((group) => {
        const to = modelGroupToLocation(group, filters);
        const title = groupTitle(group, locale);
        const priceHint =
          group.min_price != null && group.max_price != null
            ? group.min_price === group.max_price
              ? formatPriceMnt(group.min_price)
              : `${formatPriceMnt(group.min_price)} — ${formatPriceMnt(group.max_price)}`
            : null;

        return (
          <li key={`${group.brand.id}-${group.model.id}-${group.generation?.id ?? 0}-${group.trim?.id ?? 0}`}>
            <Link
              to={{ pathname: to.pathname, search: to.search ? `?${to.search}` : "" }}
              className="model-group-card"
            >
              <ModelGroupPhotos photos={group.photos} fallbackIcon={group.brand.icon} />
              <div className="model-group-body">
                <h3 className="model-group-title">{title}</h3>
                {priceHint && <p className="model-group-price">{priceHint}</p>}
                {group.specs_summary && <p className="model-group-specs muted">{group.specs_summary}</p>}
                <p className="model-group-count-line muted">
                  {formatCount(group.count, locale)} {t("listingsCountShort", locale)}
                </p>
              </div>
            </Link>
          </li>
        );
      })}
    </ul>
  );
}

export function modelGroupsEmptyLabel(locale: ReturnType<typeof getLocale>): string {
  return t("noModelGroups", locale);
}
