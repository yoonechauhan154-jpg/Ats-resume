"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, Copy, Loader2, Mail } from "lucide-react";

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { ApiError, generateCoverLetter } from "@/lib/api";
import type { AnalyzeResponse } from "@/lib/types";

export interface CoverLetterPanelProps {
  result: AnalyzeResponse;
  jd: string;
}

export function CoverLetterPanel({ result, jd }: CoverLetterPanelProps) {
  const [company, setCompany] = useState("");
  const [role, setRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [letter, setLetter] = useState<string | null>(null);
  const [warning, setWarning] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setLetter(null);
    setWarning(null);
    try {
      const resp = await generateCoverLetter({
        jd,
        resume_summary: result.resume_text.slice(0, 8000),
        company,
        role,
      });
      setLetter(resp.cover_letter);
      setWarning(resp.warning || null);
    } catch (e) {
      setError(
        e instanceof ApiError
          ? e.detail
          : "Cover letter generation failed. If the AI service is offline, this feature is unavailable.",
      );
    } finally {
      setLoading(false);
    }
  };

  const copy = async () => {
    if (!letter) return;
    try {
      await navigator.clipboard.writeText(letter);
      setCopied(true);
      setTimeout(() => setCopied(false), 1600);
    } catch {
      /* clipboard unavailable */
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-lg">
          <Mail className="h-5 w-5 text-primary" />
          JD-Synced Cover Letter
        </CardTitle>
        <CardDescription>
          Written only from facts in your resume, keyword-aligned to this job. No
          invented experience, ever.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <div>
            <Label htmlFor="company">Company (optional)</Label>
            <Input id="company" value={company} onChange={(e) => setCompany(e.target.value)} placeholder="Acme Inc." />
          </div>
          <div>
            <Label htmlFor="role">Role (optional)</Label>
            <Input id="role" value={role} onChange={(e) => setRole(e.target.value)} placeholder="Senior Software Engineer" />
          </div>
        </div>

        <Button onClick={handleGenerate} disabled={loading}>
          {loading ? (
            <>
              <Loader2 className="animate-spin" /> Writing…
            </>
          ) : (
            <>Generate cover letter</>
          )}
        </Button>

        {error && (
          <Alert variant="destructive">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>{error.includes("offline") ? "AI unavailable" : "Something went wrong"}</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {warning && (
          <Alert variant="warning">
            <AlertTriangle className="h-4 w-4" />
            <AlertTitle>Note</AlertTitle>
            <AlertDescription>{warning}</AlertDescription>
          </Alert>
        )}

        {letter && (
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-xs text-muted-foreground">
                {copied ? "Copied to clipboard" : "Copy it, add your name/contact header, then paste."}
              </p>
              <Button size="sm" variant="outline" onClick={copy}>
                <Copy className="mr-1 h-3.5 w-3.5" /> Copy
              </Button>
            </div>
            <div className="whitespace-pre-wrap rounded-lg border bg-muted/40 p-4 text-sm leading-relaxed">
              {letter}
            </div>
          </motion.div>
        )}
      </CardContent>
    </Card>
  );
}
