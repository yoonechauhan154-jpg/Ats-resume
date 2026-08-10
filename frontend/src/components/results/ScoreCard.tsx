"use client";

import { useEffect, useState } from "react";

import { Card, CardContent } from "@/components/ui/card";
import { formatScore } from "@/lib/utils";

export function ringColor(score: number): string {
  if (score >= 71) return "#10b981";
  if (score >= 41) return "#f59e0b";
  return "#ef4444";
}

function ringText(score: number): string {
  if (score >= 71) return "text-emerald-600 dark:text-emerald-400";
  if (score >= 41) return "text-amber-600 dark:text-amber-400";
  return "text-red-600 dark:text-red-400";
}

export function ScoreCard({ score }: { score: number }) {
  const [animated, setAnimated] = useState(0);
  const clamped = Math.max(0, Math.min(100, score));
  const radius = 88;
  const circumference = 2 * Math.PI * radius;

  useEffect(() => {
    const raf = requestAnimationFrame(() => setAnimated(clamped));
    return () => cancelAnimationFrame(raf);
  }, [clamped]);

  const offset = circumference - (animated / 100) * circumference;

  return (
    <Card className="h-full">
      <CardContent className="flex flex-col items-center justify-center gap-5 p-6">
        <div className="relative h-52 w-52">
          <svg viewBox="0 0 200 200" className="h-full w-full -rotate-90">
            <circle
              cx="100"
              cy="100"
              r={radius}
              fill="none"
              stroke="hsl(var(--muted))"
              strokeWidth="14"
            />
            <circle
              cx="100"
              cy="100"
              r={radius}
              fill="none"
              stroke={ringColor(clamped)}
              strokeWidth="14"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              style={{ transition: "stroke-dashoffset 1.1s ease, stroke 0.3s ease" }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className={`text-5xl font-bold tracking-tight ${ringText(clamped)}`}>
              {formatScore(clamped)}
            </span>
            <span className="text-sm font-medium text-muted-foreground">out of 100</span>
          </div>
        </div>

        <div className="text-center">
          <p className="text-lg font-semibold">ATS Compatibility Score</p>
          <div className="mt-2 flex items-center justify-center gap-3 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full" style={{ background: "#ef4444" }} /> 0-40
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full" style={{ background: "#f59e0b" }} /> 41-70
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full" style={{ background: "#10b981" }} /> 71-100
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
