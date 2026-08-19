import type { Metadata } from "next";
import "./globals.css";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
export const metadata: Metadata = {
  title: "ATS Scope - Free Resume ATS Optimizer & Cover Letter Writer",
  description:
    "Free, no-signup ATS resume checker. Get a transparent 0-100 compatibility score, missing keywords with context, format issue detection, AI bullet rewrites, and a job-synced cover letter. Your resume is never stored.",
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