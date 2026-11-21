import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Builds the static site into ../docs, which Vercel (vercel.json) and GitHub Pages serve.
export default defineConfig({
  plugins: [react()],
  base: './',
  build: {
    outDir: '../docs',
    emptyOutDir: true,
  },
});
