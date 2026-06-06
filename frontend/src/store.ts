import { create } from "zustand";
import type { ImageItem, SearchResult } from "./types";
import { fetchImages, searchSimilar, uploadImage } from "./api";

interface AppState {
  images: ImageItem[];
  totalImages: number;
  imagesLoading: boolean;
  imagesError: Error | null;
  filters: {
    source: "t1" | "t2" | null;
    query: string;
    page: number;
    size: number;
  };

  searchResults: SearchResult[];
  searchLoading: boolean;
  searchError: Error | null;
  searchParams: {
    query: string;
    threshold: number;
    source: "t1" | "t2" | null;
    referenceImage: File | null;
    referenceImagePath: string | null;
  };

  setFilter: (key: string, value: any) => void;
  setSearchParam: (key: string, value: any) => void;
  fetchImages: () => Promise<void>;
  searchSimilar: () => Promise<void>;
  uploadReferenceImage: (file: File) => Promise<void>;
}

export const useStore = create<AppState>((set, get) => ({
  images: [],
  totalImages: 0,
  imagesLoading: false,
  imagesError: null,
  filters: {
    source: null,
    query: "",
    page: 1,
    size: 12,
  },

  searchResults: [],
  searchLoading: false,
  searchError: null,
  searchParams: {
    query: "",
    threshold: 0.7,
    source: null,
    referenceImage: null,
    referenceImagePath: null,
  },

  setFilter: (key, value) => {
    set((state) => ({
      filters: { ...state.filters, [key]: value },
    }));
    if (key !== "page") {
      set((state) => ({
        filters: { ...state.filters, [key]: value, page: 1 },
      }));
    }
  },

  setSearchParam: (key, value) => {
    set((state) => ({
      searchParams: { ...state.searchParams, [key]: value },
    }));
  },

  fetchImages: async () => {
    set({ imagesLoading: true, imagesError: null });
    try {
      const { filters } = get();
      const data = await fetchImages(
        filters.page,
        filters.size,
        filters.source,
        filters.query
      );
      set({ images: data.items, totalImages: data.total });
    } catch (err: any) {
      set({ imagesError: err instanceof Error ? err : new Error(err?.message || "加载失败") });
    } finally {
      set({ imagesLoading: false });
    }
  },

  searchSimilar: async () => {
    set({ searchLoading: true, searchError: null });
    try {
      const { searchParams } = get();
      const data = await searchSimilar(
        searchParams.query,
        searchParams.threshold,
        searchParams.source,
        20,
        searchParams.referenceImagePath || undefined
      );
      set({ searchResults: data.results });
    } catch (err: any) {
      set({ searchError: err instanceof Error ? err : new Error(err?.message || "检索失败") });
    } finally {
      set({ searchLoading: false });
    }
  },

  uploadReferenceImage: async (file) => {
    const res = await uploadImage(file);
    set((state) => ({
      searchParams: {
        ...state.searchParams,
        referenceImage: file,
        referenceImagePath: res.path,
      },
    }));
  },
}));
