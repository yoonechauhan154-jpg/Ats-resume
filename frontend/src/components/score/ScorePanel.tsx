"use client";

import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Info } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Badge } from "@/components/ui/badge";
import { scoreRing, formatScore, cn } from "@/lib/utils";
import type { AnalyzeResponse, ScoreBreakdown } from "@/lib/types";

const COMPONENT_LABELS: Record<string, string> = {
  keyword_match: "Keyword match",
  format_compat: "Format compatibility",
  section_coverage: "Section coverage",
  content_quality: "Content quality",
};

export function ScorePanel({ result }: { result: AnalyzeResponse }) {
  const { score } = result;
  const gaugeData = [{ name: "overall", value: score.overall, fill: scoreRing(score.overall) }];

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <CardTitle className="text-lg">ATS Compatibility Score</CardTitle>
          <Badge variant={score.overall >= 80 ? "success" : score.overall >= 60 ? "warning" : "destructive"}>
            {score.overall >= 80 ? "Strong" : score.overall >= 60 ? "Good" : "Needs work"}
          </Badge>
        </div>
        <CardDescription>{result.headline}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center gap-6 md:flex-row md:items-start">
          {/* Gauge */}
          <div className="relative h-44 w-44 shrink-0">
            <ResponsiveContainer width="100%" height="100%">
              <RadialBarChart
                innerRadius="72%"
                outerRadius="100%"
                data={gaugeData}
                startAngle={225}
                endAngle={-45}
              >
                <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
                <RadialBar dataKey="value" cornerRadius={10} background={{ fill: "hsl(var(--muted))" }}>
                  {gaugeData.map((d, i) => (
                    <Cell key={i} fill={d.fill} />
                  ))}
                </RadialBar>
              </RadialBarChart>
            </ResponsiveContainer>
            <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
              <span className={cn("text-4xl font-bold", "text-foreground")}>{formatScore(score.overall)}</span>
              <span className="text-xs text-muted-foreground">/ 100</span>
            </div>
          </div>

          {/* Breakdown */}
          <div className="w-full flex-1 space-y-4">
            {score.components.map((c) => (
              <div key={c.name}>
                <div className="mb-1 flex items-center justify-between text-sm">
                  <span className="flex items-center gap-1.5 font-medium">
                    {COMPONENT_LABELS[c.name] ?? c.name}
                    <TooltipProvider delayDuration={100}>
                      <Tooltip>
                        <TooltipTrigger asChild>
                          <span className="cursor-help text-muted-foreground">
                            <Info className="h-3.5 w-3.5" />
                          </span>
                        </TooltipTrigger>
                        <TooltipContent className="max-w-xs">
                          {c.details.join(" ")}
                          <span className="mt-1 block text-xs text-muted-foreground">
                            Weight: {Math.round(c.weight * 100)}%
                          </span>
                        </TooltipContent>
                      </Tooltip>
                    </TooltipProvider>
                  </span>
                  <span className="tabular-nums text-muted-foreground">
                    {formatScore(c.score)}
                    <span className="ml-1 text-xs">/100</span>
                  </span>
                </div>
                <Progress value={c.score} className={cn("h-2.5")} />
              </div>
            ))}

            <p className="flex items-start gap-1.5 rounded-md bg-muted/50 p-2.5 text-xs text-muted-foreground">
              <Info className="mt-0.5 h-3.5 w-3.5 shrink-0" />
              {score.methodology}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
