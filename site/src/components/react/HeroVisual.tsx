import { motion } from "motion/react";
import { useEffect, useState } from "react";

const steps = [
  { type: "url", label: "source.pyguide.html" },
  { type: "split", label: "split by heading" },
  { type: "extract", label: "extract via LLM" },
];

const output = [
  { name: "index.md", tag: "root" },
  { name: "naming-conventions.md", tag: "concept" },
  { name: "imports.md", tag: "concept" },
  { name: "comments.md", tag: "concept" },
  { name: "type-annotations.md", tag: "concept" },
  { name: "error-handling.md", tag: "concept" },
];

const cycleMs = 5200;

export default function HeroVisual() {
  const [stage, setStage] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setStage((s) => (s + 1) % (steps.length + 1)), cycleMs / (steps.length + 1));
    return () => clearInterval(id);
  }, []);

  return (
    <div className="relative mx-auto w-full max-w-[1080px]">
      {/* Glow behind the visual */}
      <div
        className="pointer-events-none absolute -inset-x-10 -inset-y-6 -z-10 rounded-[36px] opacity-70 blur-2xl"
        style={{
          background:
            "radial-gradient(60% 50% at 50% 50%, rgba(91,107,242,0.30) 0%, rgba(91,107,242,0.10) 35%, transparent 70%)",
        }}
        aria-hidden="true"
      />

      <motion.div
        initial={{ y: 24, opacity: 0, filter: "blur(8px)" }}
        animate={{ y: 0, opacity: 1, filter: "blur(0px)" }}
        transition={{ duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
        className="code-shell shine relative overflow-hidden"
      >
        {/* Window header */}
        <div className="code-shell__head">
          <div className="code-dots">
            <span style={{ background: "#FF5F57" }} />
            <span style={{ background: "#FEBC2E" }} />
            <span style={{ background: "#28C840" }} />
          </div>
          <div className="hidden items-center gap-2 rounded-md bg-[var(--bg)] px-3 py-1 text-[11px] font-medium text-ink-400 dark:text-ink-500 sm:flex">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <path d="M9 18 3 12l6-6M15 6l6 6-6 6" />
            </svg>
            <span className="font-mono">knowledge · pyguide/</span>
          </div>
          <div className="flex items-center gap-1.5 text-[11px] text-ink-400 dark:text-ink-500">
            <span className="inline-flex h-2 w-2 rounded-full bg-mint-500" />
            <span>OKF v0.1</span>
          </div>
        </div>

        {/* Body */}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_1fr]">
          {/* Left — pipeline stages */}
          <div className="relative border-b border-[var(--border)] p-6 sm:p-8 lg:border-b-0 lg:border-r">
            <div className="mb-5 flex items-center justify-between">
              <span className="text-[11px] font-medium uppercase tracking-[0.16em] text-ink-400">
                Pipeline
              </span>
              <span className="font-mono text-[11px] text-ink-400">3 stages</span>
            </div>

            <div className="space-y-3">
              {steps.map((step, i) => {
                const active = stage === i;
                return (
                  <motion.div
                    key={step.label}
                    animate={{
                      opacity: active ? 1 : stage > i ? 0.55 : 0.35,
                      scale: active ? 1.0 : 0.98,
                    }}
                    transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
                    className="relative flex items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--bg-soft)] p-3"
                  >
                    <span
                      className="relative flex h-7 w-7 shrink-0 items-center justify-center rounded-md text-[11px] font-semibold"
                      style={{
                        background:
                          i === 0
                            ? "linear-gradient(135deg,#7C8BFF,#3D4FE0)"
                            : i === 1
                            ? "linear-gradient(135deg,#5EEAD4,#0D9488)"
                            : "linear-gradient(135deg,#B5C0FF,#7C8BFF)",
                        color: "white",
                      }}
                    >
                      {i + 1}
                    </span>
                    <span className="font-mono text-[13px] text-ink-700 dark:text-ink-200">
                      {step.label}
                    </span>
                    {active && (
                      <motion.span
                        layoutId="pipeline-pulse"
                        className="absolute right-3 inline-flex h-2 w-2 rounded-full bg-accent-500"
                        animate={{ opacity: [0.3, 1, 0.3] }}
                        transition={{ duration: 1.6, repeat: Infinity }}
                      />
                    )}
                  </motion.div>
                );
              })}
            </div>

            {/* Inline CLI snippet */}
            <div className="mt-5 overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--bg-deep)]">
              <div className="flex items-center justify-between border-b border-[var(--border)] px-3 py-1.5">
                <span className="font-mono text-[10.5px] uppercase tracking-wider text-ink-400">
                  $ terminal
                </span>
                <span className="font-mono text-[10.5px] text-ink-400">bash</span>
              </div>
              <pre className="overflow-x-auto p-3 font-mono text-[12px] leading-6 text-ink-200 dark:text-ink-100">
                <code>
                  <span className="text-ink-400">$</span>{" "}
                  <span className="text-accent-300">knowledge</span>{" "}
                  <span className="text-ink-50">create</span>{" "}
                  <span className="text-mint-400">https://google.github.io/styleguide/pyguide.html</span>{" "}
                  <span className="text-ink-400">./pyguide</span>
                  {"\n"}
                  <span className="text-ink-400">▸ fetching…</span>
                  {"\n"}
                  <span className="text-ink-400">▸ splitting… 6 sections</span>
                  {"\n"}
                  <span className="text-ink-400">▸ extracting concepts via gpt-4o…</span>
                  {"\n"}
                  <span className="text-mint-400">✓ wrote 6 concept files</span>
                </code>
              </pre>
            </div>
          </div>

          {/* Right — output bundle tree */}
          <div className="relative p-6 sm:p-8">
            <div className="mb-5 flex items-center justify-between">
              <span className="text-[11px] font-medium uppercase tracking-[0.16em] text-ink-400">
                Output bundle
              </span>
              <span className="font-mono text-[11px] text-ink-400">pyguide/</span>
            </div>

            <div className="overflow-hidden rounded-xl border border-[var(--border)] bg-[var(--bg-deep)]">
              <div className="border-b border-[var(--border)] px-4 py-2">
                <span className="font-mono text-[12px] text-ink-300">pyguide</span>
              </div>
              <ul className="divide-y divide-[var(--border)]">
                {output.map((file, i) => (
                  <motion.li
                    key={file.name}
                    initial={{ opacity: 0, x: -6 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.6 + i * 0.08, duration: 0.4 }}
                    className="flex items-center justify-between px-4 py-2.5 font-mono text-[12.5px]"
                  >
                    <span className="flex items-center gap-2.5">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" className="text-accent-400">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6Z" strokeLinejoin="round" />
                        <path d="M14 2v6h6" strokeLinejoin="round" />
                      </svg>
                      <span className="text-ink-200 dark:text-ink-100">{file.name}</span>
                    </span>
                    <span
                      className="rounded-md px-1.5 py-0.5 text-[10px] font-medium"
                      style={{
                        background: file.tag === "root" ? "rgba(91,107,242,0.15)" : "rgba(94,234,212,0.10)",
                        color: file.tag === "root" ? "#9AA8FF" : "#5EEAD4",
                      }}
                    >
                      {file.tag}
                    </span>
                  </motion.li>
                ))}
              </ul>
            </div>

            {/* Stats row */}
            <div className="mt-5 grid grid-cols-3 gap-3">
              {[
                { k: "6", v: "concepts" },
                { k: "0", v: "broken links" },
                { k: "100%", v: "diffable" },
              ].map((s) => (
                <div
                  key={s.v}
                  className="rounded-xl border border-[var(--border)] bg-[var(--bg-soft)] p-3"
                >
                  <div className="font-mono text-lg font-semibold text-ink-900 dark:text-ink-50">
                    {s.k}
                  </div>
                  <div className="mt-0.5 text-[10.5px] uppercase tracking-wider text-ink-400">
                    {s.v}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </motion.div>

      {/* Floating annotation chips */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.0, duration: 0.6 }}
        className="absolute -left-2 top-24 hidden rounded-full border border-[var(--border-strong)] bg-[var(--bg-elev)] px-3 py-1.5 text-[11px] font-medium text-ink-600 shadow-soft sm:flex dark:text-ink-300"
        aria-hidden="true"
      >
        <span className="mr-1.5 inline-flex h-1.5 w-1.5 rounded-full bg-mint-500"></span>
        version-controlled
      </motion.div>
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 1.2, duration: 0.6 }}
        className="absolute -right-2 bottom-32 hidden rounded-full border border-[var(--border-strong)] bg-[var(--bg-elev)] px-3 py-1.5 text-[11px] font-medium text-ink-600 shadow-soft sm:flex dark:text-ink-300"
        aria-hidden="true"
      >
        <span className="mr-1.5 inline-flex h-1.5 w-1.5 rounded-full bg-accent-500"></span>
        provider-agnostic
      </motion.div>
    </div>
  );
}