import Link from "next/link";

import { Button } from "@/components/ui/button";

export function ClosingCta() {
  return (
    <section className="bg-navy">
      <div className="container max-w-6xl px-4 py-14 md:px-6 md:py-16">
        <div className="grid gap-8 lg:grid-cols-[minmax(0,1.25fr)_auto] lg:items-end lg:gap-16">
          <div>
            <h2 className="font-serif text-[1.875rem] font-semibold leading-[1.15] tracking-[-0.018em] text-white sm:text-[2.125rem]">
              Run your resume against the job description before you apply
            </h2>
            <p className="mt-4 max-w-[58ch] text-[0.9375rem] leading-relaxed text-paper/75">
              The scan takes a minute and returns everything it found — including the parts that
              scored badly and the keywords you have no honest way to claim. Use it to decide what to
              change, and what to leave alone.
            </p>
          </div>
          <div className="lg:justify-self-end">
            <Button
              asChild
              size="lg"
              className="w-full bg-paper text-navy hover:bg-white focus-visible:ring-white focus-visible:ring-offset-navy sm:w-auto"
            >
              <Link href="/tool">Analyze my resume</Link>
            </Button>
            <p className="mt-3 text-xs leading-relaxed text-paper/70">
              Free · no account · files deleted after the scan
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
