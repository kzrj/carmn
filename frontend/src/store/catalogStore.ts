import * as listingsApi from "../api/listings";
import {
  findGenerationByPathSlug,
  findModelByPathSlug,
  parseCatalogPath,
} from "../lib/catalogRoutes";
import {
  defaultListingFilters,
  filtersEqual,
  filtersToRoute,
  searchParamsToFilters,
} from "../lib/listingFilters";
import type { ListingFilters, ListingListItem, ListingModelGroup } from "../types";
import { canUseModelGroupsView } from "../lib/listingFilters";
import { createStore } from "./createStore";
import { refsActions, refsStore } from "./refsStore";

type CatalogState = {
  filters: ListingFilters;
  items: ListingListItem[];
  modelGroups: ListingModelGroup[];
  total: number;
  listingsTotal: number;
  modelGroupsTotal: number;
  loading: boolean;
  error: string | null;
  extendedOpen: boolean;
};

export const catalogStore = createStore<CatalogState>({
  filters: defaultListingFilters(),
  items: [],
  modelGroups: [],
  total: 0,
  listingsTotal: 0,
  modelGroupsTotal: 0,
  loading: false,
  error: null,
  extendedOpen: false,
});

export const catalogActions = {
  async initFromLocation(pathname: string, search: string) {
    await refsActions.loadBundle();
    const brands = refsStore.getState().bundle?.brands ?? [];
    const params = new URLSearchParams(search.startsWith("?") ? search.slice(1) : search);
    const filters = searchParamsToFilters(params);
    const path = parseCatalogPath(pathname);

    if (path.brandSlug) {
      const brand = brands.find((item) => item.slug === path.brandSlug);
      if (brand) filters.brand = String(brand.id);
    }

    if (filters.brand) {
      await refsActions.loadModels(Number(filters.brand));
    }

    if (path.brandSlug && path.modelSlug) {
      const model = findModelByPathSlug(refsStore.getState().models, path.brandSlug, path.modelSlug);
      if (model) filters.model = String(model.id);
    }

    if (filters.model) {
      await refsActions.loadGenerations(Number(filters.model));
    }

    if (path.brandSlug && path.modelSlug && path.generationSlug) {
      const generation = findGenerationByPathSlug(
        refsStore.getState().generations,
        path.brandSlug,
        path.modelSlug,
        path.generationSlug,
      );
      if (generation) filters.generation = String(generation.id);
    }

    if (filters.generation) {
      await refsActions.loadTrims(Number(filters.generation));
    }

    const prevFilters = catalogStore.getState().filters;
    catalogStore.setState({ filters });
    const filtersUnchanged = filtersEqual(prevFilters, filters);
    const hasCachedResults =
      filters.view === "models"
        ? catalogStore.getState().modelGroups.length > 0
        : catalogStore.getState().items.length > 0;
    if (filtersUnchanged && hasCachedResults) {
      return;
    }
    await catalogActions.loadResults();
  },

  async initFromSearch(search: string) {
    await catalogActions.initFromLocation("/", search);
  },

  setFilter<K extends keyof ListingFilters>(key: K, value: ListingFilters[K]) {
    catalogStore.setState((s) => ({
      filters: {
        ...s.filters,
        [key]: value,
        ...(key !== "page" ? { page: "1" } : {}),
      },
    }));
  },

  setFilters(patch: Partial<ListingFilters>) {
    catalogStore.setState((s) => ({
      filters: { ...s.filters, ...patch, page: patch.page ?? "1" },
    }));
  },

  resetFilters() {
    catalogStore.setState({ filters: defaultListingFilters() });
    refsStore.setState({ models: [], generations: [], trims: [] });
  },

  toggleExtended() {
    catalogStore.setState((s) => ({ extendedOpen: !s.extendedOpen }));
  },

  async onBrandChange(brandId: string) {
    const patch: Partial<ListingFilters> = { brand: brandId, model: "", generation: "", trim: "" };
    if (!brandId) patch.view = "listings";
    catalogActions.setFilters(patch);
    if (brandId) await refsActions.loadModels(Number(brandId));
    else refsStore.setState({ models: [], generations: [], trims: [] });
  },

  async onModelChange(modelId: string) {
    catalogActions.setFilters({ model: modelId, generation: "", trim: "" });
    if (modelId) await refsActions.loadGenerations(Number(modelId));
    else refsStore.setState({ generations: [], trims: [] });
  },

  async onGenerationChange(generationId: string) {
    catalogActions.setFilters({ generation: generationId, trim: "" });
    if (generationId) await refsActions.loadTrims(Number(generationId));
    else refsStore.setState({ trims: [] });
  },

  async loadListings() {
    const { filters } = catalogStore.getState();
    catalogStore.setState({ loading: true, error: null });
    try {
      const data = await listingsApi.fetchListings(filters);
      catalogStore.setState({
        items: data.results,
        modelGroups: [],
        total: data.count,
        listingsTotal: data.count,
        modelGroupsTotal: data.model_groups_count ?? catalogStore.getState().modelGroupsTotal,
        loading: false,
      });
    } catch (e) {
      catalogStore.setState({
        loading: false,
        error: e instanceof Error ? e.message : "Failed to load listings",
      });
    }
  },

  async loadModelGroups() {
    const { filters } = catalogStore.getState();
    catalogStore.setState({ loading: true, error: null });
    try {
      const data = await listingsApi.fetchModelGroups(filters);
      catalogStore.setState({
        modelGroups: data.results,
        items: [],
        total: data.count,
        listingsTotal: data.listings_count,
        modelGroupsTotal: data.count,
        loading: false,
      });
    } catch (e) {
      catalogStore.setState({
        loading: false,
        error: e instanceof Error ? e.message : "Failed to load model groups",
      });
    }
  },

  async loadResults() {
    const { filters } = catalogStore.getState();
    if (filters.view === "models" && canUseModelGroupsView(filters)) {
      await catalogActions.loadModelGroups();
    } else {
      if (filters.view === "models") {
        catalogActions.setFilter("view", "listings");
      }
      await catalogActions.loadListings();
    }
  },

  async setCatalogView(view: ListingFilters["view"], navigate?: (to: { pathname: string; search?: string }) => void) {
    catalogActions.setFilter("view", view);
    catalogActions.setFilter("page", "1");
    await catalogActions.applyFilters(navigate);
  },

  async applyFilters(navigate?: (to: { pathname: string; search?: string }) => void) {
    await catalogActions.loadResults();
    const { bundle, models, generations } = refsStore.getState();
    const brands = bundle?.brands ?? [];
    const route = filtersToRoute(catalogStore.getState().filters, brands, models, generations);
    navigate?.({ pathname: route.pathname, search: route.search });
  },

  async setPage(page: number, navigate?: (to: { pathname: string; search?: string }) => void) {
    catalogActions.setFilter("page", String(page));
    await catalogActions.applyFilters(navigate);
  },
};
