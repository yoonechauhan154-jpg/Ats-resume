import type { Metadata } from "next";
import { IBM_Plex_Sans, Source_Serif_4 } from "next/font/google";

import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";

/* Headline face — set tight and deliberate, not a default system serif. */
const serif = Source_Serif_4({
  subsets: ["latin"],
  weight: ["400", "600", "700"],
  style: ["normal"],
  display: "swap",
  variable: "--font-serif",
});

/* Interface face — body copy, form chrome, buttons, data labels. */
const sans = IBM_Plex_Sans({
  subsets: ["latin"],
  weight: ["400", "500", "600"],
  style: ["normal"],
  display: "swap",
  variable: "--font-sans",
});
export const metadata: Metadata = {
  title: "ATS Scope — Free Resume Matching, Explained",
  description:
    "Meet ATS Scope: compare your resume with a job description, understand keyword gaps, and get practical fixes. Free to use, with no account required.",
  alternates: {
    canonical: "https://ats-resumecheck.vercel.app/",
  },
  verification: {
    google: "0flRTVdHxlYuHeF6djtBuGFGjbqJB_hcysGRkTAFnqc",
  },
};
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning className={`${sans.variable} ${serif.variable}`}>
      <body>
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-3 focus:z-50 focus:rounded-md focus:border focus:border-hairline focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:font-medium focus:text-navy"
        >
          Skip to content
        </a>
        <div className="flex min-h-screen flex-col">
          <Header />
          <main id="main-content" className="flex-1">
            {children}
          </main>
          <Footer />
        </div>
      </body>
    </html>
  );
}