"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Check, Info, Quote } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { categoryLabel } from "@/lib/utils";
import type { KeywordHit } from "@/lib/types";

export function KeywordsPanel({
  missing,
  present,
}: {
  missing: KeywordHit[];
  present: string[];
}) {
  const [openItem, setOpenItem] = useState<string | undefined>(missing[0]?.keyword);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Keyword Match</CardTitle>
        <CardDescription>
          Keywords your resume is missing — with the exact JD context and why each one
          matters. Only add them if you genuinely have that experience.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {missing.length === 0 ? (
          <div className="flex items-center gap-2 rounded-lg border border-success/40 bg-success/5 p-4 text-sm text-success">
            <Check className="h-4 w-4" />
            Every JD keyword we found already appears (exactly or semantically) in your resume.
          </div>
        ) : (
          <Accordion
            type="single"
            collapsible
            value={openItem}
            onValueChange={setOpenItem}
            className="w-full"
          >
            {missing.map((hit, i) => (
              <motion.div
                key={hit.keyword}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.03 }}
              >
                <AccordionItem value={hit.keyword}>
                  <AccordionTrigger className="hover:no-underline">
                    <span className="flex flex-wrap items-center gap-2 text-left">
                      <AlertTriangle className="h-4 w-4 text-warning" />
                      <span className="font-semibold">{hit.keyword}</span>
                      <Badge variant="outline" className="text-xs">
                        {categoryLabel(hit.category)}
                      </Badge>
                    </span>
                  </AccordionTrigger>
                  <AccordionContent>
                    <div className="space-y-3">
                      <div className="rounded-md border-l-2 border-primary bg-muted/40 p-3 text-sm">
                        <span className="mb-1 flex items-center gap-1 text-xs font-medium text-muted-foreground uppercase">
                          <Quote className="h-3 w-3" /> From the job description
                        </span>
                        {hit.context || "This keyword is strongly associated with this role."}
                      </div>
                      <div className="text-sm">
                        <span className="mb-1 flex items-center gap-1 text-xs font-medium text-muted-foreground uppercase">
                          <Info className="h-3 w-3" /> Why it matters
                        </span>
                        <p className="text-muted-foreground">{hit.why_it_matters}</p>
                      </div>
                      <div className="text-sm">
                        <span className="mb-1 flex items-center gap-1 text-xs font-medium text-muted-foreground uppercase">
                          <Check className="h-3 w-3" /> What to do
                        </span>
                        <p className="text-muted-foreground">{hit.suggestion}</p>
                      </div>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </motion.div>
            ))}
          </Accordion>
        )}

        {present.length > 0 && (
          <div>
            <h4 className="mb-2 text-sm font-medium text-muted-foreground">
              Detected in your resume ({present.length})
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
