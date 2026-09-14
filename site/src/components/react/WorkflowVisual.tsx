import { motion } from "motion/react";

interface Node {
  id: string;
  x: number;
  y: number;
  label: string;
  tag: "root" | "concept" | "tag";
}

const nodes: Node[] = [
  { id: "root", x: 50, y: 22, label: "index.md", tag: "root" },
  { id: "naming", x: 18, y: 56, label: "naming", tag: "concept" },
  { id: "imports", x: 50, y: 70, label: "imports", tag: "concept" },
  { id: "errors", x: 82, y: 56, label: "errors", tag: "concept" },
  { id: "naming-tag", x: 12, y: 90, label: "style/", tag: "tag" },
];

const edges = [
  { from: "root", to: "naming" },
  { from: "root", to: "imports" },
  { from: "root", to: "errors" },
  { from: "naming", to: "naming-tag" },
];

const tagColor = {
  root: "#9AA8FF",
  concept: "#5EEAD4",
  tag: "#7C8BFF",
};

const tagBg = {
  root: "rgba(154,168,255,0.15)",
  concept: "rgba(94,234,212,0.12)",
  tag: "rgba(124,139,255,0.12)",
};

export default function WorkflowVisual() {
  return (
    <div className="relative aspect-[4/3] w-full overflow-hidden rounded-xl">
      {/* Faint grid */}
      <svg
        className="absolute inset-0 h-full w-full text-[var(--border)]"
        aria-hidden="true"
      >
        <defs>
          <pattern id="wf-grid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M 32 0 L 0 0 0 32" fill="none" stroke="currentColor" strokeWidth="0.6" />
          </pattern>
          <radialGradient id="wf-glow" cx="50%" cy="40%" r="60%">
            <stop offset="0%" stopColor="rgba(91,107,242,0.30)" />
            <stop offset="100%" stopColor="rgba(91,107,242,0)" />
          </radialGradient>
        </defs>
        <rect width="100%" height="100%" fill="url(#wf-grid)" />
        <rect width="100%" height="100%" fill="url(#wf-glow)" />
      </svg>

      {/* Edges */}
      <svg
        className="absolute inset-0 h-full w-full"
        viewBox="0 0 100 100"
        preserveAspectRatio="none"
      >
        {edges.map((e, i) => {
          const a = nodes.find((n) => n.id === e.from)!;
          const b = nodes.find((n) => n.id === e.to)!;
          return (
            <motion.line
              key={i}
              x1={a.x}
              y1={a.y}
              x2={b.x}
              y2={b.y}
              stroke="rgba(124,139,255,0.55)"
              strokeWidth="0.4"
              strokeLinecap="round"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 1 }}
              transition={{ duration: 1.4, delay: 0.4 + i * 0.2, ease: [0.16, 1, 0.3, 1] }}
            />
          );
        })}
      </svg>

      {/* Nodes */}
      {nodes.map((n, i) => (
        <motion.div
          key={n.id}
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{
            delay: 0.2 + i * 0.12,
            duration: 0.6,
            ease: [0.16, 1, 0.3, 1],
          }}
          className="absolute"
          style={{
            left: `${n.x}%`,
            top: `${n.y}%`,
            transform: "translate(-50%, -50%)",
          }}
        >
          <motion.div
            animate={{ y: [0, -2, 0] }}
            transition={{ duration: 4 + i * 0.4, repeat: Infinity, ease: "easeInOut" }}
            className="flex items-center gap-1.5 rounded-full border px-2.5 py-1 font-mono text-[10px] backdrop-blur"
            style={{
              background: tagBg[n.tag],
              borderColor: "rgba(124,139,255,0.25)",
              color: tagColor[n.tag],
            }}
          >
            <span
              className="h-1.5 w-1.5 rounded-full"
              style={{ background: tagColor[n.tag] }}
            />
            {n.label}
          </motion.div>
        </motion.div>
      ))}
    </div>
  );
}