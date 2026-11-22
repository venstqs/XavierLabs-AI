import { motion } from 'motion/react';

export default function BlurText({ text, as = 'h1', className = '', delay = 0, stagger = 0.06 }) {
  const Tag = motion[as];
  const words = text.split(' ');
  return (
    <Tag
      className={className}
      initial="hidden"
      animate="show"
      transition={{ staggerChildren: stagger, delayChildren: delay }}
      aria-label={text}
    >
      {words.map((w, i) => (
        <motion.span
          key={i}
          className="word"
          aria-hidden="true"
          variants={{
            hidden: { opacity: 0, filter: 'blur(10px)', y: 8 },
            show: { opacity: 1, filter: 'blur(0px)', y: 0, transition: { duration: 0.55, ease: [0.22, 1, 0.36, 1] } },
          }}
        >
          {w}
          {i < words.length - 1 ? ' ' : ''}
        </motion.span>
      ))}
    </Tag>
  );
}
