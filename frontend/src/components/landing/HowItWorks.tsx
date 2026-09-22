/* The three real inputs the product takes. No placeholder "step 1/2/3" copy:
   each line names what the tool actually does, including its real limits. */
const STEPS = [
  {
    title: "Add your resume",
    body: "Upload a PDF or DOCX, or paste the text. The file is parsed in memory and deleted from the server as soon as the scan finishes, so nothing is kept between visits.",
    meta: "PDF or DOCX · 5 MB maximum · a text-based PDF parses most cleanly",
  },
  {
    title: "Paste the job description",
    body: "Copy the posting as it was written — responsibilities and requirements included. Keywords are extracted from the employer's own wording, so paraphrasing the advert weakens the comparison.",
    meta: "At least 20 characters · the full posting gives the most accurate read",
  },
  {
    title: "Read the keyword and formatting analysis",
    body: "You get a weighted 0–100 score, the JD keywords your resume never mentions with the sentence each came from, the format problems that stop parsers reading your file, and a rewrite you can compare line by line.",
    meta: "One report · score, keywords, format flags, rewrites, cover letter",
  },
];

export function HowItWorks() {
  return (
    <section id="how-it-works" className="scroll-mt-20 border-b border-hairline bg-white">
      <div className="container max-w-6xl px-4 py-16 md:px-6 md:py-20">
        <div className="grid gap-10 lg:grid-cols-[minmax(0,20rem)_minmax(0,1fr)] lg:gap-16">
          <div className="lg:sticky lg:top-24 lg:self-start">
            <h2 className="font-serif text-[1.875rem] font-semibold leading-[1.15] tracking-[-0.018em] text-navy sm:text-[2.125rem]">
              How a scan runs
            </h2>
            <p className="mt-4 max-w-[38ch] text-[0.9375rem] leading-relaxed text-greyblue">
              Three inputs, one report. Nothing is sent to a recruiter, and no account is created
              along the way — the steps below are the whole workflow.
            </p>
          </div>

          <ol className="border-t border-hairline">
            {STEPS.map((step, index) => (
              <li
                key={step.title}
                className="grid gap-2 border-b border-hairline py-7 first:pt-7 sm:grid-cols-[2.5rem_minmax(0,1fr)] sm:gap-6"
              >
                <span aria-hidden className="font-serif text-2xl font-semibold leading-none text-steel/70">
                  {index + 1}
                </span>
                <div>
                  <h3 className="font-serif text-xl font-semibold tracking-[-0.01em] text-navy">
                    {step.title}
                  </h3>
                  <p className="mt-2.5 max-w-[58ch] text-[0.9375rem] leading-relaxed text-greyblue">
                    {step.body}
                  </p>
                  <p className="mt-3 max-w-[58ch] border-l border-hairline pl-3 text-xs leading-relaxed text-greyblue">
                    {step.meta}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </div>
    </section>
  );
}
