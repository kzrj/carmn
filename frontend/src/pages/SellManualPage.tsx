import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { createListing } from "../api/listings";
import { Field, SelectField } from "../components/ui/Fields";
import { getLocale, pickName } from "../lib/i18n";
import { t } from "../lib/labels";
import {
  buildListingPayload,
  formatApiError,
  specsFromGeneration,
  specsFromTrim,
  yearOptions,
} from "../lib/sellForm";
import { authStore } from "../store/authStore";
import { refsActions, refsStore } from "../store/refsStore";
import type { Generation, Trim } from "../types";

function refOptions(items: { id: number; name: { mn: string; ru: string; en: string } }[], locale: ReturnType<typeof getLocale>) {
  return items.map((item) => ({ value: String(item.id), label: pickName(item.name, locale) }));
}

export default function SellManualPage() {
  const locale = getLocale();
  const navigate = useNavigate();
  const user = authStore.useStore((s) => s.user);
  const { bundle, models, generations, trims } = refsStore.useStore((s) => s);

  const [brandId, setBrandId] = useState("");
  const [modelId, setModelId] = useState("");
  const [generationId, setGenerationId] = useState("");
  const [trimId, setTrimId] = useState("");
  const [year, setYear] = useState("");
  const [condition, setCondition] = useState<"new" | "used">("used");
  const [mileage, setMileage] = useState("");
  const [bodyType, setBodyType] = useState("");
  const [fuel, setFuel] = useState("");
  const [transmission, setTransmission] = useState("");
  const [drive, setDrive] = useState("");
  const [vin, setVin] = useState("");
  const [chassis, setChassis] = useState("");
  const [description, setDescription] = useState("");
  const [priceMode, setPriceMode] = useState<"mnt" | "usd">("mnt");
  const [price, setPrice] = useState("");
  const [regionId, setRegionId] = useState("");
  const [cityId, setCityId] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    refsActions.loadBundle();
  }, []);

  useEffect(() => {
    if (brandId) refsActions.loadModels(Number(brandId));
  }, [brandId]);

  useEffect(() => {
    if (modelId) refsActions.loadGenerations(Number(modelId));
  }, [modelId]);

  useEffect(() => {
    if (generationId) refsActions.loadTrims(Number(generationId));
  }, [generationId]);

  const selectedGeneration = useMemo(
    () => generations.find((g) => String(g.id) === generationId) ?? null,
    [generations, generationId],
  );

  const years = useMemo(() => yearOptions(selectedGeneration), [selectedGeneration]);

  const cities = useMemo(() => {
    if (!bundle) return [];
    if (!regionId) return bundle.cities;
    return bundle.cities.filter((c) => String(c.region.id) === regionId);
  }, [bundle, regionId]);

  const applySpecs = (gen: Generation | null, trim: Trim | null) => {
    const specs = trim ? specsFromTrim(trim, gen) : specsFromGeneration(gen);
    setBodyType(specs.bodyType);
    setFuel(specs.fuel);
    setTransmission(specs.transmission);
    setDrive(specs.drive);
  };

  const onBrandChange = (value: string) => {
    setBrandId(value);
    setModelId("");
    setGenerationId("");
    setTrimId("");
    setYear("");
    applySpecs(null, null);
  };

  const onModelChange = (value: string) => {
    setModelId(value);
    setGenerationId("");
    setTrimId("");
    setYear("");
    applySpecs(null, null);
  };

  const onGenerationChange = (value: string) => {
    setGenerationId(value);
    setTrimId("");
    setYear("");
    const gen = generations.find((g) => String(g.id) === value) ?? null;
    applySpecs(gen, null);
  };

  const onTrimChange = (value: string) => {
    setTrimId(value);
    const trim = trims.find((item) => String(item.id) === value) ?? null;
    applySpecs(selectedGeneration, trim);
  };

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    if (!user) {
      navigate(`/login?next=${encodeURIComponent("/sell/manual")}`);
      return;
    }

    setSubmitting(true);
    try {
      const listing = await createListing(
        buildListingPayload({
          brandId,
          modelId,
          generationId,
          trimId,
          year,
          condition,
          mileage,
          specs: { bodyType, fuel, transmission, drive },
          vin,
          chassis,
          description,
          priceMode,
          price,
          cityId,
        }),
      );
      navigate(`/sell/photos/${listing.id}`);
    } catch (err) {
      setError(formatApiError(err));
    } finally {
      setSubmitting(false);
    }
  };

  if (!bundle) {
    return <p className="muted page-pad">{t("loading", locale)}</p>;
  }

  return (
    <div className="sell-page page-pad">
      <div className="sell-page-head">
        <h1>{t("manualTitle", locale)}</h1>
        <Link to="/sell" className="btn btn-ghost">
          {t("back", locale)}
        </Link>
      </div>

      {!user && <p className="sell-note">{t("loginRequired", locale)}</p>}

      <form className="card sell-form" onSubmit={onSubmit}>
        <section className="sell-section">
          <SelectField
            label={t("brand", locale)}
            value={brandId}
            onChange={onBrandChange}
            options={refOptions(bundle.brands, locale)}
            placeholder={t("selectBrand", locale)}
          />
          <SelectField
            label={t("model", locale)}
            value={modelId}
            onChange={onModelChange}
            options={refOptions(models, locale)}
            disabled={!brandId}
            placeholder={t("selectModel", locale)}
          />
        </section>

        <section className="sell-section">
          <SelectField
            label={t("generation", locale)}
            value={generationId}
            onChange={onGenerationChange}
            options={refOptions(generations, locale)}
            disabled={!modelId}
            placeholder="—"
          />
          <SelectField
            label={t("trim", locale)}
            value={trimId}
            onChange={onTrimChange}
            options={refOptions(trims, locale)}
            disabled={!generationId}
            placeholder="—"
          />
        </section>

        <section className="sell-section">
          <SelectField
            label={t("year", locale)}
            value={year}
            onChange={setYear}
            options={years.map((y) => ({ value: String(y), label: String(y) }))}
            placeholder={t("selectYear", locale)}
          />
          <SelectField
            label={t("condition", locale)}
            value={condition}
            onChange={(v) => setCondition(v as "new" | "used")}
            options={[
              { value: "used", label: t("used", locale) },
              { value: "new", label: t("new", locale) },
            ]}
          />
          <Field label={t("mileage", locale)}>
            <input
              type="number"
              min={0}
              value={mileage}
              onChange={(e) => setMileage(e.target.value)}
              placeholder="km"
            />
          </Field>
        </section>

        <section className="sell-section">
          <SelectField
            label={t("bodyType", locale)}
            value={bodyType}
            onChange={setBodyType}
            options={refOptions(bundle.bodyTypes, locale)}
          />
          <SelectField
            label={t("fuel", locale)}
            value={fuel}
            onChange={setFuel}
            options={refOptions(bundle.fuelTypes, locale)}
          />
          <SelectField
            label={t("transmission", locale)}
            value={transmission}
            onChange={setTransmission}
            options={refOptions(bundle.transmissions, locale)}
          />
          <SelectField
            label={t("drive", locale)}
            value={drive}
            onChange={setDrive}
            options={refOptions(bundle.driveTypes, locale)}
          />
        </section>

        <section className="sell-section">
          <Field label={t("vin", locale)}>
            <input
              value={vin}
              onChange={(e) => setVin(e.target.value.toUpperCase())}
              maxLength={17}
              placeholder={t("vinPlaceholder", locale)}
            />
          </Field>
          <Field label={t("chassis", locale)}>
            <input value={chassis} onChange={(e) => setChassis(e.target.value)} />
          </Field>
          <Field label={t("description", locale)}>
            <textarea
              rows={4}
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </Field>
        </section>

        <section className="sell-section">
          <div className="price-mode">
            <button
              type="button"
              className={priceMode === "mnt" ? "active" : ""}
              onClick={() => setPriceMode("mnt")}
            >
              ₮
            </button>
            <button
              type="button"
              className={priceMode === "usd" ? "active" : ""}
              onClick={() => setPriceMode("usd")}
            >
              $
            </button>
          </div>
          <Field label={priceMode === "mnt" ? t("priceMnt", locale) : t("priceUsd", locale)}>
            <input
              type="number"
              min={0}
              required
              value={price}
              onChange={(e) => setPrice(e.target.value)}
            />
          </Field>
          <SelectField
            label={t("region", locale)}
            value={regionId}
            onChange={(id) => {
              setRegionId(id);
              setCityId("");
            }}
            options={refOptions(bundle.regions, locale)}
            placeholder={t("allRegions", locale)}
          />
          <SelectField
            label={t("city", locale)}
            value={cityId}
            onChange={setCityId}
            options={cities.map((c) => ({ value: String(c.id), label: pickName(c.name, locale) }))}
            placeholder={t("selectCity", locale)}
          />
        </section>

        {error && <p className="error">{error}</p>}

        <button
          type="submit"
          className="btn btn-primary sell-submit"
          disabled={submitting || !brandId || !modelId || !year || !cityId || !price}
        >
          {submitting ? t("loading", locale) : t("submit", locale)}
        </button>
      </form>
    </div>
  );
}
