import { useState, useRef, useCallback } from "react";

interface CompareSliderProps {
  beforeSrc: string;
  afterSrc: string;
  beforeLabel?: string;
  afterLabel?: string;
}

export default function CompareSlider({
  beforeSrc,
  afterSrc,
  beforeLabel = "T1",
  afterLabel = "T2",
}: CompareSliderProps) {
  const [sliderPosition, setSliderPosition] = useState(50);
  const containerRef = useRef<HTMLDivElement>(null);
  const isDragging = useRef(false);

  const handleMove = useCallback(
    (clientX: number) => {
      if (!containerRef.current) return;
      const rect = containerRef.current.getBoundingClientRect();
      const x = Math.max(0, Math.min(clientX - rect.left, rect.width));
      const pct = (x / rect.width) * 100;
      setSliderPosition(pct);
    },
    []
  );

  const onMouseDown = () => {
    isDragging.current = true;
  };
  const onMouseUp = () => {
    isDragging.current = false;
  };
  const onMouseMove = (e: React.MouseEvent) => {
    if (!isDragging.current) return;
    handleMove(e.clientX);
  };
  const onTouchMove = (e: React.TouchEvent) => {
    handleMove(e.touches[0].clientX);
  };

  const fullBefore = beforeSrc.startsWith("/") ? `http://localhost:8000${beforeSrc}` : beforeSrc;
  const fullAfter = afterSrc.startsWith("/") ? `http://localhost:8000${afterSrc}` : afterSrc;

  return (
    <div
      ref={containerRef}
      className="relative w-full select-none overflow-hidden rounded-xl border"
      style={{ borderColor: "var(--border)", aspectRatio: "16/9" }}
      onMouseMove={onMouseMove}
      onMouseUp={onMouseUp}
      onMouseLeave={onMouseUp}
      onTouchMove={onTouchMove}
      onTouchEnd={onMouseUp}
    >
      {/* After image (full width, background) */}
      <img
        src={fullAfter}
        alt="after"
        className="absolute inset-0 w-full h-full object-cover"
        draggable={false}
      />
      <span
        className="absolute top-3 right-3 px-2 py-0.5 text-[10px] font-mono font-semibold rounded-md z-10"
        style={{ background: "var(--t2)", color: "#0f172a" }}
      >
        {afterLabel}
      </span>

      {/* Before image (clipped by slider position) */}
      <div
        className="absolute inset-0 overflow-hidden"
        style={{ width: `${sliderPosition}%` }}
      >
        <img
          src={fullBefore}
          alt="before"
          className="absolute inset-0 w-full h-full object-cover"
          style={{ minWidth: `${100 / (sliderPosition / 100 || 0.01)}%` }}
          draggable={false}
        />
        <span
          className="absolute top-3 left-3 px-2 py-0.5 text-[10px] font-mono font-semibold rounded-md z-10"
          style={{ background: "var(--t1)", color: "#0f172a" }}
        >
          {beforeLabel}
        </span>
      </div>

      {/* Slider line + handle */}
      <div
        className="absolute top-0 bottom-0 w-0.5 cursor-ew-resize"
        style={{ left: `${sliderPosition}%`, background: "rgba(255,255,255,0.6)", transform: "translateX(-50%)" }}
        onMouseDown={onMouseDown}
        onTouchStart={onMouseDown}
      >
        <div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full border flex items-center justify-center shadow-lg"
          style={{ background: "var(--bg-secondary)", borderColor: "rgba(255,255,255,0.3)" }}
        >
          <div className="flex gap-0.5">
            <div className="w-0.5 h-3 rounded-full bg-white/60" />
            <div className="w-0.5 h-3 rounded-full bg-white/60" />
          </div>
        </div>
      </div>
    </div>
  );
}
