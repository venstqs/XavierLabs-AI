import { useRef } from 'react';
import { motion, useMotionValue, useSpring, useReducedMotion } from 'motion/react';

/**
 * Card with a cursor-following spotlight, a glowing border under the cursor,
 * and a gentle 3D tilt. Fades up when scrolled into view.
 */
export default function SpotlightCard({ children, className = '', index = 0, tilt = 6 }) {
  const ref = useRef(null);
  const reduced = useReducedMotion();
  const rx = useSpring(useMotionValue(0), { stiffness: 220, damping: 20 });
  const ry = useSpring(useMotionValue(0), { stiffness: 220, damping: 20 });

  const onMove = (e) => {
    const el = ref.current;
    const r = el.getBoundingClientRect();
    const px = (e.clientX - r.left) / r.width;
    const py = (e.clientY - r.top) / r.height;
    el.style.setProperty('--mx', `${px * 100}%`);
    el.style.setProperty('--my', `${py * 100}%`);
    el.style.setProperty('--spot-o', '1');
    if (!reduced) {
      rx.set((0.5 - py) * tilt);
      ry.set((px - 0.5) * tilt);
    }
  };

  const onLeave = () => {
    ref.current?.style.setProperty('--spot-o', '0');
    rx.set(0);
    ry.set(0);
  };

  return (
    <motion.article
      ref={ref}
      className={className}
      onPointerMove={onMove}
      onPointerLeave={onLeave}
      style={{ rotateX: rx, rotateY: ry }}
      initial={{ opacity: 0, y: 18 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-60px' }}
      transition={{ duration: 0.5, delay: (index % 3) * 0.08, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.article>
  );
}
