import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";

export const metadata: Metadata = {
  title: "ATS-Friendly Resume Format: Examples & Checklist",
  description:
    "Check resume layout, headings, reading order, and PDF or DOCX output. Use worked examples and a practical formatting checklist.",
  alternates: {
    canonical: "https://ats-resumecheck.vercel.app/guides/ats-resume-format-guide",
  },
};

export default function AtsResumeFormatGuidePage() {
  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: "https://ats-resumecheck.vercel.app/" },
      { "@type": "ListItem", position: 2, name: "Guides", item: "https://ats-resumecheck.vercel.app/guides" },
      { "@type": "ListItem", position: 3, name: "ATS-Friendly Resume Format", item: "https://ats-resumecheck.vercel.app/guides/ats-resume-format-guide" },
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
            <li aria-current="page">ATS-Friendly Resume Format</li>
          </ol>
        </nav>
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
        The 2026 ATS-Friendly Resume Format, Explained Simply
      </h1>
      <div className="mt-6 space-y-4 leading-relaxed text-muted-foreground">
        <p>
          Format matters because an ATS doesn&apos;t &quot;read&quot; your resume like a
          human — it extracts text into fields. If the layout confuses that extraction, real
          experience can disappear from your application entirely.
        </p>
        <p>
          <span className="font-semibold text-foreground">What works:</span> A single-column
          layout with standard section headings (&quot;Work Experience,&quot; &quot;Education,&quot;
          &quot;Skills&quot; — not creative alternatives). Reverse-chronological order for
          jobs. Contact details in the main body of the document, not in a header or footer
          (some parsers skip those entirely). Text-based PDF or DOCX, never a scanned image.
        </p>
        <p>
          <span className="font-semibold text-foreground">What breaks parsing:</span> Tables
          and multi-column layouts, since the system can&apos;t always determine reading
          order. Icons or graphics used to represent skill levels — they carry no readable
          text. Skills or experience hidden inside text boxes, since many parsers only extract
          content from the main text flow.
        </p>
        <p>
          <span className="font-semibold text-foreground">On keywords:</span> match the job
          description&apos;s exact phrasing where it&apos;s accurate to your experience, and
          include both the abbreviation and full term once (e.g., &quot;CRM&quot; and
          &quot;Customer Relationship Management&quot;) since different systems search for
          different forms. Place your strongest, most relevant keywords in your summary and
          the first bullet under each role — some systems weight early placement more heavily.
        </p>
        <p>
          <span className="font-semibold text-foreground">The bottom line:</span> ATS-friendly
          formatting isn&apos;t about tricking software. A clean, well-structured resume is
          also easier for the human recruiter to skim once it gets through — the same rules
          serve both readers.
        </p>
      </div>
      </article>
    </>
  );
}