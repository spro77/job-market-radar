import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Joins class names; a later Tailwind class wins over a conflicting earlier one (shadcn/ui). */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** A chart token name ("chart-3") becomes var(--chart-3); a CSS color passes through. */
export function tokenColor(color: string | undefined, fallback = 'var(--chart-1)') {
  if (!color) return fallback
  return /^(#|rgb|hsl|oklch|var\()/.test(color) ? color : `var(--${color})`
}
