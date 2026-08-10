"use client";

import { useRef, useState } from "react";
import { toPng } from "html-to-image";
import { Download, Linkedin, Share2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import { ringColor } from "@/components/results/ScoreCard";
import { formatScore } from "@/lib/utils";
import type { AnalyzeResponse } from "@/lib/types";

function estimatedAfter(result: AnalyzeResponse): number {
  const byName: Record<string, number> = {};
  for (const c of result.score.components) byName[c.name] = c.score;
  const section = byName["section_coverage"] ?? 0;
  const content = byName["content_quality"] ?? 0;
  // If you fix ALL missing keywords (->100) and ALL format issues (->100),
  // the remaining components stay where they are.
  return Math.min(100, Math.round(70 + section * 0.15 + content * 0.15));
}

export function ShareableCard({ result }: { result: AnalyzeResponse }) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [downloading, setDownloading] = useState(false);
  const score = Math.round(result.score.overall);
  const after = estimatedAfter(result);

  const download = async () => {
    if (!cardRef.current) return;
    setDownloading(true);
    try {
      const dataUrl = await toPng(cardRef.current, { pixelRatio: 2, cacheBust: true });
      const a = document.createElement("a");
      a.download = "ats-scope-score-card.png";
      a.href = dataUrl;
      a.click();
    } catch (e) {
      console.error("Failed to export card", e);
    } finally {
      setDownloading(false);
    }
  };

  const shareLinkedIn = () => {
    const url = encodeURIComponent(window.location.href);
    window.open(
      `https://www.linkedin.com/sharing/share-offsite/?url=${url}`,
      "_blank",
      "noopener,noreferrer",
    );
  };

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 text-lg font-semibold">
          <Share2 className="h-5 w-5 text-primary" /> Share your progress
        </h2>
      </div>

      <div
        ref={cardRef}
        className="relative overflow-hidden rounded-2xl border border-primary/20 bg-gradient-to-br from-primary/15 via-card to-emerald-500/10 p-6 sm:p-8"
      >
        <div className="flex items-center justify-between text-xs font-semibold tracking-wide text-muted-foreground">
          <span>ATS SCOPE</span>
          <span className="rounded-full border border-primary/30 px-2 py-0.5">100% FREE</span>
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm font-medium text-muted-foreground">My resume ATS score</p>
          <div className="mt-2 flex items-center justify-center gap-4">
            <div className="relative flex h-28 w-28 items-center justify-center">
              <svg viewBox="0 0 120 120" className="h-full w-full -rotate-90">
                <circle cx="60" cy="60" r="52" fill="none" stroke="hsl(var(--muted))" strokeWidth="10" />
                <circle
                  cx="60"
                  cy="60"
                  r="52"
                  fill="none"
                  stroke={ringColor(score)}
                  strokeWidth="10"
                  strokeLinecap="round"
                  strokeDasharray={2 * Math.PI * 52}
                  strokeDashoffset={2 * Math.PI * 52 * (1 - score / 100)}
                />
              </svg>
              <span className="absolute text-4xl font-bold" style={{ color: ringColor(score) }}>
                {formatScore(score)}
              </span>
            </div>
            <div className="text-left">
              <span className="block text-xs text-muted-foreground">after applying fixes</span>
              <span className="block text-3xl font-bold text-emerald-600 dark:text-emerald-400">
                {formatScore(after)}
              </span>
              <span className="block text-xs text-muted-foreground">/ 100 (estimated)</span>
            </div>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-muted-foreground">
          atsscope.app · free ATS resume checker · resume never stored
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <Button variant="outline" onClick={shareLinkedIn}>
          <Linkedin className="mr-1.5 h-4 w-4 text-[#0a66c2]" /> Share on LinkedIn
        </Button>
        <Button variant="outline" onClick={download} disabled={downloading}>
          <Download className="mr-1.5 h-4 w-4" />
          {downloading ? "Preparing…" : "Download image"}
        </Button>
        <p className="w-full text-xs text-muted-foreground sm:w-auto">
          LinkedIn needs the image, not a link — download it and attach it to your post.
        </p>
      </div>
    </section>
  );
}
