import Link from "next/link";

const FOOTER_LINKS = [
  { href: "/tool", label: "Resume checker" },
  { href: "/methodology", label: "Scoring methodology" },
  { href: "/guides", label: "Guides" },
  { href: "/faq", label: "FAQ" },
];

export function Footer() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-hairline bg-white">
      <div className="container max-w-6xl px-4 py-10 md:px-6 md:py-12">
        <div className="grid gap-8 md:grid-cols-[minmax(0,1fr)_auto] md:items-start md:gap-16">
          <div>
            <p className="font-serif text-[1.0625rem] font-semibold tracking-[-0.01em] text-navy">
              ATS Scope
            </p>
            <p className="mt-3 max-w-md text-sm leading-relaxed text-greyblue">
              A free resume-to-job-description checker. Your file is parsed in memory and deleted
              from the server once the scan finishes — no account, no resume database, no paid tier.
            </p>
          </div>
          <nav aria-label="Footer">
            <ul className="grid gap-x-10 gap-y-2 text-sm sm:grid-cols-2">
              {FOOTER_LINKS.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="rounded-sm text-greyblue transition-colors hover:text-ink focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-steel focus-visible:ring-offset-2 focus-visible:ring-offset-white"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </nav>
        </div>
        <p className="mt-8 border-t border-hairline pt-5 text-xs leading-relaxed text-greyblue">
          Scores describe how our checks read one resume against one job description. They are
          guidance, not a prediction of a hiring decision. ATS Scope is independent and not
          affiliated with any applicant tracking system vendor. © {year} ATS Scope
        </p>
      </div>
    </footer>
  );
}

