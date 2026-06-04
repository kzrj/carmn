import * as refsApi from "../api/references";
import type { Generation, ReferenceBundle, Trim, VehicleModel } from "../types";
import { createStore } from "./createStore";

type RefsState = {
  bundle: ReferenceBundle | null;
  models: VehicleModel[];
  generations: Generation[];
  trims: Trim[];
  loading: boolean;
  error: string | null;
};

export const refsStore = createStore<RefsState>({
  bundle: null,
  models: [],
  generations: [],
  trims: [],
  loading: false,
  error: null,
});

export const refsActions = {
  async loadBundle() {
    if (refsStore.getState().bundle) return;
    refsStore.setState({ loading: true, error: null });
    try {
      const bundle = await refsApi.fetchReferenceBundle();
      refsStore.setState({ bundle, loading: false });
    } catch (e) {
      refsStore.setState({
        loading: false,
        error: e instanceof Error ? e.message : "Failed to load references",
      });
    }
  },

  async loadModels(brandId: number) {
    if (!brandId) {
      refsStore.setState({ models: [], generations: [], trims: [] });
      return;
    }
    const models = await refsApi.fetchModels(brandId);
    refsStore.setState({ models, generations: [], trims: [] });
  },

  async loadGenerations(modelId: number) {
    if (!modelId) {
      refsStore.setState({ generations: [], trims: [] });
      return;
    }
    const generations = await refsApi.fetchGenerations(modelId);
    refsStore.setState({ generations, trims: [] });
  },

  async loadTrims(generationId: number) {
    if (!generationId) {
      refsStore.setState({ trims: [] });
      return;
    }
    const trims = await refsApi.fetchTrims(generationId);
    refsStore.setState({ trims });
  },
};
