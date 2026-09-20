import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "ATS Scope Scoring Methodology | How Your Resume Score Works",
  description:
    "See exactly how ATS Scope calculates your resume score: keyword match, format compatibility, section coverage, and content quality, with weights and a worked example.",
  alternates: {
    canonical: "https://ats-resumecheck.vercel.app/methodology",
  },
};

const COMPONENTS = [
  {
    name: "Keyword match",
    weight: "40%",
    explanation:
      "Compares job-description keywords with the extracted resume text. Exact terms and close semantic equivalents can count as present.",
  },
  {
    name: "Format compatibility",
    weight: "30%",
    explanation:
      "Checks for common parsing risks such as scanned documents, tables, columns, images, unusual fonts, very small text, missing contact details, and very short resumes.",
  },
  {
    name: "Section coverage",
    weight: "15%",
    explanation:
      "Checks whether the standard summary, experience, education, and skills sections are detected.",
  },
  {
    name: "Content quality",
    weight: "15%",
    explanation:
      "Scores quantified outcomes, action-verb usage, and whether the extracted resume length is within the scorer's 250-750 word range.",
  },
];

export default function MethodologyPage() {
  return (
    <article className="container max-w-3xl px-4 py-14 md:px-6">
      <header>
        <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">How ATS Scope calculates your score</h1>
        <p className="mt-3 text-muted-foreground sm:text-lg">
          ATS Scope uses a transparent weighted score. Each component is scored from 0 to 100,
          then multiplied by its weight and added to the other components.
        </p>
      </header>

      <section className="mt-10 space-y-6" aria-labelledby="components-heading">
        <h2 id="components-heading" className="text-2xl font-bold tracking-tight">
          The four components
        </h2>
        <div className="divide-y rounded-lg border">
          {COMPONENTS.map((component) => (
            <div key={component.name} className="p-5">
              <div className="flex flex-wrap items-baseline justify-between gap-2">
                <h3 className="font-semibold">{component.name}</h3>
                <span className="font-semibold text-primary">{component.weight}</span>
              </div>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {component.explanation}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section className="mt-10" aria-labelledby="example-heading">
        <h2 id="example-heading" className="text-2xl font-bold tracking-tight">
          Worked example
        </h2>
        <p className="mt-3 leading-relaxed text-muted-foreground">
          Suppose the component scores are keyword match <strong className="text-foreground">80</strong>,
          format compatibility <strong className="text-foreground">90</strong>, section coverage{" "}
          <strong className="text-foreground">75</strong>, and content quality{" "}
          <strong className="text-foreground">70</strong>:
        </p>
        <div className="mt-4 overflow-x-auto rounded-lg border bg-muted/30 p-5 font-mono text-sm leading-7">
          <p>80 x 0.40 = 32.00</p>
          <p>90 x 0.30 = 27.00</p>
          <p>75 x 0.15 = 11.25</p>
          <p>70 x 0.15 = 10.50</p>
          <p className="mt-2 border-t pt-2 font-semibold">Total = 80.75, displayed as 80.8/100</p>
        </div>
        <p className="mt-3 text-sm text-muted-foreground">
          The production scorer rounds the final weighted total to one decimal place.
        </p>
      </section>

      <section className="mt-10" aria-labelledby="limits-heading">
        <h2 id="limits-heading" className="text-2xl font-bold tracking-tight">
          What this score does not mean
        </h2>
        <div className="mt-3 space-y-3 leading-relaxed text-muted-foreground">
          <p>
            This simulates common ATS parsing and matching behavior, not any single vendor&apos;s
            exact algorithm. Different employers configure different systems, fields, ranking
            rules, and review processes.
          </p>
          <p>
            A score is guidance, not a hiring prediction. It cannot account for recruiter judgment,
            competition, role-specific preferences, or whether a claimed qualification is actually
            true. Use recommendations only when they accurately reflect your experience.
          </p>
        </div>
      </section>

      <p className="mt-10 text-sm text-muted-foreground">
        Ready to check a resume? <Link href="/tool" className="text-primary underline">Run a free scan</Link>.
      </p>
    </article>
  );
}