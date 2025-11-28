"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Briefing error:", error);
  }, [error]);

  return (
    <div className="container mx-auto py-16 px-4">
      <div className="flex flex-col items-center justify-center text-center">
        <div className="mb-6">
          <svg
            className="h-16 w-16 text-orange-500 mx-auto"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M13 10V3L4 14h7v7l9-11h-7z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-bold mb-4">Intelligence Briefing Error</h2>
        <p className="text-muted-foreground mb-6 max-w-md">
          There was a problem loading the intelligence briefing data. Please try again.
        </p>
        <div className="flex gap-4">
          <Button onClick={reset}>Try again</Button>
          <Link href="/">
            <Button variant="outline">Go to Dashboard</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
