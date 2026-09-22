/* Plain items on a hairline band — no icon-in-circle kit, no chips.
   Every claim here is verifiable in the product or the backend config.

   Below xl the items stack as a borderless list (one per line, no markers), because
   the inline row does not fit on a single line at those widths — see the measured
   inline width in the QA notes. At xl and up they read as one middot-separated line. */
const ITEMS = [
  "No signup, no account",
  "No credit card, no paid tier",
  "Resume deleted once the scan finishes",
  "5 free scans per IP per day",
  "Every score point explained",
];

export function TrustStrip() {
  return (
    <section aria-label="What to expect" className="border-b border-hairline bg-white">
      <div className="container max-w-6xl px-4 py-5 md:px-6">
        <ul className="flex flex-col gap-y-2.5 text-[0.8125rem] leading-relaxed text-greyblue xl:flex-row xl:flex-wrap xl:items-center xl:gap-y-2">
          {ITEMS.map((item, index) => (
            <li
              key={item}
              className={
                index === 0
                  ? undefined
                  : "xl:before:mx-3 xl:before:text-greyblue/60 xl:before:content-['·']"
              }
            >
              {item}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}

