import { useState, useEffect } from "react";
import { GitCompare, ArrowLeft, Loader2 } from "lucide-react";
import type { ImagePair, PairSimilarityResponse } from "../types";
import { fetchPairs, fetchPairSimilarity } from "../api";
import CompareSlider from "../components/CompareSlider";
import AnimatedNumber from "../components/AnimatedNumber";
import ErrorDisplay from "../components/ErrorDisplay";

export default function ComparePage() {
  const [pairs, setPairs] = useState<ImagePair[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPair, setSelectedPair] = useState<ImagePair | null>(null);
  const [similarity, setSimilarity] = useState<PairSimilarityResponse | null>(null);
  const [simLoading, setSimLoading] = useState(false);

  useEffect(() => {
    fetchPairs()
      .then((res) => {
        setPairs(res.pairs);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const openCompare = async (pair: ImagePair) => {
    setSelectedPair(pair);
    setSimilarity(null);
    setSimLoading(true);
    try {
      const res = await fetchPairSimilarity(pair.pair_id);
      setSimilarity(res);
    } catch {
      setSimilarity(null);
    } finally {
      setSimLoading(false);
    }
  };

  if (selectedPair) {
    return (
      <div className="space-y-4 animate-fade-in-up">
        <div className="flex items-center gap-3">
          <button
            onClick={() => setSelectedPair(null)}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors"
            style={{ background: "var(--bg-secondary)", color: "var(--text-secondary)" }}
          >
            <ArrowLeft className="w-4 h-4" />
            返回列表
          </button>
          <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
            {selectedPair.pair_id}
          </h2>
        </div>

        <div className="animate-scale-in">
          <CompareSlider
            beforeSrc={selectedPair.t1.preview_url}
            afterSrc={selectedPair.t2.preview_url}
          />
        </div>

        <div className="flex flex-wrap items-center gap-4 p-4 rounded-xl border" style={{ borderColor: "var(--border)", background: "var(--bg-secondary)" }}>
          <div className="flex items-center gap-2">
            <span className="text-sm" style={{ color: "var(--text-muted)" }}>语义相似度</span>
            {simLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" style={{ color: "var(--text-muted)" }} />
            ) : similarity ? (
              <span className="text-lg font-mono font-semibold" style={{ color: "var(--accent)" }}>
                <AnimatedNumber value={similarity.similarity * 100} decimals={2} suffix="%" />
              </span>
            ) : (
              <span className="text-sm" style={{ color: "var(--text-muted)" }}>--</span>
            )}
          </div>
          <div className="h-4 w-px" style={{ background: "var(--border)" }} />
          <div className="flex items-center gap-2">
            <span className="text-sm" style={{ color: "var(--text-muted)" }}>说明</span>
            <span className="text-sm" style={{ color: "var(--text-secondary)" }}>
              基于两期图像 caption 向量计算，值越高说明地表变化越小
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-5 animate-fade-in-up">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold" style={{ color: "var(--text-primary)" }}>
          图像配对对比
        </h2>
        <span className="text-sm" style={{ color: "var(--text-muted)" }}>
          共 {pairs.length} 对
        </span>
      </div>

      {loading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="rounded-xl border p-3 space-y-3" style={{ borderColor: "var(--border)" }}>
              <div className="flex gap-2">
                <div className="w-1/2 aspect-[4/3] rounded-lg shimmer" />
                <div className="w-1/2 aspect-[4/3] rounded-lg shimmer" />
              </div>
              <div className="h-3 w-3/4 rounded shimmer" />
            </div>
          ))}
        </div>
      )}

      {error && <ErrorDisplay error={error} />}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 stagger-grid">
        {pairs.map((pair) => (
          <button
            key={pair.pair_id}
            onClick={() => openCompare(pair)}
            className="group text-left rounded-xl border p-3 transition-all hover:border-cyan-500/30"
            style={{ borderColor: "var(--border)", background: "var(--bg-card)" }}
          >
            <div className="flex gap-2 mb-2">
              <div className="relative w-1/2 aspect-[4/3] rounded-lg overflow-hidden border" style={{ borderColor: "var(--border)" }}>
                <img
                  src={pair.t1.preview_url.startsWith("/") ? `http://localhost:8000${pair.t1.preview_url}` : pair.t1.preview_url}
                  alt="t1"
                  className="w-full h-full object-cover"
                />
                <span className="absolute top-1.5 left-1.5 px-1.5 py-0.5 text-[10px] font-mono font-semibold rounded" style={{ background: "var(--t1)", color: "#0f172a" }}>
                  T1
                </span>
              </div>
              <div className="relative w-1/2 aspect-[4/3] rounded-lg overflow-hidden border" style={{ borderColor: "var(--border)" }}>
                <img
                  src={pair.t2.preview_url.startsWith("/") ? `http://localhost:8000${pair.t2.preview_url}` : pair.t2.preview_url}
                  alt="t2"
                  className="w-full h-full object-cover"
                />
                <span className="absolute top-1.5 left-1.5 px-1.5 py-0.5 text-[10px] font-mono font-semibold rounded" style={{ background: "var(--t2)", color: "#0f172a" }}>
                  T2
                </span>
              </div>
            </div>
            <p className="text-xs font-mono truncate" style={{ color: "var(--text-muted)" }}>
              {pair.pair_id}
            </p>
            <div className="flex items-center gap-1 mt-1.5 text-xs" style={{ color: "var(--accent)" }}>
              <GitCompare className="w-3 h-3" />
              点击对比
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
