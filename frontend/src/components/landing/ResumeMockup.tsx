import Link from "next/link";

/* Values mirror the sample report in src/lib/mock-data.ts so the hero visual
   and the mock results page tell the same story. */
const OVERALL_SCORE = 61;

const SCORE_COMPONENTS = [
  { label: "Keywords", value: 40, good: false },
  { label: "Format", value: 87, good: true },
  { label: "Sections", value: 75, good: false },
  { label: "Content", value: 73, good: false },
];

function Mark({ children }: { children: React.ReactNode }) {
  return (
    <mark className="bg-steel-tint px-[2px] text-ink underline decoration-steel decoration-[1.5px] underline-offset-[3px]">
      {children}
    </mark>
  );
}

function Marker({ className = "" }: { className?: string }) {
  return <sup className={`text-[9px] font-semibold leading-none text-steel ${className}`}>1</sup>;
}

function Bullet({ children }: { children: React.ReactNode }) {
  return (
    <li className="flex gap-2">
      <span
        aria-hidden
        className="mt-[0.42em] h-[3px] w-[3px] shrink-0 rounded-full bg-greyblue/60"
      />
      <span>{children}</span>
    </li>
  );
}

export function ResumeMockup() {
  return (
    <figure className="relative mx-auto w-full max-w-[35rem]">
      <p className="sr-only">
        Sample annotated resume. Three matched keywords — REST APIs, PostgreSQL and AWS — are
        underlined. A margin note marks one gap: Kubernetes appears twice in the job description but
        is missing from the resume&apos;s skills list. The match score panel shows {OVERALL_SCORE} out
        of 100, broken into keywords 40, format 87, sections 75 and content 73.
      </p>

      <div aria-hidden className="relative">
        {/* second sheet behind, so this reads as paper rather than a UI card */}
        <div className="absolute inset-0 translate-x-1.5 translate-y-1.5 border border-hairline bg-white/70" />

        <div className="relative border border-hairline bg-white px-5 py-5 sm:px-7 sm:py-6">
          <div className="grid gap-x-7 gap-y-5 md:grid-cols-[minmax(0,1fr)_10.5rem]">
            {/* resume body — identity, summary, experience */}
            <div className="md:col-start-1 md:row-start-1">
              <div className="border-b border-hairline pb-3">
                <p className="font-serif text-[1.125rem] font-semibold tracking-[-0.01em] text-ink">
                  John Smith
                </p>
                <p className="mt-0.5 text-[10px] text-greyblue">
                  Senior Software Engineer · Austin, TX
                </p>
                <p className="mt-0.5 text-[10px] text-greyblue">
                  john.smith@email.com · github.com/jsmith
                </p>
              </div>

              <p className="mt-3 text-[11px] leading-[1.7] text-ink">
                Backend engineer with six years building data-heavy services for freight and
                healthcare platforms, from schema design through deployment.
              </p>

              <div className="mt-4 border-t border-hairline pt-3">
                <p className="text-[10px] font-semibold text-navy">Experience</p>

                <div className="mt-2.5">
                  <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                    <p className="text-[11.5px] font-medium text-ink">Senior Software Engineer</p>
                    <p className="text-[10px] text-greyblue">2021 – present</p>
                  </div>
                  <p className="text-[10px] text-greyblue">Northwind Freight</p>
                  <ul className="mt-1.5 space-y-[5px] text-[11px] leading-[1.6] text-ink">
                    <Bullet>
                      Built and maintained <Mark>REST APIs</Mark> in Python and{" "}
                      <Mark>PostgreSQL</Mark> handling 2M requests a day
                    </Bullet>
                    <Bullet>
                      Moved nightly batch jobs to <Mark>AWS</Mark> and Docker, cutting runtime from 6
                      hours to 90 minutes
                    </Bullet>
                    <Bullet>Led four engineers through a payments migration with no downtime</Bullet>
                  </ul>
                </div>

                <div className="mt-3">
                  <div className="flex flex-wrap items-baseline justify-between gap-x-3">
                    <p className="text-[11.5px] font-medium text-ink">Software Engineer</p>
                    <p className="text-[10px] text-greyblue">2019 – 2021</p>
                  </div>
                  <p className="text-[10px] text-greyblue">Halcyon Health</p>
                  <ul className="mt-1.5 space-y-[5px] text-[11px] leading-[1.6] text-ink">
                    <Bullet>Cut p95 query latency by 40% with indexing and caching</Bullet>
                    <Bullet>Introduced automated release checks, cutting deploy time by 30%</Bullet>
                  </ul>
                </div>
              </div>
            </div>

            {/* match score, integrated into the sheet rather than floating beside it */}
            <div className="border border-hairline bg-steel-tint/40 p-3 md:col-start-2 md:row-start-1 md:self-start">
              <p className="text-[10px] text-greyblue">Match score</p>
              <p className="mt-1 flex items-baseline gap-1">
                <span className="font-serif text-[2rem] font-semibold leading-none text-navy">
                  {OVERALL_SCORE}
                </span>
                <span className="text-[10px] text-greyblue">/ 100</span>
              </p>
              <dl className="mt-3 space-y-2">
                {SCORE_COMPONENTS.map((component) => (
                  <div key={component.label}>
                    <div className="flex items-baseline justify-between gap-2 text-[10px]">
                      <dt className="truncate text-greyblue">{component.label}</dt>
                      <dd
                        className={
                          component.good ? "font-semibold text-success" : "font-medium text-ink"
                        }
                      >
                        {component.value}
                      </dd>
                    </div>
                    <div className="mt-1 h-[3px] w-full bg-white">
                      <div
                        className={component.good ? "h-full bg-success" : "h-full bg-navy"}
                        style={{ width: `${component.value}%` }}
                      />
                    </div>
                  </div>
                ))}
              </dl>
              <p className="mt-3 border-t border-hairline pt-2 text-[9.5px] leading-snug text-greyblue">
                Every component traced to evidence in your file.
              </p>
            </div>

            {/* skills + education — the row the margin note points at */}
            <div className="border-t border-hairline pt-3 md:col-start-1 md:row-start-2">
              <p className="text-[10px] font-semibold text-navy">Skills</p>
              <p className="mt-1.5 text-[11px] leading-[2.1] text-ink">
                Python, SQL, AWS, Docker, PostgreSQL, Git
                <span className="ml-1.5 inline-flex items-center whitespace-nowrap border border-dashed border-greyblue/50 px-1.5 text-[10px] leading-[1.7] text-greyblue">
                  + Kubernetes
                  <Marker className="ml-1" />
                </span>
              </p>
              <p className="mt-2 border-t border-hairline pt-2 text-[10px] text-greyblue">
                B.Sc. Computer Science · University of Texas at Austin
              </p>
            </div>

            {/* margin annotation — an editorial note, not a tooltip */}
            <div className="relative md:col-start-2 md:row-start-2 md:self-start md:border-l md:border-steel/25 md:pl-4">
              <span
                aria-hidden
                className="hidden md:absolute md:-left-4 md:top-[0.5em] md:block md:h-px md:w-4 md:bg-steel/40"
              />
              <p className="text-[10.5px] font-medium leading-snug text-ink">
                <Marker className="mr-1" />
                Kubernetes is not in your resume
              </p>
              <p className="mt-1.5 text-[10.5px] leading-relaxed text-greyblue">
                The posting names it twice, in the deployment section: “Deploy on AWS with Docker and
                Kubernetes.” If your team runs it, add it to Skills and to one deployment bullet.
              </p>
            </div>
          </div>
        </div>
      </div>

      <figcaption className="mt-5 text-xs leading-relaxed text-greyblue">
        Illustrative sample. Underlined phrases are keywords the scan matched; the margin note shows
        how a gap is explained with the sentence it came from.{" "}
        <Link
          href="/methodology"
          className="rounded-sm text-navy underline decoration-steel/40 underline-offset-4 transition-colors hover:decoration-steel focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-steel focus-visible:ring-offset-2"
        >
          How the score is calculated
        </Link>
      </figcaption>
    </figure>
  );
}
