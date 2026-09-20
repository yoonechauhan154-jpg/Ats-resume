import Link from "next/link";
import { FileSearch } from "lucide-react";

import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-[#D8D0C2] bg-[#F7F3EA]/95 backdrop-blur supports-[backdrop-filter]:bg-[#F7F3EA]/95">
      <div className="container flex h-14 items-center gap-6 px-4 md:px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold text-[#18232B]">
          <FileSearch className="h-5 w-5 text-[#2F7770]" />
          <span>
            ATS <span className="text-[#2F7770]">Scope</span>
          </span>
        </Link>
        <nav className="ml-auto flex items-center gap-3 text-sm text-muted-foreground">
          <Link href="/guides" className="hover:text-[#18232B]">
            Guides
          </Link>
          <Link href="/faq" className="hover:text-[#18232B]">
            FAQ
          </Link>
          <Button asChild size="sm" className="bg-[#2F7770] text-[#F7F3EA] shadow-none hover:bg-[#245F5A]">
            <Link href="/tool">Analyze my resume</Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}
