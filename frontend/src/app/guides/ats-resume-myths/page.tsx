import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "5 ATS Resume Myths That Are Costing You Interviews",
  description:
    "The five most repeated ATS resume myths — auto-rejection, keyword stuffing, one-page requirements, creative templates, and the ATS as the villain — and the reality behind each.",
};

const MYTHS = [
  {
    myth: 'Myth 1: "75% of resumes are auto-rejected by ATS."',
    text: "This number gets repeated constantly, but research into real ATS behavior doesn't support it. Most systems rank and sort resumes for human review rather than automatically rejecting them. The real issue is resumes ranking too low to get noticed — which is fixable.",
  },
  {
    myth: 'Myth 2: "Keyword stuffing improves your score."',
    text: "Older ATS systems rewarded raw keyword counts. In 2026, most platforms evaluate whether a keyword appears in meaningful context — tied to a real result or responsibility — not just how many times it's repeated.",
  },
  {
    myth: 'Myth 3: "A one-page resume is always required."',
    text: "Length isn't penalized by ATS software directly. What matters is whether your experience maps clearly to real qualifications. Padding a one-pager with vague filler is worse than a focused two-pager with real substance.",
  },
  {
    myth: 'Myth 4: "Creative templates help you stand out to ATS."',
    text: "The opposite is usually true. Tables, multi-column layouts, icons, and text boxes are common causes of parsing failures — the system may skip entire sections it can't read cleanly.",
  },
  {
    myth: 'Myth 5: "If I don\'t hear back, my resume was rejected by the ATS."',
    text: "Silence after applying can mean many things — role was filled internally, hiring paused, or simply high competition. Don't assume the ATS is always the villain; use a checker to rule out formatting/keyword issues, then keep applying.",
  },
];

export default function AtsResumeMythsPage() {
  return (
    <article className="container max-w-3xl px-4 py-14 md:px-6">
      <h1 className="text-3xl font-bold tracking-tight sm:text-4xl">
        5 ATS Resume Myths That Are Costing You Interviews
      </h1>
      <div className="mt-6 space-y-6">
        {MYTHS.map((m) => (
          <section key={m.myth}>
            <h2 className="text-xl font-semibold tracking-tight">{m.myth}</h2>
            <p className="mt-2 leading-relaxed text-muted-foreground">{m.text}</p>
          </section>
        ))}
      </div>
    </article>
  );
}