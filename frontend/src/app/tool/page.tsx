"use client";

import { useEffect, useState } from "react";

import { UploadForm } from "@/components/upload/UploadForm";
import { LoadingStep } from "@/components/upload/LoadingStep";
import { ResultsPage } from "@/components/results/ResultsPage";
import { scanResume, ApiError } from "@/lib/api";
import { MOCK_RESULT, MOCK_OPTIMIZED } from "@/lib/mock-data";
import type { AnalyzeResponse } from "@/lib/types";

export default function ToolPage() {
  const [step, setStep] = useState<1 | 2 | 3>(1); // 1: input, 2: loading, 3: results
  const [jdText, setJdText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [results, setResults] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [remaining, setRemaining] = useState<number | null>(null);

  // Dev preview: /tool?mock=1 renders the results page with sample data,
  // so the UI can be tested without a real scan.
  useEffect(() => {
    if (typeof window !== "undefined" && window.location.search.includes("mock=1")) {
      setResults(MOCK_RESULT);
      setStep(3);
    }
  }, []);

  const handleSubmit = async () => {
    if (!resumeFile || jdText.trim().length < 20) return;
    setError(null);
    setStep(2);
    try {
      const { data, remaining } = await scanResume(resumeFile, jdText.trim());
      setResults(data);
      setRemaining(remaining);
      setStep(3);
    } catch (e) {
      setResults(null);
      if (e instanceof ApiError) {
        setError(e.detail || `Request failed (${e.status}).`);
      } else {
        setError("Could not reach the analysis service. Please try again.");
      }
      setStep(1);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
    setStep(1);
  };

  return (
    <div className="container max-w-6xl px-4 py-8 md:px-6 md:py-10">
      {/* Tool header */}
      <header className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight sm:text-3xl">
          Check your resume against a job
        </h1>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          Paste a job description and upload your resume (PDF or DOCX). You get a transparent
          0–100 compatibility score, the exact JD keywords you&apos;re missing, ATS format issues,
          and AI-powered rewrites — all free, no signup.
        </p>
      </header>

      {/* Step 1: input */}
      {step === 1 && (
        <UploadForm
          jd={jdText}
          onJdChange={setJdText}
          file={resumeFile}
          onFileChange={setResumeFile}
          onSubmit={handleSubmit}
          onError={setError}
          error={error}
        />
      )}

      {/* Step 2: loading */}
      {step === 2 && <LoadingStep />}

      {/* Step 3: results */}
      {step === 3 && results && (
        <ResultsPage
          result={results}
          jd={jdText}
          remaining={remaining}
          initialOptimized={jdText ? undefined : MOCK_OPTIMIZED}
          onReset={handleReset}
        />
      )}
    </div>
  );
}
