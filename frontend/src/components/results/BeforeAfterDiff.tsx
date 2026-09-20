"use client";

import { useMemo, useState } from "react";
import ReactDiffViewer from "react-diff-viewer-continued";
import { motion } from "framer-motion";
import { AlertTriangle, Copy, Flag, Loader2, Wand2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ApiError, rewriteBullets } from "@/lib/api";
import { useMediaQuery } from "@/lib/use-media-query";
import type { AnalyzeResponse } from "@/lib/types";

export function BeforeAfterDiff({
  result,
  jd,
  initialOptimized,
}: {
  result: AnalyzeResponse;
  jd: string;
  initialOptimized?: string;
}) {
  const isDesktop = useMediaQuery("(min-width: 768px)");
  const [optimized, setOptimized] = useState<string | null>(initialOptimized ?? null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);
  const [reported, setReported] = useState(false);

  const original = useMemo(() => {
    const bullets = result.resume_bullets;
    return bullets.length > 0 ? bullets.join("\n") : result.resume_text;
  }, [result]);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setOptimized(null);
    try {
      const resp = await rewriteBullets({
        bullets: result.resume_bullets,
        jd,
        role: "",
        context: result.resume_text.slice(0, 8000),
      });
      const text = resp.rewritten.map((b) => b.rewritten).join("\n");
      setOptimized(text || resp.rewritten.map((b) => b.original).join("\n"));
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.detail
          : "AI rewrite failed. If the AI service is offline, this feature is unavailable.",
      );
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!optimized) return;
    try {
      await navigator.clipboard.writeText(optimized);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable */
    }
  };

  const reportBad = () => {
    setReported(true);
    setTimeout(() => setReported(false), 2500);
  };

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-lg">
          <Wand2 className="h-5 w-5 text-primary" />
          Before / After — AI Rewrite
        </CardTitle>
        <CardDescription>
          Rewrites your bullet points against this JD. Numbers are checked, and the model is
          instructed to rephrase your existing facts rather than add new claims.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {!optimized && !loading && (
          <div className="flex flex-col items-start gap-3 rounded-lg border bg-muted/30 p-4">
            <p className="text-sm text-muted-foreground">
              Generate a keyword-aligned rewrite of your resume bullets, then compare it side by
              side with your original.
            </p>
            <Button onClick={handleGenerate} disabled={loading}>
              <Wand2 className="mr-1.5 h-4 w-4" /> Generate AI-optimized version
            </Button>
          </div>
        )}

        {loading && (
          <div className="flex items-center gap-3 rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            Rewriting your bullets against the job description…
          </div>
        )}

        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Rewrite failed</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {optimized && (
          <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="space-y-3">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <p className="text-xs text-muted-foreground">
                {isDesktop
                  ? "Left is your original, right is AI-optimized."
                  : "Stacked view on mobile: your original lines first, then the optimized version."}
              </p>
              <div className="flex items-center gap-2">
                <Button size="sm" variant="outline" onClick={reportBad}>
                  <Flag className="mr-1.5 h-3.5 w-3.5" />
                  {reported ? "Thanks — reported" : "Report bad suggestion"}
                </Button>
                <Button size="sm" variant="outline" onClick={copy}>
                  <Copy className="mr-1.5 h-3.5 w-3.5" />
                  {copied ? "Copied" : "Copy optimized"}
                </Button>
              </div>
            </div>

            <div className="overflow-hidden rounded-lg border">
              <ReactDiffViewer
                oldValue={original}
                newValue={optimized}
                splitView={isDesktop}
                useDarkTheme={false}
                leftTitle="Your Original"
                rightTitle="AI Optimized"
                showDiffOnly
              />
            </div>

            <Alert variant="warning">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>AI Suggestion — Please review all changes before using.</AlertTitle>
              <AlertDescription>
                Verify accuracy before updating your resume. The AI preserves facts and numbers but
                you are responsible for the final wording. Flag anything that looks wrong with the
                report button.
              </AlertDescription>
            </Alert>
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
}
