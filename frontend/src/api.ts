import type { ImagesResponse, SearchResponse, PairsResponse, PairSimilarityResponse } from "./types";

const API_BASE = "/api/v1";
const REQUEST_TIMEOUT_MS = 10000;

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public kind: "timeout" | "network" | "server" | "client" = "server"
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchJson<T>(url: string, options?: RequestInit): Promise<T> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

  try {
    const res = await fetch(url, { ...options, signal: controller.signal });
    clearTimeout(timeoutId);

    if (!res.ok) {
      const text = await res.text().catch(() => "Unknown error");
      const kind = res.status >= 500 ? "server" : "client";
      throw new ApiError(`HTTP ${res.status}: ${text}`, res.status, kind);
    }
    return res.json() as Promise<T>;
  } catch (err) {
    clearTimeout(timeoutId);
    if (err instanceof ApiError) throw err;

    if (err instanceof DOMException && err.name === "AbortError") {
      throw new ApiError("请求超时，请检查网络或稍后重试", undefined, "timeout");
    }
    if (err instanceof TypeError) {
      throw new ApiError("网络连接失败，请检查后端服务是否启动", undefined, "network");
    }
    throw new ApiError(String(err), undefined, "server");
  }
}

export async function fetchImages(
  page: number,
  size: number,
  source: string | null,
  q: string
): Promise<ImagesResponse> {
  const params = new URLSearchParams();
  params.set("page", String(page));
  params.set("size", String(size));
  if (source) params.set("source", source);
  if (q) params.set("q", q);
  return fetchJson<ImagesResponse>(`${API_BASE}/images?${params.toString()}`);
}

export async function searchSimilar(
  query: string,
  threshold: number,
  source: string | null,
  limit: number,
  imagePath?: string
): Promise<SearchResponse> {
  const body: Record<string, unknown> = {
    threshold,
    limit,
  };
  if (query) body.query = query;
  if (source) body.source = source;
  if (imagePath) body.image_path = imagePath;

  return fetchJson<SearchResponse>(`${API_BASE}/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function uploadImage(file: File): Promise<{ path: string }> {
  const form = new FormData();
  form.append("file", file);
  return fetchJson<{ path: string }>(`${API_BASE}/upload`, {
    method: "POST",
    body: form,
  });
}

export async function fetchPairs(): Promise<PairsResponse> {
  return fetchJson<PairsResponse>(`${API_BASE}/pairs`);
}

export async function fetchPairSimilarity(pairId: string): Promise<PairSimilarityResponse> {
  return fetchJson<PairSimilarityResponse>(`${API_BASE}/pairs/${encodeURIComponent(pairId)}/similarity`);
}
