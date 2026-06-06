import { NavLink, Outlet, useLocation } from "react-router-dom";
import { Database, Search, Orbit, GitCompare } from "lucide-react";
import ParticleBackground from "./ParticleBackground";
import MouseGlow from "./MouseGlow";

const navItems = [
  { to: "/vectors", icon: Database, label: "向量库" },
  { to: "/search", icon: Search, label: "相似度检索" },
  { to: "/compare", icon: GitCompare, label: "配对对比" },
];

export default function Layout() {
  const location = useLocation();

  return (
    <div className="relative flex h-screen w-screen overflow-hidden" style={{ background: "var(--bg-primary)" }}>
      <ParticleBackground />
      <MouseGlow />
      {/* Sidebar */}
      <aside className="hidden md:flex flex-col w-60 shrink-0 border-r relative z-10" style={{ borderColor: "var(--border)", background: "rgba(15,23,42,0.8)" }}>
        <div className="flex items-center gap-3 px-6 h-16">
          <div className="relative">
            <Orbit className="w-6 h-6" style={{ color: "var(--accent)" }} />
            <div className="absolute inset-0 blur-lg opacity-50" style={{ background: "var(--accent)" }} />
          </div>
          <div>
            <span className="font-semibold text-sm tracking-wide block">Image RAG</span>
            <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>知识库控制台</span>
          </div>
        </div>

        <nav className="flex-1 py-4 px-3 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.to;
            return (
              <NavLink
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                  isActive ? "font-medium" : "hover:bg-white/[0.03]"
                }`}
                style={{
                  background: isActive ? "rgba(56,189,248,0.08)" : undefined,
                  color: isActive ? "var(--accent)" : "var(--text-secondary)",
                }}
              >
                <div className={`relative ${isActive ? "" : ""}`}>
                  <item.icon className="w-4 h-4" />
                  {isActive && (
                    <div className="absolute inset-0 blur-md opacity-60" style={{ background: "var(--accent)" }} />
                  )}
                </div>
                {item.label}
                {isActive && (
                  <div className="ml-auto w-1 h-4 rounded-full" style={{ background: "var(--accent)" }} />
                )}
              </NavLink>
            );
          })}
        </nav>

        <div className="px-4 py-4 border-t" style={{ borderColor: "var(--border)" }}>
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg" style={{ background: "rgba(52,211,153,0.05)" }}>
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full opacity-75" style={{ background: "var(--t2)" }} />
              <span className="relative inline-flex rounded-full h-2 w-2" style={{ background: "var(--t2)" }} />
            </span>
            <span className="text-xs" style={{ color: "var(--text-muted)" }}>服务正常运行</span>
          </div>
        </div>
      </aside>

      {/* Mobile bottom nav */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 flex justify-around border-t h-16 items-center glass">
        {navItems.map((item) => {
          const isActive = location.pathname === item.to;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className="flex flex-col items-center gap-1 text-xs py-1 px-4 rounded-lg transition-colors"
              style={{
                color: isActive ? "var(--accent)" : "var(--text-muted)",
                background: isActive ? "rgba(56,189,248,0.08)" : undefined,
              }}
            >
              <item.icon className="w-5 h-5" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative z-10">
        <header className="flex items-center justify-between h-16 px-6 border-b shrink-0 glass">
          <h1 className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
            {location.pathname === "/vectors" ? "向量库浏览" : location.pathname === "/compare" ? "图像配对对比" : "语义相似度检索"}
          </h1>
          <div className="flex items-center gap-3">
            <span className="px-2 py-1 rounded-md text-[10px] font-mono border" style={{ borderColor: "var(--border)", color: "var(--text-muted)" }}>
              v0.1.0
            </span>
          </div>
        </header>
        <div className="flex-1 overflow-auto p-6 pb-20 md:pb-6">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
