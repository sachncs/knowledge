import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";

interface Tab {
  id: string;
  label: string;
  code: string;
}

interface Props {
  tabs: Tab[];
}

export default function CodeTabs({ tabs }: Props) {
  const [active, setActive] = useState(tabs[0]?.id);
  const tab = tabs.find((t) => t.id === active) ?? tabs[0];

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(tab.code);
    } catch {}
  };

  return (
    <div className="code-shell overflow-hidden">
      {/* Header */}
      <div className="code-shell__head">
        <div className="flex items-center gap-3">
          <div className="code-dots">
            <span style={{ background: "#FF5F57" }} />
            <span style={{ background: "#FEBC2E" }} />
            <span style={{ background: "#28C840" }} />
          </div>
          <div className="ml-2 flex items-center gap-1 rounded-full border border-[var(--border)] bg-[var(--bg)] p-0.5">
            {tabs.map((t) => {
              const isActive = t.id === active;
              return (
                <button
                  key={t.id}
                  type="button"
                  onClick={() => setActive(t.id)}
                  className={`relative rounded-full px-3 py-1 text-[12px] font-medium transition-colors duration-200 ${
                    isActive
                      ? "text-ink-900 dark:text-ink-50"
                      : "text-ink-500 hover:text-ink-700 dark:text-ink-400 dark:hover:text-ink-200"
                  }`}
                >
                  {isActive && (
                    <motion.span
                      layoutId="code-tab-pill"
                      transition={{ type: "spring", stiffness: 320, damping: 28 }}
                      className="absolute inset-0 rounded-full bg-[var(--bg-soft)] shadow-ring"
                    />
                  )}
                  <span className="relative z-10">{t.label}</span>
                </button>
              );
            })}
          </div>
        </div>
        <button
          type="button"
          onClick={copy}
          aria-label="Copy code"
          className="inline-flex h-7 items-center gap-1.5 rounded-md border border-[var(--border)] bg-[var(--bg)] px-2.5 text-[11px] font-medium text-ink-500 transition-colors hover:text-ink-900 dark:text-ink-400 dark:hover:text-ink-50"
        >
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect width="14" height="14" x="8" y="8" rx="2" />
            <path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2" />
          </svg>
          Copy
        </button>
      </div>

      {/* Body */}
      <div className="relative">
        <AnimatePresence mode="wait">
          <motion.pre
            key={tab.id}
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.25 }}
            className="overflow-x-auto bg-[var(--bg-deep)] p-5 font-mono text-[12.5px] leading-[1.7] text-ink-100 sm:p-7"
          >
            <code className="block">{renderColored(tab.code, tab.id)}</code>
          </motion.pre>
        </AnimatePresence>
      </div>
    </div>
  );
}

/**
 * Tiny custom syntax highlighter — no external deps, three languages:
 *  - shell-ish (CLI tab)
 *  - python (Python API tab)
 *  - markdown / tree (Output tab)
 */
function renderColored(code: string, tab: string) {
  const lines = code.split("\n");
  return lines.map((line, i) => {
    let lineEl: React.ReactNode = line.length === 0 ? "\u00A0" : line;
    if (tab === "cli") {
      lineEl = highlightShell(line);
    } else if (tab === "python") {
      lineEl = highlightPython(line);
    } else if (tab === "bundle") {
      lineEl = highlightBundle(line);
    }
    return (
      <span key={i} className="block">
        {lineEl}
      </span>
    );
  });
}

