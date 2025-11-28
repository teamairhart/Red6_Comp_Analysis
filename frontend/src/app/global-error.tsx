"use client";

import { useEffect } from "react";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("Global error:", error);
  }, [error]);

  return (
    <html>
      <body>
        <div style={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          minHeight: "100vh",
          padding: "2rem",
          fontFamily: "system-ui, sans-serif",
          textAlign: "center"
        }}>
          <div style={{ marginBottom: "2rem" }}>
            <svg
              style={{ height: "96px", width: "96px", color: "#ef4444" }}
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
          </div>
          <h2 style={{ fontSize: "1.5rem", fontWeight: "bold", marginBottom: "1rem" }}>
            Critical Application Error
          </h2>
          <p style={{ color: "#6b7280", marginBottom: "2rem", maxWidth: "28rem" }}>
            A critical error has occurred. Please refresh the page or try again later.
          </p>
          {error.digest && (
            <p style={{
              fontSize: "0.75rem",
              color: "#9ca3af",
              marginBottom: "1rem",
              fontFamily: "monospace"
            }}>
              Error ID: {error.digest}
            </p>
          )}
          <div style={{ display: "flex", gap: "1rem" }}>
            <button
              onClick={reset}
              style={{
                padding: "0.75rem 1.5rem",
                backgroundColor: "#000",
                color: "#fff",
                border: "none",
                borderRadius: "0.375rem",
                cursor: "pointer",
                fontSize: "0.875rem",
                fontWeight: "500"
              }}
            >
              Try again
            </button>
            <button
              onClick={() => window.location.href = "/"}
              style={{
                padding: "0.75rem 1.5rem",
                backgroundColor: "transparent",
                color: "#000",
                border: "1px solid #d1d5db",
                borderRadius: "0.375rem",
                cursor: "pointer",
                fontSize: "0.875rem",
                fontWeight: "500"
              }}
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
