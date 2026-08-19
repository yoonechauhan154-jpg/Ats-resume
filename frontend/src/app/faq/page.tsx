import type { Metadata } from "next";
import Script from "next/script";

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { FAQS } from "@/lib/faqs";

export const metadata: Metadata = {
  title: "FAQ - ATS Scope",
  description:
    "Answers about ATS resume checking: what an ATS is, whether resumes get auto-rejected, what causes a poor score, PDF vs DOCX, keyword usage, and how ATS Scope scores your resume.",
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
        <Accordion type="single" collapsible className="mt-8">
          {FAQS.map((faq, i) => (
            <AccordionItem key={faq.q} value={`faq-${i}`}>
              <AccordionTrigger>{faq.q}</AccordionTrigger>
              <AccordionContent className="text-muted-foreground">{faq.a}</AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </section>
    </>
  );
}