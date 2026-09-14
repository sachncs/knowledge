import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";

type Link = { href: string; label: string };

interface Props {
  links: Link[];
}

export default function MobileMenu({ links }: Props) {
  const [open, setOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    const prev = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = prev;
    };
  }, [open]);

  return (
    <>
      <button
        type="button"
        aria-label="Toggle menu"
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        className="relative inline-flex h-9 w-9 items-center justify-center rounded-full border border-[var(--border-strong)] bg-[var(--bg-elev)] text-ink-600 transition-all hover:bg-[var(--bg-soft)] hover:text-ink-900 dark:text-ink-300 dark:hover:text-ink-50 lg:hidden"
      >
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
          {open ? (
            <>
              <path d="M18 6 6 18" />
              <path d="m6 6 12 12" />
            </>
          ) : (
            <>
              <path d="M4 6h16" />
              <path d="M4 12h16" />
              <path d="M4 18h16" />
            </>
          )}
        </svg>
      </button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 z-40 lg:hidden"
            onClick={() => setOpen(false)}
          >
            <div
              className="absolute inset-0 bg-[color-mix(in_oklab,var(--bg)_85%,transparent)] backdrop-blur-xl"
              aria-hidden="true"
            />
            <motion.nav
              initial={{ y: -20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              exit={{ y: -20, opacity: 0 }}
              transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
              onClick={(e) => e.stopPropagation()}
              className="relative mx-auto mt-[80px] w-[calc(100%-2rem)] max-w-md rounded-2xl border border-[var(--border)] bg-[var(--bg-elev)] p-4 shadow-elev"
              aria-label="Mobile"
            >
              <ul className="flex flex-col">
                {links.map((link) => (
                  <li key={link.href}>
                    <a
                      href={link.href}
                      onClick={() => setOpen(false)}
                      className="block rounded-xl px-4 py-3 text-base font-medium text-ink-700 transition-colors hover:bg-[var(--bg-soft)] hover:text-ink-900 dark:text-ink-200 dark:hover:text-ink-50"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
              <div className="mt-2 flex flex-col gap-2 border-t border-[var(--border)] pt-3">
                <a
                  href="https://github.com/sachncs/knowledge"
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => setOpen(false)}
                  className="btn-ghost w-full justify-center"
                >
                  View on GitHub
                </a>
                <a
                  href="https://github.com/sachncs/knowledge#installation"
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={() => setOpen(false)}
                  className="btn-primary w-full justify-center"
                >
                  Get started
                </a>
              </div>
            </motion.nav>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}