import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Free ATS Resume Checker — No Signup | ATS Scope",
  description:
    "Upload a PDF or DOCX and paste a job description. Get a free ATS compatibility report with keyword gaps, formatting checks, and rewrites. No signup.",
  alternates: {
    canonical: "https://ats-resumecheck.vercel.app/tool",
  },
};

export default function ToolLayout({ children }: { children: React.ReactNode }) {
  return children;
}
