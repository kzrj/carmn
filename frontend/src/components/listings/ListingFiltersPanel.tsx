import { generationSelectOptions } from "../../lib/generationLabel";
import {
  ENGINE_VOLUME_PRESETS,
  PRICE_PRESETS_MNT,
  formatEngineVolumePreset,
  formatPricePresetMnt,
  yearFilterOptions,
} from "../../lib/filterPresets";
import { getLocale, pickName } from "../../lib/i18n";
import { t } from "../../lib/labels";
import type { Generation, ListingFilters, ReferenceBundle, TransmissionRef, VehicleModel } from "../../types";
import {
  BodyTypePickerField,
  CheckboxField,
  ColorPickerField,
  CompactSelect,
  FilterDropdown,
  FilterDropdownRange,
  FilterPresetRange,
  InputField,
  RadioSegment,
  RangeControl,
  SelectField,
} from "../ui/Fields";

const RADIUS_OPTIONS = [
  { value: "100", labelKey: "radius100" as const },
  { value: "200", labelKey: "radius200" as const },
  { value: "500", labelKey: "radius500" as const },
  { value: "1000", labelKey: "radius1000" as const },
];

type Props = {
  filters: ListingFilters;
  extendedOpen: boolean;
  bundle: ReferenceBundle | null;
  models: VehicleModel[];
  generations: Generation[];
  onBrandChange: (v: string) => void;
  onModelChange: (v: string) => void;
  onGenerationChange: (v: string) => void;
  onFilterChange: <K extends keyof ListingFilters>(key: K, value: ListingFilters[K]) => void;
  onToggleExtended: () => void;
  onReset: () => void;
  onSubmit: () => void;
};

