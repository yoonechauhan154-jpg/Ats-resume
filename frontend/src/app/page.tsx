"use client";

import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import { ArrowRight } from "lucide-react";

import { ClosingCta } from "@/components/landing/ClosingCta";
import { FaqSection } from "@/components/landing/FaqSection";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { ReportContents } from "@/components/landing/ReportContents";
import { ResumeMockup } from "@/components/landing/ResumeMockup";
import { TrustStrip } from "@/components/landing/TrustStrip";
import { Button } from "@/components/ui/button";

const inlineLink =
  "rounded-sm text-sm font-medium text-navy underline decoration-steel/40 underline-offset-[6px] transition-colors hover:decoration-steel focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-steel focus-visible:ring-offset-2 focus-visible:ring-offset-paper";

export default function Landing() {
  const reduceMotion = useReducedMotion();
  const heroMotion = reduceMotion
    ? {}
    : { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 } };

  return (
    <div className="bg-paper">
      <section className="border-b border-hairline">
        <div className="container grid max-w-6xl items-start gap-12 px-4 pb-14 pt-12 md:px-6 md:pb-16 md:pt-16 lg:grid-cols-[minmax(0,1fr)_minmax(0,1fr)] lg:items-center lg:gap-14 lg:pb-20 lg:pt-20">
          <motion.div transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }} {...heroMotion}>
            <h1 className="max-w-[19ch] font-serif text-[2.5rem] font-semibold leading-[1.06] tracking-[-0.022em] text-navy sm:text-[3.25rem] lg:text-[3.5rem]">
              See your resume the way the screening software reads it
            </h1>
            <p className="mt-6 max-w-[46ch] text-base leading-relaxed text-greyblue sm:text-[1.0625rem]">
              Paste a job description and add your resume. You get a plain read on which keywords you
              match, which ones you are missing — with the sentence each came from — and the
              formatting that stops a parser reading your file.
            </p>
            <div className="mt-9 flex flex-col items-start gap-4 sm:flex-row sm:items-center sm:gap-7">
              <Button
                asChild
                size="lg"
                className="bg-steel text-paper hover:bg-steel-strong focus-visible:ring-steel focus-visible:ring-offset-paper"
              >
                <Link href="/tool">
                  Analyze my resume
                  <ArrowRight aria-hidden />
                </Link>
              </Button>
              <a href="#how-it-works" className={inlineLink}>
                See how it works
              </a>
            </div>
          </motion.div>

          <ResumeMockup />
        </div>
      </section>

      <TrustStrip />
      <HowItWorks />
      <ReportContents />
      <FaqSection />
      <ClosingCta />
    </div>
  );
}
