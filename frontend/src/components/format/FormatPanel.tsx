"use client";

import { motion } from "framer-motion";
import { FileWarning, Wrench } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn, severityStyles } from "@/lib/utils";
import type { FormatIssue } from "@/lib/types";

const SEVERITY_LABEL: Record<string, string> = {
  critical: "Critical",
  warning: "Warning",
  info: "Info",
};

export function FormatPanel({
  issues,
  summary,
}: {
  issues: FormatIssue[];
  summary: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <FileWarning className="h-5 w-5 text-warning" />
          Format & ATS Parsing Issues
        </CardTitle>
        <CardDescription>
          {summary || "Issues that can prevent ATS software from extracting your text correctly."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {issues.length === 0 ? (
          <p className="rounded-lg border border-success/40 bg-success/5 p-4 text-sm text-success">
            No format red flags detected. Your resume looks ATS-friendly.
          </p>
        ) : (
          issues.map((issue, i) => {
            const s = severityStyles(issue.severity);
            return (
              <motion.div
                key={`${issue.type}-${i}`}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.04 }}
                className={cn("rounded-lg border p-4", s.border, s.bg)}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex items-start gap-2">
                    <span className={cn("mt-1.5 h-2 w-2 shrink-0 rounded-full", s.dot)} />
                    <div>
                      <h4 className={cn("font-medium", s.text)}>{issue.title}</h4>
                      <p className="mt-1 text-sm text-muted-foreground">{issue.description}</p>
                    </div>
                  </div>
                  <Badge
                    variant={
                      issue.severity === "critical"
                        ? "destructive"
                        : issue.severity === "warning"
                          ? "warning"
                          : "secondary"
                    }
                    className="shrink-0"
                  >
                    {SEVERITY_LABEL[issue.severity] ?? issue.severity}
                  </Badge>
                </div>

                <div className="mt-3 grid gap-3 text-sm sm:grid-cols-2">
                  <div className="rounded-md bg-background/60 p-3">
                    <span className="text-xs font-medium uppercase text-muted-foreground">
                      How it affects ATS
                    </span>
                    <p className="mt-1">{issue.ats_impact}</p>
                  </div>
                  <div className="rounded-md bg-background/60 p-3">
                    <span className="flex items-center gap-1 text-xs font-medium uppercase text-muted-foreground">
                      <Wrench className="h-3 w-3" /> Fix
                    </span>
                    <p className="mt-1">{issue.fix}</p>
                  </div>
                </div>
              </motion.div>
            );
          })
        )}
      </CardContent>
    </Card>
  );
}
