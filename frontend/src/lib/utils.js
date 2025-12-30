import { clsx } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs) {
  return twMerge(clsx(inputs))
}

export function getStarRatingColor(rating) {
  if (rating >= 4) return 'text-positive'
  if (rating >= 3) return 'text-neutral'
  return 'text-negative'
}
