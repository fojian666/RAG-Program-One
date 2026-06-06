import { WifiOff, ClockAlert, AlertTriangle } from "lucide-react";
import { ApiError } from "../api";

interface ErrorDisplayProps {
  error: Error | string | null;
}

export default function ErrorDisplay({ error }: ErrorDisplayProps) {
  if (!error) return null;

  const message = typeof error === "string" ? error : error.message;
  let kind: string | undefined;
  if (error instanceof ApiError) {
    kind = error.kind;
  }

  const configs: Record<string, { icon: typeof WifiOff; color: string; title: string; hint: string }> = {
    timeout: {
      icon: ClockAlert,
      color: "#f59e0b",
      title: "请求超时",
      hint: "后端处理较慢或网络不稳定，请稍后重试",
    },
    network: {
      icon: WifiOff,
      color: "#f87171",
      title: "网络连接失败",
      hint: "请确认后端服务已启动（./start.sh）",
    },
    client: {
      icon: AlertTriangle,
      color: "#f59e0b",
      title: "请求参数错误",
      hint: "请检查输入内容是否正确",
    },
    server: {
      icon: AlertTriangle,
      color: "#f87171",
      title: "服务端错误",
      hint: "服务器内部出错，请查看后端日志",
    },
  };

  const cfg = configs[kind || "server"];
  const Icon = cfg.icon;

  return (
    <div
      className="flex items-start gap-3 p-4 rounded-xl border"
      style={{
        borderColor: `${cfg.color}30`,
        background: `${cfg.color}08`,
      }}
    >
      <div
        className="flex items-center justify-center w-8 h-8 rounded-lg shrink-0"
        style={{ background: `${cfg.color}15` }}
      >
        <Icon className="w-4 h-4" style={{ color: cfg.color }} />
      </div>
      <div className="min-w-0">
        <p className="text-sm font-medium" style={{ color: cfg.color }}>
          {cfg.title}
        </p>
        <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
          {message}
        </p>
        <p className="text-[11px] mt-1" style={{ color: "var(--text-muted)" }}>
          {cfg.hint}
        </p>
      </div>
    </div>
  );
}
