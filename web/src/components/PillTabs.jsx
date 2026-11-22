import { motion } from 'motion/react';

/** Tab buttons with a highlight pill that glides between the active tab (shared layout). */
export default function PillTabs({ items, value, onChange, layoutId, className, tabClassName, label }) {
  return (
    <div className={className} role="tablist" aria-label={label}>
      {items.map((it) => {
        const active = it.value === value;
        return (
          <button
            key={it.value}
            type="button"
            role="tab"
            aria-selected={active}
            className={`${tabClassName}${active ? ' active' : ''}`}
            onClick={() => onChange(it.value)}
          >
            {active && (
              <motion.span
                layoutId={layoutId}
                className="pill-indicator"
                transition={{ type: 'spring', stiffness: 420, damping: 34 }}
              />
            )}
            <span className="tab-label">{it.label}</span>
          </button>
        );
      })}
    </div>
  );
}
