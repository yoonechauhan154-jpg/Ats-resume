"use client";

import { Info } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import type { ScoreComponent } from "@/lib/types";

interface BarDef {
  key: "keyword_match" | "format_compat" | "section_coverage" | "content_quality";
  label: string;
  outOf: number;
  why: string;
}

const BARS: BarDef[] = [
  {
    key: "keyword_match",
    label: "Keyword Match",
    outOf: 40,
    why: "Compares job-description keywords with the extracted resume text. Exact terms and close semantic equivalents can count as present.",
  },
  {
    key: "format_compat",
    label: "Format Compatibility",
    outOf: 30,
    why: "Checks common parsing risks such as scanned documents, tables, columns, images, unusual fonts, missing contact details, and very short resumes.",
  },
  {
    key: "section_coverage",
    label: "Section Coverage",
    outOf: 15,
    why: "Checks whether the standard summary, experience, education, and skills sections are detected.",
  },
  {
    key: "content_quality",
    label: "Content Quality",
    outOf: 15,
    why: "Scores quantified outcomes, action-verb usage, and whether the extracted resume length is within the scorer's 250-750 word range.",
  },
];

function pointsFor(components: ScoreComponent[], key: BarDef["key"]): number {
  const byName: Record<string, number> = {};
  for (const c of components) byName[c.name] = c.score;
  const weights: Record<BarDef["key"], number> = {
    keyword_match: 0.4,
    format_compat: 0.3,
    section_coverage: 0.15,
    content_quality: 0.15,
  };
  return Math.round((byName[key] ?? 0) * weights[key]);
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
          These are the official production weights used to calculate your overall score. Read the{" "}
          <a href="/methodology" className="text-primary underline">full methodology</a>.
        </p>
      </CardContent>
    </Card>
  );
}
