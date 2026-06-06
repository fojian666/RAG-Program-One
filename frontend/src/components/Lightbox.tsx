import { useRef, useEffect } from "react";
import { X } from "lucide-react";

interface LightboxProps {
  src: string;
  caption: string;
  onClose: () => void;
}

export default function Lightbox({ src, caption, onClose }: LightboxProps) {
  const dialogRef = useRef<HTMLDialogElement>(null);
  const fullSrc = src.startsWith("/") ? `http://localhost:8000${src}` : src;

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog) {
      dialog.showModal();
      document.body.style.overflow = "hidden";
    }
    return () => {
      if (dialog) {
        dialog.close();
      }
      document.body.style.overflow = "";
    };
  }, []);

  return (
    <dialog
      ref={dialogRef}
      onClick={onClose}
      style={{
        background: "transparent",
        border: "none",
        padding: 0,
        margin: "auto",
        maxWidth: "100vw",
        maxHeight: "100vh",
        overflow: "visible",
      }}
    >
      <div
        style={{
          position: "fixed",
          inset: 0,
          background: "rgba(0,0,0,0.9)",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          padding: 24,
        }}
        onClick={onClose}
      >
        <button
          onClick={onClose}
          style={{
            position: "absolute",
            top: 20,
            right: 20,
            background: "#1e293b",
            border: "1px solid rgba(148,163,184,0.2)",
            borderRadius: 12,
            padding: 10,
            color: "#cbd5e1",
            cursor: "pointer",
            zIndex: 1,
          }}
        >
          <X className="w-5 h-5" />
        </button>

        <div
          style={{ textAlign: "center" }}
          onClick={(e) => e.stopPropagation()}
        >
          <img
            src={fullSrc}
            alt={caption}
            style={{
              maxWidth: "90vw",
              maxHeight: "85vh",
              borderRadius: 12,
              display: "block",
              margin: "0 auto",
            }}
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = "none";
              const err = document.getElementById("lb-err");
              if (err) err.style.display = "block";
            }}
          />
          <div id="lb-err" style={{ display: "none", color: "#94a3b8", padding: 20 }}>
            图片加载失败
          </div>
          {caption && (
            <p style={{ color: "#cbd5e1", marginTop: 12, fontSize: 14 }}>{caption}</p>
          )}
        </div>
      </div>
    </dialog>
  );
}
