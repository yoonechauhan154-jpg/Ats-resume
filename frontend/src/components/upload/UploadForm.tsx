"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { AlertCircle, CheckCircle2, FileText, Sparkles, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { cn } from "@/lib/utils";

interface UploadFormProps {
  jd: string;
  onJdChange: (value: string) => void;
  file: File | null;
  onFileChange: (file: File | null) => void;
  onSubmit: () => void;
  onError?: (message: string | null) => void;
  error?: string | null;
}

const MAX_MB = 5;

export function UploadForm({
  jd,
  onJdChange,
  file,
  onFileChange,
  onSubmit,
  onError,
  error,
}: UploadFormProps) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      const f = accepted[0];
      if (!f) return;
      if (f.size > MAX_MB * 1024 * 1024) {
        onFileChange(null);
        onError?.(`File is larger than ${MAX_MB}MB. Please compress it first.`);
        return;
      }
      onError?.(null);
      onFileChange(f);
    },
    [onFileChange, onError],
  );

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    },
    maxFiles: 1,
    noClick: true,
  });

  const canSubmit = jd.trim().length >= 20 && file;

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      {/* Resume upload */}
      <div className="flex flex-col gap-3">
        <Label className="text-base">1. Upload your resume</Label>
        <div
          {...getRootProps()}
          className={cn(
            "flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-8 text-center transition-colors cursor-pointer",
            isDragActive
              ? "border-primary bg-primary/5"
              : "border-input hover:border-primary/60 hover:bg-muted/40"
          )}
        >
          <input {...getInputProps()} />
          {file ? (
            <>
              <FileText className="h-8 w-8 text-primary" />
              <div>
                <p className="font-medium break-all">{file.name}</p>
                <p className="text-xs text-muted-foreground">
                  {(file.size / 1024).toFixed(1)} KB · ready to scan
                </p>
              </div>
              <Button
                type="button"
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation();
                  onFileChange(null);
                }}
              >
                <X className="mr-1 h-4 w-4" /> Remove
              </Button>
            </>
          ) : (
            <>
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-primary/10">
                <Sparkles className="h-6 w-6 text-primary" />
              </div>
              <div>
                <p className="font-medium">
                  {isDragActive ? "Drop your resume here" : "Drag & drop your resume"}
                </p>
                <p className="text-sm text-muted-foreground">
                  or <span className="text-primary underline">browse files</span>
                </p>
                <p className="mt-1 text-xs text-muted-foreground">PDF or DOCX · up to {MAX_MB}MB</p>
              </div>
              <Button type="button" variant="outline" size="sm" onClick={open}>
                Choose file
              </Button>
            </>
          )}
        </div>
        <p className="flex items-start gap-1.5 text-xs text-muted-foreground">
          <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-success" />
          Privacy: your file is analyzed in memory and deleted from our server
          immediately after processing. We never store its content.
        </p>
      </div>

      {/* Job description */}
      <div className="flex flex-col gap-3">
        <Label htmlFor="jd" className="text-base">
          2. Paste the job description
        </Label>
        <Textarea
          id="jd"
          value={jd}
          onChange={(e) => onJdChange(e.target.value)}
          placeholder={
            "Paste the full job description here. The more complete it is, the more accurate the keyword analysis.\n\nTip: include the responsibilities and requirements sections."
          }
          className="min-h-[200px] flex-1"
        />
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>{jd.trim().length} characters</span>
          <span className={jd.trim().length > 0 && jd.trim().length < 20 ? "text-destructive" : ""}>
            {jd.trim().length > 0 && jd.trim().length < 20 ? "needs at least 20 chars" : ""}
          </span>
        </div>
      </div>

      {error && (
        <Alert variant="destructive" className="lg:col-span-2">
          <AlertCircle className="h-4 w-4" />
          <AlertTitle>Scan failed</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="lg:col-span-2">
        <Button onClick={onSubmit} disabled={!canSubmit} size="lg" className="w-full sm:w-auto">
          Analyze my resume
        </Button>
        <p className="mt-2 text-xs text-muted-foreground">
          Parsing, keyword extraction, and scoring are fully automatic and free.
        </p>
      </div>
    </div>
  );
}
