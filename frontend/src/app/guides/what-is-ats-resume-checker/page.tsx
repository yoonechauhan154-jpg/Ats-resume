import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";

export const metadata: Metadata = {
  title: "What Is an ATS Resume Checker? Uses & Limits",
  description:
    "Learn what ATS resume checkers measure, how job matching differs from parsing, and why a checker score cannot predict a hiring decision.",
  alternates: {
    canonical: "https://ats-resumecheck.vercel.app/guides/what-is-ats-resume-checker",
  },
};

export default function WhatIsAtsResumeCheckerPage() {
  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: "https://ats-resumecheck.vercel.app/" },
      { "@type": "ListItem", position: 2, name: "Guides", item: "https://ats-resumecheck.vercel.app/guides" },
      { "@type": "ListItem", position: 3, name: "What Is an ATS Resume Checker?", item: "https://ats-resumecheck.vercel.app/guides/what-is-ats-resume-checker" },
    ],
  };

  return (
    <>
      <Script id="guide-breadcrumb-jsonld" type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }} />
      <article className="container max-w-3xl px-4 py-14 md:px-6">
        <nav aria-label="Breadcrumb" className="mb-6 text-sm text-muted-foreground">
          <ol className="flex flex-wrap items-center gap-2">
            <li><Link href="/" className="hover:text-foreground">Home</Link></li>
            <li aria-hidden="true">&gt;</li>
            <li><Link href="/guides" className="hover:text-foreground">Guides</Link></li>
            <li aria-hidden="true">&gt;</li>
            <li aria-current="page">What Is an ATS Resume Checker?</li>
          </ol>
        </nav>
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
        What Is an ATS Resume Checker, and Do You Actually Need One?
      </h1>
      <div className="mt-6 space-y-4 leading-relaxed text-muted-foreground">
        <p>
          If you&apos;ve applied to dozens of jobs and heard nothing back, you&apos;ve probably
          seen the advice: &quot;run your resume through an ATS checker first.&quot; But what
          does that actually mean?
        </p>
        <p>
          An Applicant Tracking System (ATS) is software companies use to manage job
          applications. When you submit a resume, the ATS extracts your contact details, work
          history, education, and skills into a structured record, then ranks how well that
          record matches the job description. Nearly all large companies use one — it&apos;s
          less about rejecting people and more about helping recruiters sort through hundreds
          of applications.
        </p>
        <p>
          An ATS resume checker simulates part of that process. You upload your resume and
          paste in a job description, and the tool shows you: which keywords from the posting
          are missing, whether your formatting will parse cleanly, and how complete your
          sections are. The goal isn&apos;t to &quot;trick&quot; the software — it&apos;s to
          make sure the system reads your real qualifications correctly, instead of losing
          them to a formatting quirk or missing keyword.
        </p>
        <p>
          Who benefits most from checking their resume this way? Career switchers translating
          old experience into new industry language. Freshers who don&apos;t yet know which
          keywords recruiters search for. Anyone applying to multiple roles who needs to
          quickly confirm their resume is still aligned after tailoring it.
        </p>
        <p>
          A good checker won&apos;t guarantee an interview — no tool can do that. But it
          removes one of the most common, invisible failure points in a job search: a strong
          candidate whose resume simply never gets read the way they intended.
        </p>
      </div>
      </article>
    </>
  );
}