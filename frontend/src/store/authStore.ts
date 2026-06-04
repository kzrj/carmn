import * as authApi from "../api/auth";
import { clearTokens, getAccessToken } from "../api/client";
import type { UserMe } from "../types";
import { createStore } from "./createStore";

type AuthState = {
  user: UserMe | null;
  loading: boolean;
  error: string | null;
  initialized: boolean;
};

export const authStore = createStore<AuthState>({
  user: null,
  loading: false,
  error: null,
  initialized: false,
});

export const authActions = {
  async init() {
    if (!getAccessToken()) {
      authStore.setState({ initialized: true });
      return;
    }
    authStore.setState({ loading: true, error: null });
    try {
      const user = await authApi.fetchMe();
      authStore.setState({ user, loading: false, initialized: true });
    } catch {
      clearTokens();
      authStore.setState({ user: null, loading: false, initialized: true });
    }
  },

  async login(phone: string, password: string) {
    authStore.setState({ loading: true, error: null });
    try {
      await authApi.loginUser(phone, password);
      const user = await authApi.fetchMe();
      authStore.setState({ user, loading: false });
    } catch (e) {
      authStore.setState({
        loading: false,
        error: e instanceof Error ? e.message : "Login failed",
      });
      throw e;
    }
  },

  async register(data: {
    phone: string;
    password: string;
    seller_type: string;
    display_name?: string;
  }) {
    authStore.setState({ loading: true, error: null });
    try {
      await authApi.registerUser(data);
      await authApi.loginUser(data.phone, data.password);
      const user = await authApi.fetchMe();
      authStore.setState({ user, loading: false });
    } catch (e) {
      authStore.setState({
        loading: false,
        error: e instanceof Error ? e.message : "Registration failed",
      });
      throw e;
    }
  },

  logout() {
    clearTokens();
    authStore.setState({ user: null, error: null });
  },
};
