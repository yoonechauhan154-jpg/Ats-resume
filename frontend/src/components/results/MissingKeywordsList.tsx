"use client";

import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Check, Quote, TrendingUp, AlertTriangle } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import type { KeywordHit } from "@/lib/types";

const IMPORTANCE_META: Record<string, { label: string; className: string }> = {
  HIGH: {
    label: "HIGH priority",
    className: "bg-red-500/15 text-red-600 dark:text-red-400 border-red-500/40",
  },
  MEDIUM: {
    label: "MEDIUM priority",
    className: "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/40",
  },
  LOW: {
    label: "LOW priority",
    className: "bg-blue-500/15 text-blue-600 dark:text-blue-400 border-blue-500/40",
  },
};

const IMPORTANCE_ORDER: Record<string, number> = { HIGH: 0, MEDIUM: 1, LOW: 2 };

function importanceMeta(imp: string) {
  return IMPORTANCE_META[imp] ?? IMPORTANCE_META.MEDIUM;
}

export function MissingKeywordsList({
  missing,
  present,
}: {
  missing: KeywordHit[];
  present: string[];
}) {
  const sorted = useMemo(
    () =>
      [...missing].sort(
        (a, b) =>
          (IMPORTANCE_ORDER[a.importance] ?? 1) - (IMPORTANCE_ORDER[b.importance] ?? 1) ||
          b.jd_frequency - a.jd_frequency,
      ),
    [missing],
  );

  const [openItem, setOpenItem] = useState<string | undefined>(sorted[0]?.keyword);

  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="flex items-center gap-2 text-lg">
          <TrendingUp className="h-5 w-5 text-primary" />
          Missing Keywords — Your Biggest Opportunity
        </CardTitle>
        <CardDescription>
          Exact terms from this JD that your resume doesn&apos;t contain. Add them only if you
          genuinely have the experience — honesty beats keyword-stuffing.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {sorted.length === 0 ? (
          <div className="flex items-center gap-2 rounded-lg border border-success/40 bg-success/5 p-4 text-sm text-success">
            <Check className="h-4 w-4" />
            Every JD keyword we found already appears in your resume.
          </div>
        ) : (
          <Accordion
            type="single"
            collapsible
            value={openItem}
            onValueChange={setOpenItem}
            className="w-full"
          >
            {sorted.map((hit, i) => {
              const meta = importanceMeta(hit.importance);
              return (
                <motion.div
                  key={hit.keyword}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.03 }}
                >
                  <AccordionItem value={hit.keyword}>
                    <AccordionTrigger className="hover:no-underline">
                      <span className="flex flex-1 flex-wrap items-center gap-2 text-left">
                        <AlertTriangle className="h-4 w-4 shrink-0 text-warning" />
                        <span className="font-semibold">{hit.keyword}</span>
                        <Badge variant="outline" className={meta.className}>
                          {meta.label}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          Mentioned {hit.jd_frequency}x in JD
                        </span>
                      </span>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="space-y-3">
                        <div className="rounded-md border-l-2 border-primary bg-muted/40 p-3 text-sm">
                          <span className="mb-1 flex items-center gap-1 text-xs font-medium uppercase text-muted-foreground">
                            <Quote className="h-3 w-3" /> From the job description
                          </span>
                          <p className="italic">&ldquo;{hit.context || "—"}&rdquo;</p>
                        </div>
                        <div className="text-sm">
                          <p className="mb-1 text-xs font-medium uppercase text-muted-foreground">
                            Why it matters
                          </p>
                          <p className="text-muted-foreground">{hit.why_it_matters}</p>
                        </div>
                        <div className="rounded-md bg-primary/5 p-3 text-sm">
                          <p className="mb-1 text-xs font-medium uppercase text-primary">
                            How to add it naturally
                          </p>
                          <p className="text-muted-foreground">{hit.suggestion}</p>
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </motion.div>
              );
            })}
          </Accordion>
        )}

        {present.length > 0 && (
          <div>
            <h4 className="mb-2 text-sm font-medium text-muted-foreground">
              Already in your resume ({present.length})
            </h4>
            <div className="flex flex-wrap gap-1.5">
              {present.map((k) => (
                <Badge key={k} variant="success" className="text-xs font-normal">
                  <Check className="mr-1 h-3 w-3" />
                  {k}
                </Badge>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
