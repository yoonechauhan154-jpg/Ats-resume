import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
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
    <html lang="en" suppressHydrationWarning>
      <body>
        <div className="flex min-h-screen flex-col">
          <Header />
          <main className="flex-1">{children}</main>
          <Footer />
        </div>
      </body>
    </html>
  );
}