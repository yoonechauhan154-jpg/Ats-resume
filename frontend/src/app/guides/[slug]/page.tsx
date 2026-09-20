import type { Metadata } from "next";
import Link from "next/link";
import Script from "next/script";

import { SEO_GUIDE_ARTICLES } from "@/lib/seo-guide-articles";
import { SEO_GUIDE_BY_SLUG, SEO_GUIDES } from "@/lib/seo-guides";

const BASE_URL = "https://ats-resumecheck.vercel.app";

type GuidePageProps = {
  params: { slug: string };
};

export function generateStaticParams() {
  return SEO_GUIDES.map(({ slug }) => ({ slug }));
}

export function generateMetadata({ params }: GuidePageProps): Metadata {
  const guide = SEO_GUIDE_BY_SLUG[params.slug];
  if (!guide) return {};
  return {
    title: `${guide.title} | ATS Scope`,
    description: guide.description,
    alternates: { canonical: `${BASE_URL}/guides/${guide.slug}` },
  };
}

export default function SeoGuidePage({ params }: GuidePageProps) {
  const guide = SEO_GUIDE_BY_SLUG[params.slug];
  if (!guide) return null;
  const articleSections = SEO_GUIDE_ARTICLES[guide.slug];

  const breadcrumbJsonLd = {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: [
      { "@type": "ListItem", position: 1, name: "Home", item: `${BASE_URL}/` },
      { "@type": "ListItem", position: 2, name: "Guides", item: `${BASE_URL}/guides` },
      { "@type": "ListItem", position: 3, name: guide.title, item: `${BASE_URL}/guides/${guide.slug}` },
    ],
  };

  return (
    <>
      <Script
        id="seo-guide-breadcrumb-jsonld"
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(breadcrumbJsonLd) }}
      />
      <article className="container max-w-3xl px-4 py-14 md:px-6">
        <nav aria-label="Breadcrumb" className="mb-6 text-sm text-muted-foreground">
          <ol className="flex flex-wrap items-center gap-2">
            <li><Link href="/" className="hover:text-foreground">Home</Link></li>
            <li aria-hidden="true">&gt;</li>
            <li><Link href="/guides" className="hover:text-foreground">Guides</Link></li>
            <li aria-hidden="true">&gt;</li>
            <li aria-current="page">{guide.title}</li>
          </ol>
        </nav>
        <header>
          <p className="text-sm font-medium text-primary">Resume guide</p>
          <h1 className="mt-2 text-3xl font-bold tracking-tight sm:text-4xl">{guide.title}</h1>
          <p className="mt-4 text-lg leading-relaxed text-muted-foreground">{guide.summary}</p>
        </header>
        <div className="mt-8 space-y-6 leading-relaxed">
          {articleSections ? articleSections.map((section) => (
            <section key={section.heading}>
              <h2 className="text-2xl font-bold tracking-tight">{section.heading}</h2>
              <div className="mt-3 space-y-4 text-muted-foreground">
                {section.paragraphs.map((paragraph) => <p key={paragraph}>{paragraph}</p>)}
              </div>
            </section>
          )) : (
            <section>
              <h2 className="text-2xl font-bold tracking-tight">What to check</h2>
              <ul className="mt-4 list-disc space-y-3 pl-5 text-muted-foreground">
                {guide.points.map((point) => <li key={point}>{point}</li>)}
              </ul>
            </section>
          )}
          <section className="rounded-lg border bg-muted/30 p-5">
            <h2 className="text-xl font-semibold tracking-tight">A practical next step</h2>
            <p className="mt-2 text-muted-foreground">
              Compare your resume with the specific job description, make only accurate changes,
              and check the result before you submit. ATS Scope can show keyword gaps, format
              issues, section coverage, and content-quality signals in one report.
            </p>
            <Link href="/tool" className="mt-4 inline-block text-primary underline">
              Check your resume against a job
            </Link>
          </section>
        </div>
      </article>
    </>
  );
}
