import { useSyncExternalStore } from "react";

type Listener = () => void;

export function createStore<T extends object>(initial: T) {
  let state = initial;
  const listeners = new Set<Listener>();

  const getState = () => state;

  const setState = (patch: Partial<T> | ((s: T) => Partial<T>)) => {
    const next = typeof patch === "function" ? patch(state) : patch;
    state = { ...state, ...next };
    listeners.forEach((l) => l());
  };

  const subscribe = (listener: Listener) => {
    listeners.add(listener);
    return () => listeners.delete(listener);
  };

  const useStore = <R>(selector: (s: T) => R): R =>
    useSyncExternalStore(subscribe, () => selector(getState()), () => selector(getState()));

  return { getState, setState, subscribe, useStore };
}
