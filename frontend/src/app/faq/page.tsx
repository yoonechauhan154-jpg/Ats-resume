import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";

import { FAQS } from "@/lib/faqs";

export const metadata: Metadata = {
  title: "ATS Resume Checker FAQ: Scores & Privacy | ATS Scope",
  description:
    "Understand ATS Scope's scores, supported files, privacy practices, and limitations—and how to use resume recommendations responsibly.",
  alternates: {
    canonical: "https://ats-resumecheck.vercel.app/faq",
  },
};

export default function FaqPage() {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: FAQS.map((faq) => ({
      "@type": "Question",
      name: faq.q,
      acceptedAnswer: {
        "@type": "Answer",
        text: faq.a,
      },
    })),
  };

  return (
    <>
      <Script
        id="faq-jsonld"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <section className="container max-w-3xl px-4 py-14 md:px-6">
        <h1 className="text-center text-3xl font-bold tracking-tight sm:text-4xl">
          Frequently asked questions
        </h1>
        <p className="mx-auto mt-3 max-w-2xl text-center text-muted-foreground sm:text-lg">
          Everything you might want to know about ATS resume checking and how ATS Scope works.
        </p>
        <div className="mt-8 space-y-2">
          {FAQS.map((faq) => (
            <details key={faq.q} className="border-b">
              <summary className="cursor-pointer py-4 font-medium">{faq.q}</summary>
              <p className="pb-4 text-sm text-muted-foreground">{faq.a}</p>
              {faq.q === "How is my ATS score calculated?" && (
                <p className="pb-4 text-sm">
                  <Link href="/methodology" className="text-primary underline">
                    Read the full scoring methodology
                  </Link>
                </p>
              )}
            </details>
          ))}
        </div>
      </section>
    </>
  );
}