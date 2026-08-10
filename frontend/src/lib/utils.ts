import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatScore(score: number): string {
  return Math.round(score).toString();
}

export function scoreColor(score: number): string {
  if (score >= 80) return "text-emerald-600 dark:text-emerald-400";
  if (score >= 60) return "text-amber-600 dark:text-amber-400";
  return "text-red-600 dark:text-red-400";
}

export function scoreRing(score: number): string {
  if (score >= 80) return "#10b981";
  if (score >= 60) return "#f59e0b";
  return "#ef4444";
}

export function severityStyles(severity: string) {
  switch (severity) {
    case "critical":
      return { border: "border-red-500/40", bg: "bg-red-50 dark:bg-red-950/40", text: "text-red-700 dark:text-red-300", dot: "bg-red-500" };
    case "warning":
      return { border: "border-amber-500/40", bg: "bg-amber-50 dark:bg-amber-950/40", text: "text-amber-700 dark:text-amber-300", dot: "bg-amber-500" };
    default:
      return { border: "border-slate-300 dark:border-slate-700", bg: "bg-slate-50 dark:bg-slate-900/60", text: "text-slate-600 dark:text-slate-300", dot: "bg-slate-400" };
  }
}

export function categoryLabel(category: string): string {
  switch (category) {
    case "hard_skill":
      return "Skill";
    case "soft_skill":
      return "Soft skill";
    case "credential":
      return "Credential";
    case "tool":
      return "Tool";
    default:
      return category;
  }
}
