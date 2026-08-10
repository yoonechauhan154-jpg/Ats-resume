export function Footer() {
  return (
    <footer className="border-t">
      <div className="container flex flex-col gap-2 px-4 py-6 text-xs text-muted-foreground md:flex-row md:items-center md:justify-between md:px-6">
        <p>
          ATS Scope · Free ATS resume optimizer. We never store your resume — files
          are deleted seconds after analysis.
        </p>
        <p>
          Built to help candidates fix keyword mismatch and format issues, not to
          claim a single magic score. Use it as guidance, not gospel.
        </p>
      </div>
    </footer>
  );
}
