"use client";

import { motion } from "framer-motion";
import { CheckCircle2, Wrench } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import type { FormatIssue } from "@/lib/types";

const SEVERITY_META: Record<string, { label: string; badge: string; dot: string; border: string }> = {
  critical: { label: "HIGH", badge: "text-red-600 dark:text-red-400 border-red-500/40", dot: "bg-red-500", border: "border-l-red-500" },
  warning: { label: "MEDIUM", badge: "text-amber-600 dark:text-amber-400 border-amber-500/40", dot: "bg-amber-500", border: "border-l-amber-500" },
  info: { label: "LOW", badge: "text-blue-600 dark:text-blue-400 border-blue-500/40", dot: "bg-blue-500", border: "border-l-blue-500" },
};

const TYPE_LABELS: Record<string, string> = {
  table: "Table layout",
  columns: "Multi-column layout",
  image: "Image-based content",
  font: "Unusual font",
  scanned: "Scanned document",
  no_text_layer: "No selectable text",
  textbox: "Floating text boxes",
  watermark: "Watermark / background",
  too_short: "Too short",
  missing_contact: "Missing contact info",
};

export function FormatIssuesList({
  issues,
  summary,
}: {
  issues: FormatIssue[];
  summary?: string;
}) {
  if (issues.length === 0) {
    return (
      <Card>
        <CardContent className="flex items-center gap-3 p-5">
          <CheckCircle2 className="h-6 w-6 shrink-0 text-success" />
          <div>
            <p className="font-semibold">No ATS formatting issues found</p>
            <p className="text-sm text-muted-foreground">
              Your layout parses cleanly. {summary || ""}
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-lg">ATS Formatting Issues</CardTitle>
        <CardDescription>
          {summary || "Issues that can break how ATS parses your resume, ordered by severity."}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {issues.map((issue, i) => {
          const meta = SEVERITY_META[issue.severity] ?? SEVERITY_META.info;
          return (
            <motion.div
              key={`${issue.type}-${i}`}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.04 }}
              className={cn(
                "rounded-r-lg border-l-4 bg-card p-4 shadow-sm ring-1 ring-border",
                meta.border,
              )}
            >
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className={cn("h-2.5 w-2.5 rounded-full", meta.dot)} />
                  <span className="font-semibold">{TYPE_LABELS[issue.type] ?? issue.type}</span>
                </div>
                <Badge variant="outline" className={meta.badge}>
                  {meta.label}
                </Badge>
              </div>
              <p className="mt-1.5 text-sm font-medium">{issue.title}</p>
              <p className="mt-0.5 text-sm text-muted-foreground">{issue.description}</p>
              {issue.fix && (
                <p className="mt-2 flex items-start gap-1.5 rounded-md bg-muted/50 p-2 text-sm">
                  <Wrench className="mt-0.5 h-3.5 w-3.5 shrink-0 text-primary" />
                  <span>{issue.fix}</span>
                </p>
              )}
              {issue.ats_impact && (
                <p className="mt-1.5 text-xs italic text-muted-foreground">{issue.ats_impact}</p>
              )}
            </motion.div>
          );
        })}
      </CardContent>
    </Card>
  );
}
