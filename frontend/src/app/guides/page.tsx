import type { Metadata } from "next";
import Link from "next/link";
import { ArrowRight } from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";

export const metadata: Metadata = {
  title: "Guides - ATS Scope",
  description:
    "Practical guides on ATS resume checking: what an ATS resume checker does, the biggest ATS myths, and the 2026 ATS-friendly resume format.",
};

const GUIDES = [
  {
    href: "/guides/what-is-ats-resume-checker",
    title: "What Is an ATS Resume Checker, and Do You Actually Need One?",
    excerpt:
      "What an ATS resume checker does, who benefits most, and why it removes the most common invisible failure point in a job search.",
  },
  {
    href: "/guides/ats-resume-myths",
    title: "5 ATS Resume Myths That Are Costing You Interviews",
    excerpt:
      "The five most repeated ATS resume myths — auto-rejection, keyword stuffing, one-page requirements, creative templates, and the ATS as the villain — and the reality behind each.",
  },
  {
    href: "/guides/ats-resume-format-guide",
    title: "The 2026 ATS-Friendly Resume Format, Explained Simply",
    excerpt:
      "What works and what breaks when an ATS extracts your resume — layout, section headings, file types, and keyword placement.",
  },
];

export default function GuidesIndexPage() {
  return (
    <section className="container max-w-3xl px-4 py-14 md:px-6">
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">Guides</h1>
      <p className="mt-3 text-muted-foreground sm:text-lg">
        Practical, no-fluff guides on surviving ATS screening and getting your resume read the
        way you intended.
      </p>
      <div className="mt-8 space-y-4">
        {GUIDES.map((g) => (
          <Link key={g.href} href={g.href} className="group block">
            <Card className="transition-colors group-hover:border-primary/50">
              <CardContent className="flex items-center justify-between gap-4 p-5">
                <div>
                  <h2 className="font-semibold group-hover:text-primary">{g.title}</h2>
                  <p className="mt-1 text-sm text-muted-foreground">{g.excerpt}</p>
                </div>
                <ArrowRight className="h-5 w-5 shrink-0 text-muted-foreground transition-transform group-hover:translate-x-1 group-hover:text-primary" />
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </section>
  );
}