function highlightShell(line: string): React.ReactNode {
  if (line.startsWith("$ ")) {
    const rest = line.slice(2);
    return (
      <>
        <span style={{ color: "#6c768c" }}>$</span>{" "}
        {highlightShellCmd(rest)}
      </>
    );
  }
  if (line.startsWith("▸ ")) return <span style={{ color: "#8B95A8" }}>{line}</span>;
  if (line.startsWith("✓ ")) return <span style={{ color: "#5EEAD4" }}>{line}</span>;
  if (line.startsWith("# ")) return <span style={{ color: "#6c768c" }}>{line}</span>;
  // Continuation lines — highlight URLs, paths, and arguments
  if (/https?:\/\/|^\s+\S|^\.\/|^\//.test(line)) return highlightShellCmd(line);
  return line;
}

function highlightShellCmd(s: string): React.ReactNode {
  // Split on whitespace but keep tokens intact.
  const parts = s.split(/(\s+)/);
  let seenFirstNonWs = false;
  return parts.map((p, i) => {
    if (/^\s+$/.test(p)) return <span key={i}>{p}</span>;
    if (p === "\\") return <span key={i} style={{ color: "#B5C0FF" }}>{p}</span>;
    if (/^https?:\/\//.test(p)) return <span key={i} style={{ color: "#5EEAD4" }}>{p}</span>;
    if (!seenFirstNonWs) {
      seenFirstNonWs = true;
      return <span key={i} style={{ color: "#9AA8FF" }}>{p}</span>;
    }
    // Subcommand (next non-whitespace token) — slightly different accent
    if (/^[a-z][a-z-]*$/i.test(p) && /^(create|update|remove|build|test|run|fetch|list|get|set|delete|add)$/i.test(p)) {
      return <span key={i} style={{ color: "#B5C0FF" }}>{p}</span>;
    }
    if (p.startsWith("-")) return <span key={i} style={{ color: "#B5C0FF" }}>{p}</span>;
    if (/^\.\//.test(p) || /^\//.test(p)) return <span key={i} style={{ color: "#B5C0FF" }}>{p}</span>;
    return <span key={i}>{p}</span>;
  });
}

function highlightPython(line: string): React.ReactNode {
  if (line.startsWith("#")) return <span style={{ color: "#6c768c" }}>{line}</span>;
  if (line.startsWith("from ") || line.startsWith("import ")) {
    return <span style={{ color: "#9AA8FF" }}>{line}</span>;
  }
  // simple highlights
  const tokens = line.split(/(\s+|[(){}\[\],.:])/);
  return tokens.map((t, i) => {
    if (!t) return null;
    if (/^["'].*["']$/.test(t)) return <span key={i} style={{ color: "#5EEAD4" }}>{t}</span>;
    if (/^(print|from|import|return|class|def)$/.test(t)) return <span key={i} style={{ color: "#9AA8FF" }}>{t}</span>;
    if (/^(True|False|None)$/.test(t)) return <span key={i} style={{ color: "#B5C0FF" }}>{t}</span>;
    if (/^https?:\/\//.test(t)) return <span key={i} style={{ color: "#5EEAD4" }}>{t}</span>;
    if (/^[A-Za-z_][A-Za-z0-9_]*(?=\()/.test(t)) return <span key={i} style={{ color: "#FFFFFF" }}>{t}</span>;
    return <span key={i}>{t}</span>;
  });
}

function highlightBundle(line: string): React.ReactNode {
  if (line.startsWith("# ")) return <span style={{ color: "#6c768c" }}>{line}</span>;
  if (line.startsWith("---") || line === "---") return <span style={{ color: "#B5C0FF" }}>{line}</span>;
  if (line.startsWith("├──") || line.startsWith("└──") || line.startsWith("│")) {
    // tree
    const m = line.match(/^([├└│─\s]+)(.*)$/);
    if (m) {
      const indent = m[1];
      const name = m[2];
      return (
        <>
          <span style={{ color: "#6c768c" }}>{indent}</span>
          {name.includes("/") ? (
            <span style={{ color: "#9AA8FF" }}>{name}</span>
          ) : (
            <span>{name}</span>
          )}
        </>
      );
    }
  }
  // YAML-like keys
  const yamlMatch = line.match(/^([a-z_]+):/i);
  if (yamlMatch) {
    return (
      <>
        <span style={{ color: "#9AA8FF" }}>{yamlMatch[1]}</span>
        <span style={{ color: "#B5C0FF" }}>:</span>
        <span>{line.slice(yamlMatch[0].length)}</span>
      </>
    );
  }
  if (line.startsWith("- →")) return <span style={{ color: "#5EEAD4" }}>{line}</span>;
  return line;
}