import type { Metadata } from "next";

import { ScoreCard } from "@/components/results/ScoreCard";
import { ScoreBreakdown } from "@/components/results/ScoreBreakdown";
import { FormatIssuesList } from "@/components/results/FormatIssuesList";
import { MissingKeywordsList } from "@/components/results/MissingKeywordsList";
import { BeforeAfterDiff } from "@/components/results/BeforeAfterDiff";
import { CoverLetterSection } from "@/components/results/CoverLetterSection";
import { ShareableCard } from "@/components/results/ShareableCard";
import { MOCK_RESULT, MOCK_OPTIMIZED } from "@/lib/mock-data";

export const metadata: Metadata = {
  title: "Component Preview - ATS Scope",
  robots: { index: false },
  alternates: {
    canonical: "https://ats-resumecheck.vercel.app/preview",
  },
};

export default function PreviewPage() {
  return (
    <div className="container max-w-6xl space-y-8 px-4 py-10 md:px-6">
      <p className="rounded-md border bg-muted/40 p-2 text-xs text-muted-foreground">
        Dev preview: renders every results component with mock data. Not indexed.
      </p>

      <div className="grid gap-6 lg:grid-cols-2">
        <ScoreCard score={MOCK_RESULT.score.overall} />
        <ScoreBreakdown components={MOCK_RESULT.score.components} />
      </div>

      <FormatIssuesList issues={MOCK_RESULT.format_issues} summary={MOCK_RESULT.format_summary} />
      <MissingKeywordsList missing={MOCK_RESULT.missing_keywords} present={MOCK_RESULT.present_keywords} />
      <BeforeAfterDiff result={MOCK_RESULT} jd={""} initialOptimized={MOCK_OPTIMIZED} />
      <CoverLetterSection result={MOCK_RESULT} jd={""} />
      <ShareableCard result={MOCK_RESULT} />
    </div>
  );
}
