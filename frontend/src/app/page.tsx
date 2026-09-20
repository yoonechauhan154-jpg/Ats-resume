"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, BadgeCheck, Check, FileText, Lock, Search, ScanLine, ShieldCheck, Sparkles } from "lucide-react";

import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FAQS } from "@/lib/faqs";

const FEATURES = [
  { icon: Search, title: "Transparent scoring", text: "A 0–100 compatibility score with every point explained. No black box." },
  { icon: BadgeCheck, title: "Keywords with context", text: "Missing keywords come with the exact JD sentence and why they matter." },
  { icon: FileText, title: "Format checker", text: "Tables, columns, images and fonts that may cause parsing problems — caught for you." },
  { icon: ShieldCheck, title: "Privacy first", text: "Your resume is deleted seconds after analysis. No signup, no storage." },
];

const STEPS = [
  { n: "01", title: "Paste the job description", text: "Copy the JD from the listing — the full responsibilities and requirements." },
  { n: "02", title: "Upload your resume", text: "PDF or DOCX, up to 5MB. It's analyzed in memory, never stored." },
  { n: "03", title: "Get a fix-it report", text: "A transparent score, missing keywords with context, format issues, and AI rewrites." },
];

export default function Landing() {
  return (
    <div className="bg-[#F7F3EA] text-[#18232B]">
      <section className="border-b border-[#D8D0C2]">
        <div className="container grid max-w-6xl items-center gap-12 px-4 py-12 md:grid-cols-[minmax(0,1fr)_minmax(360px,0.85fr)] md:px-6 md:py-20">
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} className="max-w-2xl">
            <Badge className="mb-6 border-[#D8D0C2] bg-[#E8B84B]/20 px-3 py-1 font-medium text-[#18232B] hover:bg-[#E8B84B]/20">
              <Sparkles className="mr-1 h-3 w-3 text-[#E56B4A]" /> 100% free · No signup · Resume never stored
            </Badge>
            <h1 className="font-serif text-5xl font-bold leading-[0.98] tracking-tight sm:text-7xl">Understand your resume&apos;s match to the job</h1>
            <p className="mt-6 max-w-xl text-[#52605F] sm:text-lg">
              Fix the keyword mismatch and formatting issues that keep otherwise strong resumes
              from ranking. See exactly what to change and why — then rewrite it in place.
            </p>
            <div className="mt-8 flex flex-col gap-3 sm:flex-row">
              <Button asChild size="lg" className="bg-[#2F7770] text-[#F7F3EA] shadow-none hover:bg-[#245F5A]"><Link href="/tool">Analyze my resume <ArrowRight className="ml-2 h-4 w-4" /></Link></Button>
              <Button asChild variant="outline" size="lg" className="border-[#B8ADA0] bg-transparent text-[#18232B] shadow-none hover:bg-[#EDE5D8]"><a href="#how-it-works">See how it works</a></Button>
            </div>
          </motion.div>

          <div className="relative" aria-label="Resume and job description matching preview">
            <div className="absolute -left-5 top-8 hidden h-24 w-24 border-l border-t border-[#E56B4A]/50 md:block" />
            <div className="relative overflow-hidden border border-[#B8ADA0] bg-[#FFFDF8] p-5 shadow-[12px_12px_0_#E8B84B] sm:p-7">
              <div className="flex items-center justify-between border-b border-[#D8D0C2] pb-4"><div className="flex items-center gap-2 text-sm font-semibold"><FileText className="h-4 w-4 text-[#2F7770]" /> Resume scan</div><span className="font-mono text-xs text-[#7A8580]">MATCH_014</span></div>
              <div className="mt-6 grid gap-5 sm:grid-cols-[1fr_auto]">
                <div className="space-y-4"><div><div className="h-3 w-32 bg-[#18232B]" /><div className="mt-2 h-2 w-48 bg-[#D8D0C2]" /></div><div className="space-y-2"><div className="h-2 w-full bg-[#E5DED3]" /><div className="h-2 w-11/12 bg-[#E5DED3]" /><div className="h-2 w-4/5 bg-[#E5DED3]" /></div><div className="flex flex-wrap gap-2 pt-1">{["Python", "REST APIs", "PostgreSQL"].map((keyword, index) => <span key={keyword} className={`border px-2 py-1 font-mono text-[11px] ${index === 1 ? "border-[#E56B4A]/50 bg-[#E56B4A]/10 text-[#A94D35]" : "border-[#B9D2CB] bg-[#E4F0EC] text-[#2F7770]"}`}>{keyword}</span>)}</div></div>
                <div className="flex flex-col items-end justify-between border-l border-[#D8D0C2] pl-5"><ScanLine className="h-7 w-7 text-[#E56B4A]" /><div className="text-right"><div className="font-serif text-4xl font-bold text-[#2F7770]">78</div><div className="font-mono text-[10px] uppercase tracking-[0.12em] text-[#7A8580]">match score</div></div></div>
              </div>
              <div className="mt-6 flex items-center gap-2 border-t border-[#D8D0C2] pt-4 text-xs text-[#52605F]"><Check className="h-4 w-4 text-[#2F7770]" /> 12 keywords found · 2 format flags</div>
            </div>
          </div>
        </div>
      </section>

      <section id="how-it-works" className="container max-w-6xl px-4 py-16 md:px-6 md:py-20">
        <h2 className="font-serif text-3xl font-bold tracking-tight sm:text-4xl">Three steps to a stronger resume</h2>
        <div className="mt-8 grid border-y border-[#D8D0C2] sm:grid-cols-3">{STEPS.map((s, i) => <div key={s.n} className={`relative min-h-[190px] p-6 ${i > 0 ? "border-t border-[#D8D0C2] sm:border-l sm:border-t-0" : ""}`}><span className="font-mono text-xs font-semibold tracking-[0.14em] text-[#E56B4A]">{s.n} / MATCH</span><h3 className="mt-8 font-serif text-xl font-bold">{s.title}</h3><p className="mt-2 text-sm leading-relaxed text-[#52605F]">{s.text}</p></div>)}</div>
      </section>

      <section className="border-t border-[#D8D0C2] bg-[#EDE5D8]"><div className="container max-w-6xl px-4 py-14 md:px-6"><h2 className="font-serif text-3xl font-bold tracking-tight sm:text-4xl">Everything in your report</h2><div className="mt-8 grid border-y border-[#D8D0C2] sm:grid-cols-2 lg:grid-cols-4">{FEATURES.map((f, i) => <div key={f.title} className={`flex min-h-[190px] flex-col gap-3 p-5 ${i > 0 ? "border-t border-[#D8D0C2] sm:border-l sm:border-t-0" : ""}`}><f.icon className="h-6 w-6 text-[#2F7770]" /><h3 className="font-serif text-lg font-bold">{f.title}</h3><p className="text-sm leading-relaxed text-[#52605F]">{f.text}</p></div>)}</div></div></section>

      <section className="border-t border-[#D8D0C2] bg-[#F7F3EA]"><div className="container max-w-3xl px-4 py-14 md:px-6"><h2 className="font-serif text-3xl font-bold tracking-tight sm:text-4xl">Frequently asked questions</h2><Accordion type="single" collapsible className="mt-8">{FAQS.map((faq, i) => <AccordionItem key={faq.q} value={`faq-${i}`}><AccordionTrigger>{faq.q}</AccordionTrigger><AccordionContent className="text-[#52605F]">{faq.a}</AccordionContent></AccordionItem>)}</Accordion></div></section>

      <section className="container max-w-4xl px-4 py-16 md:px-6"><div className="flex items-center gap-2 text-sm text-[#52605F]"><Lock className="h-4 w-4 text-[#2F7770]" /><span>Resume files are processed temporarily and normally deleted immediately after parsing. No account, no resume database.</span></div><Button asChild size="lg" className="mt-6 bg-[#2F7770] text-[#F7F3EA] shadow-none hover:bg-[#245F5A]"><Link href="/tool">Get my free report <ArrowRight className="ml-2 h-4 w-4" /></Link></Button></section>
    </div>
  );
}
