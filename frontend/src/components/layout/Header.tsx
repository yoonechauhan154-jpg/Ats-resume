import Link from "next/link";
import { FileSearch } from "lucide-react";

import { Button } from "@/components/ui/button";

export function Header() {
  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-14 items-center gap-6 px-4 md:px-6">
        <Link href="/" className="flex items-center gap-2 font-semibold">
          <FileSearch className="h-5 w-5 text-primary" />
          <span>
            ATS <span className="text-primary">Scope</span>
          </span>
        </Link>
        <nav className="ml-auto flex items-center gap-3 text-sm text-muted-foreground">
          <span className="hidden sm:inline-flex items-center rounded-full border px-3 py-1 text-xs">
            100% free · No signup · Resume never stored
          </span>
          <Button asChild size="sm">
            <Link href="/tool">Analyze my resume</Link>
          </Button>
        </nav>
      </div>
    </header>
  );
}
