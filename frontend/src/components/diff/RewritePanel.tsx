"use client";

import { useMemo, useState } from "react";
import ReactDiffViewer from "react-diff-viewer-continued";
import { motion } from "framer-motion";
import { AlertTriangle, Check, Loader2, ShieldCheck, Wand2 } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { ApiError, rewriteBullets } from "@/lib/api";
import type { AnalyzeResponse, RewriteResponse } from "@/lib/types";

export interface RewritePanelProps {
  result: AnalyzeResponse;
  jd: string;
}

export function RewritePanel({ result, jd }: RewritePanelProps) {
  const initialBullets = useMemo(
    () =>
      result.resume_bullets.length > 0
        ? result.resume_bullets
        : ["Add a bullet here to rewrite it…"],
    [result.resume_bullets],
  );
  const [bullets, setBullets] = useState<string[]>(initialBullets);
  const [selected, setSelected] = useState<Set<number>>(
    () => new Set(initialBullets.map((_, i) => i)),
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [rewrite, setRewrite] = useState<RewriteResponse | null>(null);

  const toggle = (i: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });
  };

  const updateBullet = (i: number, value: string) => {
    setBullets((prev) => prev.map((b, idx) => (idx === i ? value : b)));
  };

  const handleRewrite = async () => {
    const chosen = bullets.filter((_, i) => selected.has(i)).filter((b) => b.trim().length > 5);
    if (chosen.length === 0) {
      setError("Select at least one bullet to rewrite.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const resp = await rewriteBullets({
        bullets: chosen,
        jd,
        role: "",
        context: result.resume_text.slice(0, 6000),
      });
      setRewrite(resp);
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

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Wand2 className="h-5 w-5 text-primary" />
          AI Bullet Rewriter
        </CardTitle>
        <CardDescription>
          Pick the bullets you want aligned to this job description. Every change is
          flagged in the diff; numbers and facts are never altered or invented.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          {bullets.map((b, i) => (
            <div key={i} className="flex items-start gap-2">
              <input
                type="checkbox"
                checked={selected.has(i)}
                onChange={() => toggle(i)}
                className="mt-3 h-4 w-4 accent-primary"
                aria-label={`Select bullet ${i + 1}`}
              />
              <input
                value={b}
                onChange={(e) => updateBullet(i, e.target.value)}
                className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                aria-label={`Bullet ${i + 1}`}
              />
            </div>
          ))}
        </div>

        <div className="flex items-center gap-3">
          <Button onClick={handleRewrite} disabled={loading || selected.size === 0}>
            {loading ? (
              <>
                <Loader2 className="animate-spin" /> Rewriting…
              </>
            ) : (
              <>
                <Wand2 /> Rewrite {selected.size} bullet{selected.size === 1 ? "" : "s"}
              </>
            )}
          </Button>
          <span className="text-xs text-muted-foreground">
            Uses your resume text as the only source of facts.
          </span>
        </div>

        {error && (
          <Alert variant={error.includes("only rephrase") ? "warning" : "destructive"}>
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>{error.includes("offline") ? "AI unavailable" : "Something went wrong"}</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {rewrite && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="space-y-4"
          >
            <Alert variant="success">
              <ShieldCheck className="h-4 w-4" />
              <AlertTitle>Safeguards applied</AlertTitle>
              <AlertDescription>
                <ul className="mt-1 list-disc space-y-1 pl-4">
                  {rewrite.rules_applied.map((r) => (
                    <li key={r}>{r}</li>
                  ))}
                </ul>
                <p className="mt-2 text-xs text-muted-foreground">
                  Model used: {rewrite.model_used}
                </p>
              </AlertDescription>
            </Alert>

            {rewrite.rewritten.map((item, i) => (
              <div key={i} className="rounded-lg border p-4">
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <Badge variant="secondary">Bullet {i + 1}</Badge>
                  {item.preserved.length > 0 && (
                    <Badge variant="outline">
                      <Check className="mr-1 h-3 w-3 text-success" />
                      Kept: {item.preserved.join(", ")}
                    </Badge>
                  )}
                </div>
                <ReactDiffViewer
                  oldValue={item.original}
                  newValue={item.rewritten}
                  splitView={true}
                  useDarkTheme={false}
                  styles={{
                    diffContainer: { fontFamily: "inherit", fontSize: "0.875rem" },
                    contentText: { fontSize: "0.875rem" },
                  }}
                />
                {item.changed.length > 0 && (
                  <div className="mt-3">
                    <p className="text-xs font-medium uppercase text-muted-foreground">
                      What changed
                    </p>
                    <ul className="mt-1 list-disc space-y-0.5 pl-4 text-sm text-muted-foreground">
                      {item.changed.map((c, j) => (
                        <li key={j}>{c}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {item.reason && (
                  <p className="mt-2 text-xs italic text-muted-foreground">{item.reason}</p>
                )}
              </div>
            ))}
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
}
