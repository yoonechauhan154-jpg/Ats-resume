import Link from "next/link";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { FAQS } from "@/lib/faqs";

export function FaqSection() {
  return (
    <section className="border-b border-hairline bg-white">
      <div className="container max-w-6xl px-4 py-16 md:px-6 md:py-20">
        <div className="grid gap-10 lg:grid-cols-[minmax(0,19rem)_minmax(0,1fr)] lg:gap-16">
          <div>
            <h2 className="font-serif text-[1.875rem] font-semibold leading-[1.15] tracking-[-0.018em] text-navy sm:text-[2.125rem]">
              Questions candidates ask us first
            </h2>
            <p className="mt-4 max-w-[36ch] text-[0.9375rem] leading-relaxed text-greyblue">
              Straight answers on scoring, file handling, and what an ATS check can and cannot tell
              you.
            </p>
            <Link
              href="/faq"
              className="mt-5 inline-block rounded-sm text-sm font-medium text-navy underline decoration-steel/40 underline-offset-[6px] transition-colors hover:decoration-steel focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-steel focus-visible:ring-offset-2 focus-visible:ring-offset-white"
            >
              Read all questions
            </Link>
          </div>

          <Accordion type="single" collapsible className="border-t border-hairline">
            {FAQS.map((faq, index) => (
              <AccordionItem key={faq.q} value={`faq-${index}`} className="border-hairline">
                <AccordionTrigger className="py-5 text-left text-[0.9375rem] font-medium text-ink transition-colors hover:text-navy hover:no-underline focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-steel focus-visible:ring-offset-2 focus-visible:ring-offset-white">
                  {faq.q}
                </AccordionTrigger>
                <AccordionContent className="max-w-[62ch] text-[0.9375rem] leading-relaxed text-greyblue">
                  {faq.a}
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </div>
      </div>
    </section>
  );
}
