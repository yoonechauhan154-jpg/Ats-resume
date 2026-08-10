"use client";

import { RotateCcw } from "lucide-react";

import { ScoreCard } from "@/components/results/ScoreCard";
import { ScoreBreakdown } from "@/components/results/ScoreBreakdown";
import { FormatIssuesList } from "@/components/results/FormatIssuesList";
import { MissingKeywordsList } from "@/components/results/MissingKeywordsList";
import { BeforeAfterDiff } from "@/components/results/BeforeAfterDiff";
import { CoverLetterSection } from "@/components/results/CoverLetterSection";
import { ShareableCard } from "@/components/results/ShareableCard";
import { Button } from "@/components/ui/button";
import type { AnalyzeResponse } from "@/lib/types";

export function ResultsPage({
  result,
  jd,
  remaining,
  initialOptimized,
  onReset,
}: {
  result: AnalyzeResponse;
  jd: string;
  remaining?: number | null;
  initialOptimized?: string;
  onReset: () => void;
}) {
  return (
    <section className="space-y-8">
      {/* Meta row */}
      <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
        <span className="rounded-full border px-3 py-1 font-medium text-foreground">
          {result.headline}
        </span>
        <span>·</span>
        <span>Scanned at {new Date(result.scanned_at).toLocaleTimeString()}</span>
        <span>·</span>
        <span>
          {result.resume_word_count} words in resume · {result.jd_word_count} words in JD
        </span>
        {remaining !== null && remaining !== undefined && (
          <>
            <span>·</span>
            <span className={remaining <= 1 ? "font-medium text-destructive" : ""}>
              {remaining} scan{remaining === 1 ? "" : "s"} left today (per IP)
            </span>
          </>
        )}
      </div>

      {/* 1. Score: the most prominent element */}
      <div className="grid gap-6 lg:grid-cols-2">
        <ScoreCard score={result.score.overall} />
        <ScoreBreakdown components={result.score.components} />
      </div>

      {/* 2. Format issues (only if there are any) */}
      {result.format_issues.length > 0 && (
        <FormatIssuesList issues={result.format_issues} summary={result.format_summary} />
      )}

      {/* 3. Biggest opportunity: missing keywords */}
      <MissingKeywordsList missing={result.missing_keywords} present={result.present_keywords} />

      {/* 4. Core differentiator: before/after diff */}
      <BeforeAfterDiff result={result} jd={jd} initialOptimized={initialOptimized} />

      {/* 5. Cover letter */}
      <CoverLetterSection result={result} jd={jd} />

      {/* 6. Viral share card */}
      <ShareableCard result={result} />

      {/* 7. Start over */}
      <div className="flex justify-center pt-2">
        <Button variant="outline" size="lg" onClick={onReset}>
          <RotateCcw className="mr-2 h-4 w-4" /> Optimize for Another Job
        </Button>
      </div>
    </section>
  );
}
