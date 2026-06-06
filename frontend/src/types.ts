export interface ImageItem {
  id: string;
  object_key: string;
  source: string;
  caption: string;
  created_at: string;
  preview_url: string;
}

export interface SearchResult {
  id: string;
  object_key: string;
  source: string;
  caption: string;
  score: number;
  preview_url: string;
}

export interface ImagesResponse {
  total: number;
  page: number;
  size: number;
  items: ImageItem[];
}

export interface SearchResponse {
  results: SearchResult[];
}

export interface ImagePairSide {
  id: string;
  object_key: string;
  bucket: string;
  preview_url: string;
}

export interface ImagePair {
  pair_id: string;
  t1: ImagePairSide;
  t2: ImagePairSide;
}

export interface PairsResponse {
  pairs: ImagePair[];
  total: number;
}

export interface PairSimilarityResponse {
  pair_id: string;
  similarity: number;
  t1_id: string;
  t2_id: string;
}
