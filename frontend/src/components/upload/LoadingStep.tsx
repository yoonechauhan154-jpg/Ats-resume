"use client";

import { useEffect, useState } from "react";
import { Loader2 } from "lucide-react";

import { Progress } from "@/components/ui/progress";

const STAGES = [
  "Parsing your resume…",
  "Extracting job-description keywords…",
  "Comparing keywords and resume sections…",
  "Checking ATS formatting…",
  "Building your report…",
];

export function LoadingStep() {
  const [stage, setStage] = useState(0);
  const [progress, setProgress] = useState(8);

  useEffect(() => {
    const timer = setInterval(() => {
      setProgress((p) => (p >= 95 ? p : Math.min(95, p + 4 + Math.random() * 6)));
    }, 600);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const timer = setInterval(() => {
      setStage((s) => Math.min(STAGES.length - 1, s + 1));
    }, 1600);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center gap-5 rounded-xl border bg-card p-10 text-center">
      <Loader2 className="h-10 w-10 animate-spin text-primary" />
      <div>
        <p className="text-lg font-semibold">Analyzing your resume</p>
        <p className="mt-1 text-sm text-muted-foreground">{STAGES[stage]}</p>
      </div>
      <Progress value={progress} className="w-full max-w-md" />
      <p className="text-xs text-muted-foreground">
        Usually takes a few seconds. Your file is processed in memory and never stored.
      </p>
    </div>
  );
}
