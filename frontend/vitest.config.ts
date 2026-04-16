import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    include: ['src/__tests__/**/*.test.ts'],
    exclude: ['node_modules', 'dist'],
    globals: true,
    environmentMatchGlobs: [
      ['src/__tests__/**/*.test.ts', 'jsdom']
    ]
  }
})