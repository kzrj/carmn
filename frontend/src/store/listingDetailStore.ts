import * as listingsApi from "../api/listings";
import type { ListingDetail } from "../types";
import { createStore } from "./createStore";

type DetailState = {
  item: ListingDetail | null;
  loading: boolean;
  error: string | null;
};

export const listingDetailStore = createStore<DetailState>({
  item: null,
  loading: false,
  error: null,
});

export const listingDetailActions = {
  async load(id: number) {
    listingDetailStore.setState({ loading: true, error: null, item: null });
    try {
      const item = await listingsApi.fetchListing(id);
      listingDetailStore.setState({ item, loading: false });
    } catch (e) {
      listingDetailStore.setState({
        loading: false,
        error: e instanceof Error ? e.message : "Failed to load listing",
      });
    }
  },

  clear() {
    listingDetailStore.setState({ item: null, error: null, loading: false });
  },
};
