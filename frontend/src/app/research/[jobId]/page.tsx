"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { API_BASE } from "@/lib/api";

interface ProviderResult {
  provider: string;
  status: "pending" | "running" | "completed" | "failed";
  content?: string;
  error?: string;
}

interface ResearchJob {
  id: string;
  company: string;
  prompt_id: string;
  prompt_name: string;
  providers: string[];
  mode: string;
  status: "pending" | "running" | "completed" | "failed";
  progress: number;
  results: ProviderResult[];
  created_at: string;
  completed_at?: string;
  error?: string;
}

const PROVIDER_NAMES: Record<string, string> = {
  google: "Google (Gemini)",
  perplexity: "Perplexity",
  openai: "OpenAI (GPT-4)",
  anthropic: "Anthropic (Claude)",
  xai: "xAI (Grok)",
};

export default function ResearchJobPage() {
  const params = useParams();
  const router = useRouter();
  const jobId = params.jobId as string;

  const [job, setJob] = useState<ResearchJob | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;

    let isActive = true; // Prevent state updates after unmount
    let shouldPoll = true; // Track if polling should continue

    const fetchJob = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/research/${jobId}`);
        if (!res.ok) {
          if (res.status === 404) {
            if (isActive) setError("Research job not found");
          } else {
            throw new Error("Failed to fetch job status");
          }
          return;
        }
        const data = await res.json();
        if (isActive) {
          setJob(data);
          setLoading(false);

          // Stop polling if job is done
          if (data.status === "completed" || data.status === "failed") {
            shouldPoll = false;
          }
        }
      } catch (err) {
        if (isActive) {
          setError("Failed to load job status. Is the API running?");
          setLoading(false);
        }
      }
    };

    // Initial fetch
    fetchJob();

    // Poll every 2 seconds while job is running
    const interval = setInterval(() => {
      if (shouldPoll) {
        fetchJob();
      }
    }, 2000);

    return () => {
      isActive = false;
      clearInterval(interval);
    };
  }, [jobId]); // Only depend on jobId, not job?.status

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-500";
      case "running":
        return "text-blue-500";
      case "failed":
        return "text-red-500";
      default:
        return "text-muted-foreground";
    }
  };

  const getStatusBg = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500";
      case "running":
        return "bg-blue-500";
      case "failed":
        return "bg-red-500";
      default:
        return "bg-muted";
    }
  };

  if (error) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-red-500">{error}</p>
            <Link href="/">
              <Button className="mt-4">Start New Research</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading job status...</p>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Research Progress</h1>
          <p className="text-muted-foreground">
            {job.company} - {job.prompt_name}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-sm font-medium ${getStatusColor(job.status)}`}>
            {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
          </span>
        </div>
      </div>

      {/* Progress bar */}
      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Overall Progress</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="w-full bg-muted rounded-full h-3">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${getStatusBg(job.status)}`}
              style={{ width: `${job.progress}%` }}
            />
          </div>
          <p className="text-sm text-muted-foreground mt-2">
            {job.progress}% complete
          </p>
        </CardContent>
      </Card>

      {/* Provider status cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {job.results.map((result) => (
          <Card key={result.provider}>
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">
                  {PROVIDER_NAMES[result.provider] || result.provider}
                </CardTitle>
                <span
                  className={`inline-flex items-center gap-1.5 text-xs font-medium ${getStatusColor(result.status)}`}
                >
                  <span
                    className={`w-2 h-2 rounded-full ${getStatusBg(result.status)} ${
                      result.status === "running" ? "animate-pulse" : ""
                    }`}
                  />
                  {result.status}
                </span>
              </div>
            </CardHeader>
            <CardContent>
              {result.status === "pending" && (
                <p className="text-sm text-muted-foreground">Waiting to start...</p>
              )}
              {result.status === "running" && (
                <p className="text-sm text-muted-foreground">
                  Researching {job.company}...
                </p>
              )}
              {result.status === "completed" && (
                <p className="text-sm text-green-600">
                  Research complete. {result.content ? `${result.content.length} characters.` : ""}
                </p>
              )}
              {result.status === "failed" && (
                <p className="text-sm text-red-500">
                  {result.error || "An error occurred"}
                </p>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Job details */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Job Details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <dt className="text-muted-foreground">Job ID</dt>
              <dd className="font-mono text-xs">{job.id}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Mode</dt>
              <dd>
                {job.mode === "deep" ? (
                  <span className="inline-flex items-center gap-1.5">
                    <span>Deep Research</span>
                    <span className="px-1.5 py-0.5 text-xs font-bold bg-gradient-to-r from-purple-500 to-blue-500 text-white rounded">
                      AI-POWERED
                    </span>
                  </span>
                ) : "Basic"}
              </dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Started</dt>
              <dd>{new Date(job.created_at).toLocaleString()}</dd>
            </div>
            {job.completed_at && (
              <div>
                <dt className="text-muted-foreground">Completed</dt>
                <dd>{new Date(job.completed_at).toLocaleString()}</dd>
              </div>
            )}
          </dl>
        </CardContent>
      </Card>

      {/* Action buttons */}
      <div className="flex gap-4">
        {job.status === "completed" && (
          <Link href={`/research/${job.id}/results`}>
            <Button>View Results</Button>
          </Link>
        )}
        <Link href="/">
          <Button variant="outline">New Research</Button>
        </Link>
        <Link href="/reports">
          <Button variant="ghost">View All Reports</Button>
        </Link>
      </div>

      {/* Error display */}
      {job.error && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader>
            <CardTitle className="text-base text-red-700">Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-red-600">{job.error}</p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
