import { useCallback, useEffect, useRef, useState } from 'react';
import { useReducedMotion } from 'motion/react';

const GLYPHS = 'abcdefghijklmnopqrstuvwxyz0123456789#%&*+=<>/';

/**
 * Scramble-to-reveal text: characters resolve left to right.
 * Plays on mount and again on hover.
 */
export default function DecryptedText({ text, className = '', speed = 38, as: Tag = 'div' }) {
  const reduced = useReducedMotion();
  const [shown, setShown] = useState(reduced ? text : '');
  const [revealed, setRevealed] = useState(reduced ? text.length : 0);
  const timer = useRef(0);

  const play = useCallback(() => {
    if (reduced) return;
    clearInterval(timer.current);
    let step = 0;
    const total = text.length * 2;
    timer.current = setInterval(() => {
      step += 1;
      const done = Math.floor(step / 2);
      setRevealed(done);
      setShown(
        text
          .split('')
          .map((ch, i) => (i < done || ch === ' ' ? ch : GLYPHS[(Math.random() * GLYPHS.length) | 0]))
          .join('')
      );
      if (step >= total) clearInterval(timer.current);
    }, speed);
  }, [text, speed, reduced]);

  useEffect(() => {
    play();
    return () => clearInterval(timer.current);
  }, [play]);

  return (
    <Tag className={className} onMouseEnter={play} aria-label={text}>
      <span aria-hidden="true">
        {shown.split('').map((ch, i) => (
          <span key={i} className={i < revealed ? undefined : 'decrypt-scrambled'}>{ch}</span>
        ))}
      </span>
    </Tag>
  );
}
