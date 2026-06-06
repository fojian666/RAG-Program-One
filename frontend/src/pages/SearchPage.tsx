import { useState } from "react";
import { useStore } from "../store";
import {
  Search,
  Upload,
  SlidersHorizontal,
  Zap,
  ImageOff,
  AlertCircle,
} from "lucide-react";
import Lightbox from "../components/Lightbox";
import ErrorDisplay from "../components/ErrorDisplay";
import TiltCard from "../components/TiltCard";

export default function SearchPage() {
  const { searchResults, searchLoading, searchError, searchSimilar, setSearchParam } = useStore();
  const [query, setQuery] = useState("");
  const [threshold, setThreshold] = useState(0.5);
  const [source, setSource] = useState<string>("all");
  const [mode, setMode] = useState<"text" | "image">("text");
  const [dragOver, setDragOver] = useState(false);
  const [lightbox, setLightbox] = useState<{ src: string; caption: string } | null>(null);

  const [localError, setLocalError] = useState<string | null>(null);

  const handleSearch = () => {
    setLocalError(null);
    if (mode === "text" && !query.trim()) {
      setLocalError("请输入查询文本后再进行检索");
      return;
    }
    setSearchParam("query", query);
    setSearchParam("threshold", threshold);
    setSearchParam("source", source === "all" ? null : source);
    setSearchParam("referenceImagePath", undefined);
    searchSimilar();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) {
      setSearchParam("query", "");
      setSearchParam("threshold", threshold);
      setSearchParam("source", source === "all" ? null : source);
      setSearchParam("referenceImagePath", URL.createObjectURL(file));
      searchSimilar();
    }
  };

  const scoreColor = (s: number) => {
    if (s >= 0.85) return "#34d399";
    if (s >= 0.7) return "var(--accent)";
    if (s >= 0.5) return "#fbbf24";
    return "#f87171";
  };

  return (
    <div className="space-y-6 animate-fade-in-up max-w-7xl mx-auto">
      {/* Query Panel */}
      <div className="rounded-2xl border p-6 space-y-5" style={{ background: "rgba(15,23,42,0.6)", borderColor: "var(--border)" }}>
        {/* Mode Switch */}
        <div className="flex items-center gap-1 p-1 rounded-xl w-fit" style={{ background: "var(--bg-secondary)" }}>
          {[
            { key: "text", icon: Search, label: "文本查询" },
            { key: "image", icon: Upload, label: "参考图片" },
          ].map((m) => (
            <button
              key={m.key}
              onClick={() => setMode(m.key as any)}
              className="flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-medium transition-all"
              style={{
                background: mode === m.key ? "rgba(56,189,248,0.12)" : "transparent",
                color: mode === m.key ? "var(--accent)" : "var(--text-muted)",
              }}
            >
              <m.icon className="w-3.5 h-3.5" />
              {m.label}
            </button>
          ))}
        </div>

        {mode === "text" ? (
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4" style={{ color: "var(--text-muted)" }} />
            <input
              type="text"
              placeholder="输入查询文本，例如：一片农田，周围有道路和村庄"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              className="w-full pl-11 pr-4 py-3.5 text-sm rounded-xl border input-glow"
              style={{
                background: "var(--bg-secondary)",
                borderColor: "var(--border)",
                color: "var(--text-primary)",
              }}
            />
          </div>
        ) : (
          <div
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className="flex flex-col items-center justify-center gap-3 py-12 rounded-xl border-2 border-dashed transition-all cursor-pointer"
            style={{
              borderColor: dragOver ? "var(--accent)" : "var(--border)",
              background: dragOver ? "rgba(56,189,248,0.04)" : "var(--bg-secondary)",
            }}
          >
            <Upload className="w-8 h-8" style={{ color: "var(--text-muted)" }} />
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>拖拽图片到此处，或点击上传</p>
            <input type="file" accept="image/*" className="hidden" onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                setSearchParam("query", "");
                setSearchParam("threshold", threshold);
                setSearchParam("source", source === "all" ? null : source);
                setSearchParam("referenceImagePath", URL.createObjectURL(file));
                searchSimilar();
              }
            }} />
          </div>
        )}

        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-5 md:items-end pt-2">
          <div className="flex-1 space-y-2">
            <div className="flex items-center justify-between">
              <label className="text-xs font-medium flex items-center gap-1.5" style={{ color: "var(--text-secondary)" }}>
                <SlidersHorizontal className="w-3 h-3" />
                相似度阈值
              </label>
              <span className="font-mono text-xs font-semibold px-2 py-0.5 rounded-md" style={{ background: "var(--bg-secondary)", color: "var(--accent)" }}>
                {threshold.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-[10px]" style={{ color: "var(--text-muted)" }}>
              <span>0</span>
              <span>0.5</span>
              <span>1.0</span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {["all", "t1", "t2"].map((s) => (
              <button
                key={s}
                onClick={() => setSource(s)}
                className="px-4 py-2.5 rounded-xl text-xs font-medium border transition-all"
                style={{
                  borderColor: source === s
                    ? (s === "t1" ? "var(--t1)" : s === "t2" ? "var(--t2)" : "var(--accent)")
                    : "var(--border)",
                  background: source === s
                    ? (s === "t1" ? "rgba(245,158,11,0.08)" : s === "t2" ? "rgba(52,211,153,0.08)" : "rgba(56,189,248,0.08)")
                    : "transparent",
                  color: source === s
                    ? (s === "t1" ? "var(--t1)" : s === "t2" ? "var(--t2)" : "var(--accent)")
                    : "var(--text-muted)",
                }}
              >
                {s === "all" ? "全部来源" : s.toUpperCase()}
              </button>
            ))}
          </div>

          <button
            onClick={handleSearch}
            disabled={searchLoading}
            className="btn-primary flex items-center gap-2 px-6 py-2.5 rounded-xl text-sm font-medium"
            style={{
              background: "var(--accent)",
              color: "#0f172a",
              boxShadow: "0 0 24px -6px rgba(56,189,248,0.4)",
              opacity: searchLoading ? 0.6 : 1,
              cursor: searchLoading ? "not-allowed" : "pointer",
            }}
          >
            <Zap className="w-4 h-4" />
            {searchLoading ? "检索中..." : "开始检索"}
          </button>
        </div>
      </div>

      {/* Results */}
      {localError && <ErrorDisplay error={localError} />}
      {searchError && <ErrorDisplay error={searchError} />}

      {searchResults.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
              检索结果
            </h3>
            <span className="text-xs font-mono px-2 py-1 rounded-md" style={{ background: "var(--bg-secondary)", color: "var(--text-muted)" }}>
              共 {searchResults.length} 条
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
            {searchResults.map((r, idx) => (
              <TiltCard
                key={r.id}
                className="group card-glow rounded-xl overflow-hidden border"
                style={{
                  background: "var(--bg-card)",
                  borderColor: "var(--border)",
                  opacity: 0,
                  animation: `fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) ${idx * 80}ms forwards`,
                }}
              >
                <div className="relative aspect-video overflow-hidden">
                  <img
                    src={r.preview_url || `/data/images/${r.source}_images/${r.object_key}`}
                    alt={r.caption}
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110 cursor-pointer"
                    loading="lazy"
                    onClick={() => setLightbox({ src: r.preview_url || `/data/images/${r.source}_images/${r.object_key}`, caption: r.caption })}
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                </div>
                <div className="p-4 space-y-3">
                  {/* Score bar */}
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-mono" style={{ color: "var(--text-muted)" }}>相似度</span>
                      <span className="font-mono text-sm font-bold" style={{ color: scoreColor(r.score) }}>
                        {(r.score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="h-1.5 rounded-full overflow-hidden" style={{ background: "var(--bg-secondary)" }}>
                      <div
                        className="h-full rounded-full score-bar-animate"
                        style={{
                          width: `${r.score * 100}%`,
                          background: scoreColor(r.score),
                          boxShadow: `0 0 12px -2px ${scoreColor(r.score)}`,
                          animationDelay: `${idx * 80}ms`,
                        }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className="px-2 py-0.5 text-[10px] font-mono font-semibold rounded-md"
                      style={{
                        background: r.source === "t1" ? "var(--t1)" : "var(--t2)",
                        color: "#0f172a",
                      }}
                    >
                      {r.source?.toUpperCase()}
                    </span>
                    <span className="font-mono text-[10px] truncate" style={{ color: "var(--text-muted)" }}>
                      {r.id.slice(0, 8)}...{r.id.slice(-4)}
                    </span>
                  </div>
                  <p className="text-xs leading-relaxed line-clamp-2" style={{ color: "var(--text-secondary)" }}>
                    {r.caption || "无描述"}
                  </p>
                </div>
              </TiltCard>
            ))}
          </div>
        </div>
      )}

      {searchResults.length === 0 && !searchLoading && !searchError && (
        <div className="flex flex-col items-center justify-center py-24 gap-4" style={{ color: "var(--text-muted)" }}>
          <div className="p-4 rounded-2xl border" style={{ borderColor: "var(--border)", background: "var(--bg-secondary)" }}>
            <ImageOff className="w-10 h-10" />
          </div>
          <p className="text-sm">输入查询后点击"开始检索"</p>
        </div>
      )}

      {lightbox && (
        <Lightbox
          src={lightbox.src}
          caption={lightbox.caption}
          onClose={() => setLightbox(null)}
        />
      )}
    </div>
  );
}
