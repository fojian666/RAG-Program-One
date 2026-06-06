import { useEffect, useState } from "react";
import { useStore } from "../store";
import { Search, ChevronLeft, ChevronRight, ImageOff, Layers } from "lucide-react";
import Lightbox from "../components/Lightbox";
import ErrorDisplay from "../components/ErrorDisplay";
import TiltCard from "../components/TiltCard";

const sizes = [12, 24, 48];

function SkeletonCard() {
  return (
    <div className="rounded-xl overflow-hidden" style={{ background: "var(--bg-card)" }}>
      <div className="shimmer aspect-video w-full" />
      <div className="p-4 space-y-3">
        <div className="flex items-center gap-2">
          <div className="shimmer h-3 w-12 rounded" />
          <div className="shimmer h-3 w-20 rounded" />
        </div>
        <div className="shimmer h-3 w-full rounded" />
        <div className="shimmer h-3 w-2/3 rounded" />
      </div>
    </div>
  );
}

export default function VectorsPage() {
  const {
    images,
    totalImages,
    imagesLoading,
    imagesError,
    filters,
    setFilter,
    fetchImages,
  } = useStore();

  const [lightbox, setLightbox] = useState<{ src: string; caption: string } | null>(null);

  useEffect(() => {
    fetchImages();
  }, [filters.page, filters.size, filters.source, filters.query]);

  const totalPages = Math.max(1, Math.ceil(totalImages / filters.size));

  return (
    <div className="space-y-5 animate-fade-in-up max-w-7xl mx-auto">
      {/* Header stats */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg border text-xs" style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}>
          <Layers className="w-3.5 h-3.5" />
          共 {totalImages} 张图片
        </div>
      </div>

      {/* Toolbar */}
      <div className="flex flex-col lg:flex-row gap-4 lg:items-center justify-between">
        <div className="flex items-center gap-2">
          {[
            { key: null, label: "全部来源", count: totalImages },
            { key: "t1", label: "T1", color: "var(--t1)" },
            { key: "t2", label: "T2", color: "var(--t2)" },
          ].map((item) => (
            <button
              key={item.label}
              onClick={() => setFilter("source", item.key)}
              className="px-3.5 py-2 text-xs font-medium rounded-lg border transition-all duration-200"
              style={{
                borderColor: filters.source === item.key ? item.color || "var(--accent)" : "var(--border)",
                background: filters.source === item.key
                  ? (item.color ? `${item.color}12` : "rgba(56,189,248,0.1)")
                  : "transparent",
                color: filters.source === item.key
                  ? (item.color || "var(--accent)")
                  : "var(--text-secondary)",
                boxShadow: filters.source === item.key
                  ? `0 0 20px -4px ${item.color || "var(--accent)"}30`
                  : "none",
              }}
            >
              {item.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5" style={{ color: "var(--text-muted)" }} />
            <input
              type="text"
              placeholder="搜索描述关键词..."
              value={filters.query}
              onChange={(e) => setFilter("query", e.target.value)}
              className="pl-9 pr-4 py-2 text-xs rounded-lg border input-glow w-56"
              style={{
                background: "var(--bg-secondary)",
                borderColor: "var(--border)",
                color: "var(--text-primary)",
              }}
            />
          </div>
          <select
            value={filters.size}
            onChange={(e) => setFilter("size", Number(e.target.value))}
            className="px-3 py-2 text-xs rounded-lg border outline-none"
            style={{ background: "var(--bg-secondary)", borderColor: "var(--border)", color: "var(--text-secondary)" }}
          >
            {sizes.map((s) => (
              <option key={s} value={s}>{s} 条/页</option>
            ))}
          </select>
        </div>
      </div>

      {/* Error */}
      {imagesError && <ErrorDisplay error={imagesError} />}

      {/* Grid */}
      {imagesLoading && images.length === 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {Array.from({ length: filters.size }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      ) : images.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4" style={{ color: "var(--text-muted)" }}>
          <div className="p-4 rounded-2xl border" style={{ borderColor: "var(--border)", background: "var(--bg-secondary)" }}>
            <ImageOff className="w-10 h-10" />
          </div>
          <p className="text-sm">暂无数据</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 stagger-grid">
          {images.map((img, idx) => (
            <TiltCard key={img.id}>
              <div
                className="group card-glow rounded-xl overflow-hidden border"
                style={{
                  background: "var(--bg-card)",
                  borderColor: "var(--border)",
                  animationDelay: `${idx * 60}ms`,
                  opacity: 0,
                  animation: `fadeInUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) ${idx * 60}ms forwards`,
                }}
              >
              <div className="relative aspect-video overflow-hidden">
                <img
                  src={img.preview_url || `/data/images/${img.source}_images/${img.object_key}`}
                  alt={img.caption}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110 cursor-pointer"
                  onClick={() => setLightbox({ src: img.preview_url || `/data/images/${img.source}_images/${img.object_key}`, caption: img.caption })}
                />
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none" />
                <span
                  className="absolute top-3 left-3 px-2 py-0.5 text-[10px] font-mono font-semibold rounded-md"
                  style={{
                    background: img.source === "t1" ? "var(--t1)" : "var(--t2)",
                    color: "#0f172a",
                    boxShadow: `0 0 12px -2px ${img.source === "t1" ? "var(--t1)" : "var(--t2)"}`,
                  }}
                >
                  {img.source?.toUpperCase()}
                </span>
              </div>
              <div className="p-4 space-y-2">
                <p className="font-mono text-[10px] truncate" style={{ color: "var(--text-muted)" }}>
                  {img.id.slice(0, 8)}...{img.id.slice(-4)}
                </p>
                <p className="text-xs leading-relaxed line-clamp-2" style={{ color: "var(--text-secondary)" }}>
                  {img.caption || "无描述"}
                </p>
                <p className="text-[10px] font-mono" style={{ color: "var(--text-muted)" }}>
                  {img.created_at ? new Date(img.created_at).toLocaleString("zh-CN", { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" }) : "—"}
                </p>
              </div>
              </div>
            </TiltCard>
          ))}
        </div>
      )}

      {/* Pagination */}
      {lightbox && (
        <Lightbox
          src={lightbox.src}
          caption={lightbox.caption}
          onClose={() => setLightbox(null)}
        />
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 pt-4">
          <button
            disabled={filters.page <= 1}
            onClick={() => setFilter("page", filters.page - 1)}
            className="p-2 rounded-lg border disabled:opacity-30 transition-all hover:bg-white/5 hover:border-white/10"
            style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <div className="flex items-center gap-1">
            {Array.from({ length: totalPages }, (_, i) => i + 1).map((p) => (
              <button
                key={p}
                onClick={() => setFilter("page", p)}
                className="w-8 h-8 rounded-lg text-xs font-mono transition-all"
                style={{
                  background: filters.page === p ? "var(--accent)" : "transparent",
                  color: filters.page === p ? "#0f172a" : "var(--text-muted)",
                  fontWeight: filters.page === p ? 600 : 400,
                }}
              >
                {p}
              </button>
            ))}
          </div>
          <button
            disabled={filters.page >= totalPages}
            onClick={() => setFilter("page", filters.page + 1)}
            className="p-2 rounded-lg border disabled:opacity-30 transition-all hover:bg-white/5 hover:border-white/10"
            style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}
