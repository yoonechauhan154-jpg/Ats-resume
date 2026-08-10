"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, BadgeCheck, FileText, Lock, Search, ShieldCheck, Sparkles } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";

const FEATURES = [
  {
    icon: Search,
    title: "Transparent scoring",
    text: "A 0–100 compatibility score with every point explained. No black box.",
  },
  {
    icon: BadgeCheck,
    title: "Keywords with context",
    text: "Missing keywords come with the exact JD sentence and why they matter.",
  },
  {
    icon: FileText,
    title: "Format checker",
    text: "Tables, columns, images and fonts that break ATS parsing — caught for you.",
  },
  {
    icon: ShieldCheck,
    title: "Privacy first",
    text: "Your resume is deleted seconds after analysis. No signup, no storage.",
  },
];

const STEPS = [
  { n: "1", title: "Paste the job description", text: "Copy the JD from the listing — the full responsibilities and requirements." },
  { n: "2", title: "Upload your resume", text: "PDF or DOCX, up to 5MB. It's analyzed in memory, never stored." },
  { n: "3", title: "Get a fix-it report", text: "A transparent score, missing keywords with context, format issues, and AI rewrites." },
];

export default function Landing() {
  return (
    <>
      {/* Hero */}
      <section className="border-b bg-gradient-to-b from-primary/5 to-background">
        <div className="container max-w-6xl px-4 py-16 text-center md:px-6 md:py-24">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            className="mx-auto max-w-3xl"
          >
            <Badge variant="outline" className="mb-4 px-3 py-1">
              <Sparkles className="mr-1 h-3 w-3 text-primary" /> 100% free · No signup · Resume never stored
            </Badge>
            <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
              Is your resume surviving{" "}
              <span className="text-primary">ATS screening</span>?
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-muted-foreground sm:text-lg">
              Fix the keyword mismatch and formatting issues that keep otherwise strong resumes
              from ranking. See exactly what to change and why — then rewrite it in place.
            </p>
            <div className="mt-8 flex flex-col items-center justify-center gap-3 sm:flex-row">
              <Button asChild size="lg">
                <Link href="/tool">
                  Analyze my resume <ArrowRight className="ml-2 h-4 w-4" />
                </Link>
              </Button>
              <Button asChild variant="outline" size="lg">
                <a href="#how-it-works">See how it works</a>
              </Button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="container max-w-6xl px-4 py-14 md:px-6">
        <h2 className="text-center text-2xl font-bold tracking-tight sm:text-3xl">
          Three steps to a stronger resume
        </h2>
        <div className="mt-8 grid gap-4 sm:grid-cols-3">
          {STEPS.map((s, i) => (
            <motion.div
              key={s.n}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
            >
              <Card className="h-full">
                <CardContent className="flex h-full flex-col gap-2 p-5">
                  <span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-sm font-bold text-primary">
                    {s.n}
                  </span>
                  <h3 className="font-semibold">{s.title}</h3>
                  <p className="text-sm text-muted-foreground">{s.text}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="border-t bg-muted/30">
        <div className="container max-w-6xl px-4 py-14 md:px-6">
          <h2 className="text-center text-2xl font-bold tracking-tight sm:text-3xl">
            Everything in your report
          </h2>
          <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map((f, i) => (
              <motion.div
                key={f.title}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
              >
                <Card className="h-full">
                  <CardContent className="flex h-full flex-col gap-2 p-5">
                    <f.icon className="h-6 w-6 text-primary" />
                    <h3 className="font-semibold">{f.title}</h3>
                    <p className="text-sm text-muted-foreground">{f.text}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="container max-w-4xl px-4 py-16 text-center md:px-6">
        <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
          <Lock className="h-4 w-4" />
          <span>Uploads are processed in memory and deleted immediately. No account, no tracking of your resume.</span>
        </div>
        <Button asChild size="lg" className="mt-6">
          <Link href="/tool">
            Get my free report <ArrowRight className="ml-2 h-4 w-4" />
          </Link>
        </Button>
      </section>
    </>
  );
}
