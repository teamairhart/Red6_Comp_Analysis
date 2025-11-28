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
    console.error("Reports error:", error);
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
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
        </div>
        <h2 className="text-xl font-bold mb-4">Reports Error</h2>
        <p className="text-muted-foreground mb-6 max-w-md">
          There was a problem loading the reports. Please check your connection and try again.
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
