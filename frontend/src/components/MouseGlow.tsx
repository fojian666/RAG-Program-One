import { useEffect, useRef } from "react";

export default function MouseGlow() {
  const glowRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const onMouseMove = (e: MouseEvent) => {
      const glow = glowRef.current;
      if (!glow) return;
      glow.style.left = `${e.clientX}px`;
      glow.style.top = `${e.clientY}px`;
      glow.style.opacity = "1";
    };

    const onMouseLeave = () => {
      const glow = glowRef.current;
      if (!glow) return;
      glow.style.opacity = "0";
    };

    window.addEventListener("mousemove", onMouseMove);
    document.body.addEventListener("mouseleave", onMouseLeave);
    return () => {
      window.removeEventListener("mousemove", onMouseMove);
      document.body.removeEventListener("mouseleave", onMouseLeave);
    };
  }, []);

  return (
    <div
      ref={glowRef}
      style={{
        position: "fixed",
        width: 400,
        height: 400,
        borderRadius: "50%",
        pointerEvents: "none",
        zIndex: 0,
        transform: "translate(-50%, -50%)",
        background: "radial-gradient(circle, rgba(56,189,248,0.06) 0%, transparent 70%)",
        opacity: 0,
        transition: "opacity 0.3s ease",
      }}
    />
  );
}