export default function ListingFiltersPanel({
  filters,
  extendedOpen,
  bundle,
  models,
  generations,
  onBrandChange,
  onModelChange,
  onGenerationChange,
  onFilterChange,
  onToggleExtended,
  onReset,
  onSubmit,
}: Props) {
  const locale = getLocale();

  const refOptions = (items: { id: number; slug?: string; name: { mn: string; ru: string; en: string } }[]) =>
    items.map((x) => ({
      value: String(x.id),
      label: pickName(x.name, locale),
      slug: x.slug,
    }));

  const transmissionDropdownGroups = (items: TransmissionRef[]) => {
    const options = refOptions(items);
    const automatic: typeof options = [];
    const manual: typeof options = [];
    for (const opt of options) {
      const item = items.find((x) => String(x.id) === opt.value);
      if (item?.group === "automatic") {
        automatic.push(opt);
      } else {
        manual.push(opt);
      }
    }
    const groups: { header?: string; options: typeof options }[] = [];
    if (automatic.length) {
      groups.push({ header: t("transmissionAutomaticGroup", locale), options: automatic });
    }
    if (manual.length) {
      groups.push({ options: manual });
    }
    return groups;
  };

  const regionLabel =
    filters.region && bundle
      ? pickName(bundle.regions.find((r) => String(r.id) === filters.region)!.name, locale)
      : t("allRegions", locale);

  const cityOptions = bundle
    ? refOptions(filters.region ? bundle.cities.filter((c) => String(c.region.id) === filters.region) : bundle.cities)
    : [];

  const colorOptions = bundle
    ? bundle.colors.map((c) => ({
        value: String(c.id),
        label: pickName(c.name, locale),
        slug: c.slug,
      }))
    : [];

  return (
    <section className="filters-panel">
      <div className="filters-location">
        <label className={`filters-chip filters-chip-region ${!filters.city ? "active" : ""}`}>
          <span className="filters-chip-text">{regionLabel}</span>
          <select
            className="filters-chip-select"
            value={filters.region}
            onChange={(e) => onFilterChange("region", e.target.value)}
            aria-label={t("allRegions", locale)}
          >
            <option value="">{t("allRegions", locale)}</option>
            {bundle ? refOptions(bundle.regions).map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            )) : null}
          </select>
        </label>

        {RADIUS_OPTIONS.map((opt) => (
          <button
            key={opt.value}
            type="button"
            className={`filters-chip ${filters.radius_km === opt.value ? "active" : ""}`}
            onClick={() => onFilterChange("radius_km", filters.radius_km === opt.value ? "" : opt.value)}
          >
            {t(opt.labelKey, locale)}
          </button>
        ))}

        <label className={`filters-chip filters-city-chip ${filters.city ? "active" : ""}`}>
          <span className="filters-chip-text">
            {filters.city && bundle
              ? pickName(bundle.cities.find((c) => String(c.id) === filters.city)!.name, locale)
              : t("otherCity", locale)}
          </span>
          <select
            className="filters-chip-select"
            value={filters.city}
            onChange={(e) => onFilterChange("city", e.target.value)}
            aria-label={t("otherCity", locale)}
          >
            <option value="">{t("otherCity", locale)}</option>
            {cityOptions.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="filters-condition-tabs" role="tablist">
        {(
          [
            ["", t("all", locale)],
            ["used", t("used", locale)],
            ["new", t("new", locale)],
          ] as const
        ).map(([val, label]) => (
          <button
            key={val || "all"}
            type="button"
            role="tab"
            className={filters.condition === val ? "active" : ""}
            onClick={() => onFilterChange("condition", val)}
          >
            {label}
          </button>
        ))}
      </div>

      <div className="filters-box">
        <div className="filters-row">
          <CompactSelect
            placeholder={t("brand", locale)}
            value={filters.brand}
            onChange={onBrandChange}
            options={bundle ? refOptions(bundle.brands) : []}
          />
          <CompactSelect
            placeholder={t("model", locale)}
            value={filters.model}
            onChange={onModelChange}
            disabled={!filters.brand}
            options={refOptions(models)}
          />
          <CompactSelect
            placeholder={t("generation", locale)}
            value={filters.generation}
            onChange={onGenerationChange}
            disabled={!filters.model}
            options={generationSelectOptions(generations, locale)}
          />
          <div className="filter-cell filter-cell-add" aria-hidden="true">
            <button type="button" className="filter-add-btn" tabIndex={-1} title="Добавить ряд выбора марки, модели">
              +
            </button>
          </div>
        </div>

        <div className="filters-row">
          <FilterPresetRange
            fromValue={filters.price_min}
            toValue={filters.price_max}
            onFromChange={(v) => onFilterChange("price_min", v)}
            onToChange={(v) => onFilterChange("price_max", v)}
            fromPlaceholder={t("priceFrom", locale)}
            toPlaceholder={t("to", locale)}
            presets={PRICE_PRESETS_MNT}
            formatPreset={formatPricePresetMnt}
            anyPresetLabel={t("anyPrice", locale)}
          />
          <FilterDropdownRange
            fromValue={filters.year_min}
            toValue={filters.year_max}
            onFromChange={(v) => onFilterChange("year_min", v)}
            onToChange={(v) => onFilterChange("year_max", v)}
            fromPlaceholder={t("yearFrom", locale)}
            toPlaceholder={t("to", locale)}
            anyLabel={t("anyYear", locale)}
            resetLabel={t("anyYear", locale)}
            options={yearFilterOptions()}
            panelClassName="filter-dropdown-panel-years"
          />
          <FilterDropdown
            placeholder={t("transmission", locale)}
            anyLabel={t("any", locale)}
            value={filters.transmission}
            onChange={(v) => onFilterChange("transmission", v)}
            groups={bundle ? transmissionDropdownGroups(bundle.transmissions) : []}
          />
          <FilterDropdown
            placeholder={t("fuel", locale)}
            anyLabel={t("any", locale)}
            value={filters.fuel}
            onChange={(v) => onFilterChange("fuel", v)}
            options={bundle ? refOptions(bundle.fuelTypes) : []}
          />
        </div>

        <div className="filters-row">
          <FilterPresetRange
            fromValue={filters.engine_volume_min}
            toValue={filters.engine_volume_max}
            onFromChange={(v) => onFilterChange("engine_volume_min", v)}
            onToChange={(v) => onFilterChange("engine_volume_max", v)}
            fromPlaceholder={t("engineFrom", locale)}
            toPlaceholder={t("to", locale)}
            presets={ENGINE_VOLUME_PRESETS}
            formatPreset={formatEngineVolumePreset}
            anyPresetLabel={t("anyVolume", locale)}
            inputMode="decimal"
          />
          <FilterDropdown
            placeholder={t("drive", locale)}
            anyLabel={t("any", locale)}
            value={filters.drive}
            onChange={(v) => onFilterChange("drive", v)}
            options={bundle ? refOptions(bundle.driveTypes) : []}
          />
          <div className="filter-cell filter-cell-span-2 filters-checks">
            <CheckboxField
              label={t("unsold", locale)}
              checked={filters.unsold}
              onChange={(v) => onFilterChange("unsold", v)}
            />
            <CheckboxField
              label={t("withPhotos", locale)}
              checked={filters.has_photos}
              onChange={(v) => onFilterChange("has_photos", v)}
            />
          </div>
        </div>

        {extendedOpen && (
          <div className="filters-extended">
            <div className="filters-row filters-row-body-color">
              <BodyTypePickerField
                placeholder={t("bodyTypeLabel", locale)}
                anyLabel={t("bodyAny", locale)}
                countLabel={(count) => t("bodyTypesCount", locale).replace("{n}", String(count))}
                value={filters.body_type}
                onChange={(v) => onFilterChange("body_type", v)}
                options={bundle ? refOptions(bundle.bodyTypes) : []}
              />
              <ColorPickerField
                label={t("colorLabel", locale)}
                value={filters.color}
                onChange={(v) => onFilterChange("color", v)}
                anyLabel={t("colorAny", locale)}
                options={colorOptions}
              />
            </div>

            <div className="filters-row">
              <SelectField
                label={t("documents", locale)}
                value={filters.pts_status}
                onChange={(v) => onFilterChange("pts_status", v)}
                placeholder={t("any", locale)}
                options={[
                  { value: "ok", label: t("ptsOk", locale) },
                  { value: "problem", label: t("ptsProblem", locale) },
                ]}
              />
              <SelectField
                label={t("damageLabel", locale)}
                value={filters.damage_status}
                onChange={(v) => onFilterChange("damage_status", v)}
                placeholder={t("any", locale)}
                options={[
                  { value: "ok", label: t("damageOk", locale) },
                  { value: "repair", label: t("damageRepair", locale) },
                ]}
              />
              <RadioSegment
                label={t("steeringLabel", locale)}
                value={filters.steering}
                onChange={(v) => onFilterChange("steering", v)}
                options={[
                  { value: "", label: t("steeringAny", locale) },
                  { value: "left", label: t("steeringLeft", locale) },
                  { value: "right", label: t("steeringRight", locale) },
                ]}
              />
            </div>

            <div className="filters-row">
              <RangeControl
                label={t("powerPts", locale)}
                fromValue={filters.power_min}
                toValue={filters.power_max}
                onFromChange={(v) => onFilterChange("power_min", v)}
                onToChange={(v) => onFilterChange("power_max", v)}
                fromPlaceholder={t("powerFrom", locale)}
                toPlaceholder={t("to", locale)}
                type="number"
              />
              <RangeControl
                label={t("mileage", locale)}
                fromValue={filters.mileage_min}
                toValue={filters.mileage_max}
                onFromChange={(v) => onFilterChange("mileage_min", v)}
                onToChange={(v) => onFilterChange("mileage_max", v)}
                fromPlaceholder={t("mileageFrom", locale)}
                toPlaceholder={t("to", locale)}
                type="number"
              />
              <div className="filter-cell filter-cell-span-2 filters-checks filters-checks-extended">
                <CheckboxField
                  label={t("noLocalMileage", locale)}
                  checked={filters.without_local_mileage}
                  onChange={(v) => onFilterChange("without_local_mileage", v)}
                />
              </div>
            </div>

            <div className="filters-row filters-row-2col">
              <SelectField
                label={t("brandCountry", locale)}
                value={filters.brand_country}
                onChange={(v) => onFilterChange("brand_country", v)}
                placeholder={t("any", locale)}
                options={bundle ? refOptions(bundle.countries) : []}
              />
              <RadioSegment
                label={t("seller", locale)}
                value={filters.seller_type}
                onChange={(v) => onFilterChange("seller_type", v)}
                options={[
                  { value: "", label: t("sellerAny", locale) },
                  { value: "owner", label: t("sellerOwner", locale) },
                  { value: "private", label: t("sellerPrivate", locale) },
                  { value: "company", label: t("sellerCompany", locale) },
                ]}
              />
            </div>

            <div className="filters-row filters-row-2col">
              <SelectField
                label={t("availabilityLabel", locale)}
                value={filters.availability}
                onChange={(v) => onFilterChange("availability", v)}
                placeholder={t("any", locale)}
                options={[
                  { value: "in_stock", label: t("availInStock", locale) },
                  { value: "in_transit", label: t("availInTransit", locale) },
                  { value: "on_order", label: t("availOnOrder", locale) },
                ]}
              />
              <RadioSegment
                label={t("ownersCount", locale)}
                value={filters.owners_count}
                onChange={(v) => onFilterChange("owners_count", v)}
                options={[
                  { value: "", label: t("ownersAny", locale) },
                  { value: "one", label: t("ownersOne", locale) },
                  { value: "up_to_two", label: t("ownersTwo", locale) },
                  { value: "up_to_three", label: t("ownersThree", locale) },
                ]}
              />
            </div>

            <div className="filters-checks filters-checks-extended">
              <CheckboxField
                label={t("exchange", locale)}
                checked={filters.exchange_possible}
                onChange={(v) => onFilterChange("exchange_possible", v)}
              />
              <CheckboxField
                label={t("certification", locale)}
                checked={filters.is_certified}
                onChange={(v) => onFilterChange("is_certified", v)}
              />
            </div>

            <InputField
              label={t("keywords", locale)}
              value={filters.q}
              onChange={(v) => onFilterChange("q", v)}
              placeholder={t("keywordsPlaceholder", locale)}
            />
          </div>
        )}

        <div className="filters-footer">
          <button type="button" className="filters-extended-toggle" onClick={onToggleExtended}>
            {extendedOpen ? t("normalSearch", locale) : t("extended", locale)}
            <span className="filters-extended-chevron" aria-hidden>
              {extendedOpen ? "▲" : "▼"}
            </span>
          </button>
          <button type="button" className="filters-reset-link" onClick={onReset}>
            {t("resetAll", locale)}
          </button>
          <button type="button" className="btn btn-show" onClick={onSubmit}>
            {t("showListings", locale)}
          </button>
        </div>
      </div>
    </section>
  );
}
