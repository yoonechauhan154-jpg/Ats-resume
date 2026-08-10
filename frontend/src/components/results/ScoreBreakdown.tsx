"use client";

import { Info } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import type { ScoreComponent } from "@/lib/types";

interface BarDef {
  key: "keyword_match" | "content" | "format_compat";
  label: string;
  outOf: number;
  why: string;
}

const BARS: BarDef[] = [
  {
    key: "keyword_match",
    label: "Keyword Match",
    outOf: 50,
    why: "Recruiters and ATS rank you on how many exact JD keywords appear in your resume. This is usually the single biggest lever for interviews.",
  },
  {
    key: "content",
    label: "Content Relevance",
    outOf: 30,
    why: "Whether your resume has the core sections a recruiter screens for and whether your bullets are quantified and achievement-focused.",
  },
  {
    key: "format_compat",
    label: "Format Score",
    outOf: 20,
    why: "Tables, columns, images and unusual fonts make it hard for ATS parsers to extract your text correctly — a great resume can still get garbled.",
  },
];

function pointsFor(components: ScoreComponent[], key: BarDef["key"]): number {
  const byName: Record<string, number> = {};
  for (const c of components) byName[c.name] = c.score;
  if (key === "keyword_match") return Math.round((byName["keyword_match"] ?? 0) * 0.5);
  if (key === "content") {
    const quality = byName["content_quality"] ?? 0;
    const sections = byName["section_coverage"] ?? 0;
    return Math.round(((quality + sections) / 2) * 0.3);
  }
  return Math.round((byName["format_compat"] ?? 0) * 0.2);
}

function barColor(score: number, outOf: number): string {
  const pct = score / outOf;
  if (pct >= 0.71) return "bg-emerald-500";
  if (pct >= 0.41) return "bg-amber-500";
  return "bg-red-500";
}

export function ScoreBreakdown({ components }: { components: ScoreComponent[] }) {
  return (
    <Card className="h-full">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">Score Breakdown</CardTitle>
        <CardDescription>
          Where your points come from — every bar is derived from explicit evidence in your resume
          and the job description.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <TooltipProvider delayDuration={100}>
          {BARS.map((bar) => {
            const points = pointsFor(components, bar.key);
            return (
              <div key={bar.key} className="space-y-1.5">
                <div className="flex items-center justify-between text-sm">
                  <span className="flex items-center gap-1.5 font-medium">
                    {bar.label}
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <span className="inline-flex cursor-help text-muted-foreground">
                          <Info className="h-3.5 w-3.5" />
                        </span>
                      </TooltipTrigger>
                      <TooltipContent side="top" className="max-w-xs">
                        {bar.why}
                      </TooltipContent>
                    </Tooltip>
                  </span>
                  <span className="font-semibold tabular-nums">
                    {points}
                    <span className="font-normal text-muted-foreground"> / {bar.outOf}</span>
                  </span>
                </div>
                <Progress
                  value={(points / bar.outOf) * 100}
                  className="h-2.5"
                  indicatorClassName={barColor(points, bar.outOf)}
                />
              </div>
            );
          })}
        </TooltipProvider>
        <p className="pt-1 text-xs text-muted-foreground">
          Breakdown uses a 50 / 30 / 20 weighting to show where points are lost. Your overall score
          (top) is the official weighted score and is what the score ring shows.
        </p>
      </CardContent>
    </Card>
  );
}
