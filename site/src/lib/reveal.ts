/**
 * Reveal-on-scroll helper. Adds `is-visible` to elements with
 * `.reveal` or `.stagger` when they enter the viewport.
 *
 * Uses IntersectionObserver and only ever runs on the client.
 */
export function initRevealOnScroll() {
  if (typeof window === "undefined") return;

  const targets = document.querySelectorAll<HTMLElement>(".reveal, .stagger");
  if (!targets.length) return;

  const io = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          io.unobserve(entry.target);
        }
      }
    },
    {
      rootMargin: "0px 0px -10% 0px",
      threshold: 0.1,
    },
  );

  targets.forEach((el) => io.observe(el));
}

/**
 * Smooth-scroll for in-page anchors with a header offset.
 */
export function initSmoothAnchors(offset = 80) {
  if (typeof window === "undefined") return;

  document.addEventListener("click", (e) => {
    const target = e.target as HTMLElement | null;
    if (!target) return;
    const anchor = target.closest<HTMLAnchorElement>("a[href^='#']");
    if (!anchor) return;
    const href = anchor.getAttribute("href");
    if (!href || href === "#") return;

    const el = document.querySelector<HTMLElement>(href);
    if (!el) return;

    e.preventDefault();
    const top = el.getBoundingClientRect().top + window.scrollY - offset;
    window.scrollTo({ top, behavior: "smooth" });
    history.replaceState(null, "", href);
  });
}

/**
 * Mark sections for active nav highlighting.
 */
export function initActiveSectionNav() {
  if (typeof window === "undefined") return;

  const links = Array.from(
    document.querySelectorAll<HTMLAnchorElement>("[data-nav-link]"),
  );
  if (!links.length) return;

  const sections = links
    .map((l) => document.querySelector<HTMLElement>(l.getAttribute("href") || ""))
    .filter(Boolean) as HTMLElement[];

  if (!sections.length) return;

  const setActive = (id: string) => {
    links.forEach((l) => {
      const isActive = l.getAttribute("href") === `#${id}`;
      l.dataset.active = String(isActive);
      if (isActive) l.setAttribute("aria-current", "true");
      else l.removeAttribute("aria-current");
    });
  };

  const io = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((e) => e.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio);
      if (visible[0]) {
        const id = visible[0].target.id;
        if (id) setActive(id);
      }
    },
    { rootMargin: "-40% 0px -50% 0px", threshold: [0, 0.25, 0.5, 1] },
  );

  sections.forEach((s) => io.observe(s));
}