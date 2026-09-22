import Link from "next/link";

/* Real weights from the scorer: keyword match 40, format 30, sections 15,
   content 15 (see docs/DEPLOYMENT.md and /methodology). */
const COMPONENTS = [
  {
    name: "Keyword match",
    weight: "40%",
    detail:
      "The share of the job description's keywords your resume actually contains — exact terms plus close semantic equivalents, counted against the employer's wording.",
  },
  {
    name: "Format compatibility",
    weight: "30%",
    detail:
      "Tables, columns, images, scanned pages, unusual fonts and missing contact details: the structures that make a parser read your resume as noise.",
  },
  {
    name: "Section coverage",
    weight: "15%",
    detail:
      "Whether summary, experience, education and skills are present and detectable under headings a parser recognises.",
  },
  {
    name: "Content quality",
    weight: "15%",
    detail:
      "Quantified outcomes, action verbs and bullet length balance — the difference between a duty list and a record of results.",
  },
];

export function ReportContents() {
  return (
    <section className="border-b border-hairline">
      <div className="container max-w-6xl px-4 py-16 md:px-6 md:py-20">
        <div className="max-w-[62ch]">
          <h2 className="font-serif text-[1.875rem] font-semibold leading-[1.15] tracking-[-0.018em] text-navy sm:text-[2.125rem]">
            What the report measures, and how much it counts
          </h2>
          <p className="mt-4 text-[0.9375rem] leading-relaxed text-greyblue">
            The overall score is a weighted average of four components. Each one is shown separately,
            so you can see which lever is worth pulling before you rewrite anything.
          </p>
        </div>

        <dl className="mt-10 border-t border-hairline">
          <div className="hidden border-b border-hairline pb-3 text-xs text-greyblue md:grid md:grid-cols-[minmax(0,13rem)_minmax(0,1fr)_4rem] md:gap-8">
            <dt>Component</dt>
            <dd>What it measures</dd>
            <dd className="text-right">Weight</dd>
          </div>
          {COMPONENTS.map((component) => (
            <div
              key={component.name}
              className="grid gap-2 border-b border-hairline py-6 md:grid-cols-[minmax(0,13rem)_minmax(0,1fr)_4rem] md:gap-8 md:py-7"
            >
              <dt className="text-[0.9375rem] font-medium leading-snug text-ink">
                {component.name}
              </dt>
              <dd className="max-w-[58ch] text-[0.9375rem] leading-relaxed text-greyblue">
                {component.detail}
              </dd>
              <dd className="font-serif text-xl font-semibold leading-none text-navy md:text-right">
                {component.weight}
              </dd>
            </div>
          ))}
        </dl>

        <div className="mt-8 grid gap-6 md:grid-cols-[minmax(0,1fr)_auto] md:items-start md:gap-16">
          <p className="max-w-[62ch] text-[0.9375rem] leading-relaxed text-greyblue">
            Every deduction in the report maps back to evidence: the exact job-description sentence, a
            detected layout problem, a missing section, or an unquantified bullet. The same screen
            also rewrites weak bullets with a before-and-after diff and drafts a cover letter limited
            to facts already in your resume.
          </p>
          <Link
            href="/methodology"
            className="rounded-sm text-sm font-medium text-navy underline decoration-steel/40 underline-offset-[6px] transition-colors hover:decoration-steel focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-steel focus-visible:ring-offset-2 focus-visible:ring-offset-paper md:justify-self-end md:whitespace-nowrap"
          >
            Read the scoring methodology
          </Link>
        </div>
      </div>
    </section>
  );
}
