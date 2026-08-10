import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Analyze Your Resume - ATS Scope",
  description:
    "Paste a job description, upload your resume (PDF/DOCX), and get a transparent 0-100 ATS compatibility score with missing keywords, format issues, and AI rewrites. Free, no signup, resume never stored.",
};

export default function ToolLayout({ children }: { children: React.ReactNode }) {
  return children;
}
