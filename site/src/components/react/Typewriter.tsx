import { useEffect, useState } from "react";

interface Props {
  text: string;
  speed?: number;
  className?: string;
}

export default function Typewriter({ text, speed = 90, className = "" }: Props) {
  const [out, setOut] = useState("");
  const [done, setDone] = useState(false);

  useEffect(() => {
    let i = 0;
    let cancelled = false;

    const tick = () => {
      if (cancelled) return;
      i += 1;
      setOut(text.slice(0, i));
      if (i >= text.length) {
        setDone(true);
        return;
      }
      setTimeout(tick, speed + Math.random() * 30);
    };

    const start = setTimeout(tick, 280);
    return () => {
      cancelled = true;
      clearTimeout(start);
    };
  }, [text, speed]);

  return (
    <span className={className}>
      {out || "\u00A0"}
      {!done && <span className="caret" />}
    </span>
  );
}