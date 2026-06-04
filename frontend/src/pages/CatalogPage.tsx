import { useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import Breadcrumbs from "../components/layout/Breadcrumbs";
import ListingFiltersPanel from "../components/listings/ListingFiltersPanel";
import ListingCard from "../components/listings/ListingCard";
import ModelGroupsList, { modelGroupsEmptyLabel } from "../components/listings/ModelGroupsList";
import PopularBrandsPanel from "../components/listings/PopularBrandsPanel";
import Pagination from "../components/ui/Pagination";
import { buildCatalogBreadcrumbs } from "../lib/breadcrumbs";
import { getLocale } from "../lib/i18n";
import { canUseModelGroupsView, hasActiveFilters } from "../lib/listingFilters";
import { t } from "../lib/labels";
import { formatCount } from "../lib/formatCount";
import { getPageRange, LISTINGS_PAGE_SIZE } from "../lib/pagination";
import { catalogActions, catalogStore } from "../store/catalogStore";
import { refsStore } from "../store/refsStore";
import type { ListingFilters } from "../types";

export default function CatalogPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const locale = getLocale();

  const { filters, items, modelGroups, total, listingsTotal, modelGroupsTotal, loading, error, extendedOpen } =
    catalogStore.useStore((s) => s);
  const { bundle, models, generations } = refsStore.useStore((s) => s);
  const resultsRef = useRef<HTMLElement>(null);

  useEffect(() => {
    catalogActions.initFromLocation(location.pathname, location.search);
  }, [location.pathname, location.search]);

  const page = Number(filters.page) || 1;
  const totalPages = Math.max(1, Math.ceil(total / LISTINGS_PAGE_SIZE));
  const { from, to } = getPageRange(page, total, LISTINGS_PAGE_SIZE);
  const showPopularBrands = !hasActiveFilters(filters);
  const breadcrumbs = buildCatalogBreadcrumbs(filters, bundle?.brands ?? [], models, generations, locale);
  const showModelLineup = canUseModelGroupsView(filters);
  const isModelLineupView = showModelLineup && filters.view === "models";

  const handlePageChange = (nextPage: number) => {
    void catalogActions.setPage(nextPage, navigate).then(() => {
      resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
    });
  };

  return (
    <div className="catalog-page">
      {breadcrumbs.length > 0 && <Breadcrumbs items={breadcrumbs} />}
      {showPopularBrands && bundle?.brands && bundle.brands.length > 0 && (
        <PopularBrandsPanel brands={bundle.brands} />
      )}

      <ListingFiltersPanel
        filters={filters}
        extendedOpen={extendedOpen}
        bundle={bundle}
        models={models}
        generations={generations}
        onBrandChange={catalogActions.onBrandChange}
        onModelChange={catalogActions.onModelChange}
        onGenerationChange={catalogActions.onGenerationChange}
        onFilterChange={catalogActions.setFilter}
        onToggleExtended={catalogActions.toggleExtended}
        onReset={async () => {
          catalogActions.resetFilters();
          navigate({ pathname: "/", search: "" });
          await catalogActions.loadResults();
        }}
        onSubmit={() => catalogActions.applyFilters(navigate)}
      />

      <section className="catalog-results" ref={resultsRef}>
        <div className="catalog-results-header">
          {showModelLineup ? (
            <nav className="catalog-view-tabs" role="tablist" aria-label={t("viewModelLineup", locale)}>
              <button
                type="button"
                role="tab"
                aria-selected={!isModelLineupView}
                className={!isModelLineupView ? "is-active" : undefined}
                onClick={() => catalogActions.setCatalogView("listings", navigate)}
              >
                {loading && !listingsTotal
                  ? t("loading", locale)
                  : `${formatCount(listingsTotal, locale)} ${t("tabListings", locale)}`}
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={isModelLineupView}
                className={isModelLineupView ? "is-active" : undefined}
                onClick={() => catalogActions.setCatalogView("models", navigate)}
              >
                {loading && !modelGroupsTotal
                  ? t("loading", locale)
                  : `${formatCount(modelGroupsTotal, locale)} ${t("tabModels", locale)}`}
              </button>
            </nav>
          ) : (
            <p className="catalog-summary muted">
              {loading
                ? t("loading", locale)
                : total > 0
                  ? `${t("shownOf", locale)} ${from}–${to} ${t("ofTotal", locale)} ${total}`
                  : `0 ${t("found", locale)}`}
            </p>
          )}
          <div className="catalog-results-actions">
            <label className="catalog-sort">
              <span className="sr-only">{t("sort", locale)}</span>
              <select
                value={isModelLineupView ? filters.groups_ordering : filters.ordering}
                onChange={(e) => {
                  if (isModelLineupView) {
                    catalogActions.setFilter("groups_ordering", e.target.value as ListingFilters["groups_ordering"]);
                  } else {
                    catalogActions.setFilter("ordering", e.target.value);
                  }
                  catalogActions.applyFilters(navigate);
                }}
              >
                {isModelLineupView ? (
                  <>
                    <option value="-count">{t("groupsSortCount", locale)} ↓</option>
                    <option value="count">{t("groupsSortCount", locale)} ↑</option>
                    <option value="name">{t("groupsSortName", locale)}</option>
                  </>
                ) : (
                  <>
                    <option value="-published_at">Newest</option>
                    <option value="price">Price ↑</option>
                    <option value="-price">Price ↓</option>
                    <option value="-year">Year ↓</option>
                    <option value="mileage">Mileage ↑</option>
                  </>
                )}
              </select>
            </label>
          </div>
        </div>
        {showModelLineup && !isModelLineupView && total > 0 && (
          <p className="catalog-summary muted catalog-summary-sub">
            {t("shownOf", locale)} {from}–{to} {t("ofTotal", locale)} {total}
          </p>
        )}

        {error && <p className="error">{error}</p>}

        {isModelLineupView ? (
          <>
            {!loading && modelGroups.length === 0 && !error && (
              <p className="muted">{modelGroupsEmptyLabel(locale)}</p>
            )}
            <ModelGroupsList groups={modelGroups} filters={filters} />
          </>
        ) : (
          <>
            {!loading && items.length === 0 && !error && (
              <p className="muted">{t("noResults", locale)}</p>
            )}
            <div className="listing-grid">
              {items.map((item) => (
                <ListingCard key={item.id} item={item} />
              ))}
            </div>
          </>
        )}

        <Pagination
          page={page}
          totalPages={totalPages}
          loading={loading}
          onPageChange={handlePageChange}
        />
      </section>
    </div>
  );
}
