import Link from "next/link";

import { Button } from "@/components/ui/button";

const NAV_LINKS = [
  { href: "/guides", label: "Guides", className: "" },
  { href: "/faq", label: "FAQ", className: "" },
  { href: "/methodology", label: "Methodology", className: "hidden lg:block" },
];

const focusRing =
  "rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-steel focus-visible:ring-offset-2 focus-visible:ring-offset-paper";

export function Header() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-hairline bg-paper/90 backdrop-blur supports-[backdrop-filter]:bg-paper/80">
      <div className="container flex h-16 max-w-6xl items-center gap-6 px-4 md:px-6">
        <Link
          href="/"
          className={`font-serif text-[1.0625rem] font-semibold tracking-[-0.01em] text-navy ${focusRing}`}
        >
          ATS Scope
        </Link>
        <nav aria-label="Main" className="ml-auto flex items-center gap-5 sm:gap-7">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm text-greyblue transition-colors hover:text-ink ${link.className} ${focusRing}`}
            >
              {link.label}
            </Link>
          ))}
          <Button
            asChild
            size="sm"
            className="bg-steel px-4 text-paper hover:bg-steel-strong focus-visible:ring-steel focus-visible:ring-offset-paper"
          >
            <Link href="/tool">Start a scan</Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}

