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
    console.error("Research error:", error);
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
              d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-bold mb-4">Research Error</h2>
        <p className="text-muted-foreground mb-6 max-w-md">
          There was a problem with the research operation. This could be due to a connection issue with the research API.
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
