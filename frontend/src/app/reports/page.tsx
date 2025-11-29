"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface ProviderResult {
  provider: string;
  status: string;
  content?: string;
  model?: string;
}

interface ResearchJob {
  id: string;
  company: string;
  prompt_id: string;
  prompt_name: string;
  status: string;
  providers: string[];
  mode: string;
  progress: number;
  results: ProviderResult[];
  created_at: string;
  completed_at?: string;
}

const API_BASE = "http://localhost:8000";

const PROVIDER_NAMES: Record<string, string> = {
  xai: "xAI (Grok)",
  google: "Google (Gemini)",
  openai: "OpenAI (GPT-4)",
  anthropic: "Anthropic (Claude)",
  perplexity: "Perplexity",
};

export default function ReportsPage() {
  const [jobs, setJobs] = useState<ResearchJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchJobs();
  }, []);

  async function fetchJobs() {
    try {
      const res = await fetch(`${API_BASE}/api/research?limit=100`);
      if (!res.ok) throw new Error("Failed to fetch reports");
      const data = await res.json();
      // Only show completed jobs
      setJobs(data.filter((job: ResearchJob) => job.status === "completed"));
    } catch (err) {
      setError("Failed to load reports. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  const filteredJobs = jobs.filter(
    (job) =>
      job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.prompt_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Group by date
  const groupedJobs = filteredJobs.reduce(
    (acc, job) => {
      const date = job.completed_at
        ? new Date(job.completed_at).toDateString()
        : new Date(job.created_at).toDateString();
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(job);
      return acc;
    },
    {} as Record<string, ResearchJob[]>
  );

  const sortedDates = Object.keys(groupedJobs).sort(
    (a, b) => new Date(b).getTime() - new Date(a).getTime()
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          <p className="text-muted-foreground">Loading reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardContent className="pt-6">
            <p className="text-red-500">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground">
            Browse and download completed research reports
          </p>
        </div>
        <Link href="/">
          <Button>New Research</Button>
        </Link>
      </div>

      <div className="max-w-md">
        <Input
          placeholder="Search reports..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {jobs.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <div className="text-center py-8">
              <svg
                className="w-12 h-12 text-muted-foreground mx-auto mb-4"
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
              <p className="text-muted-foreground">
                No reports found. Start a new research to generate reports.
              </p>
              <Link href="/">
                <Button className="mt-4">Start Research</Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-8">
          {sortedDates.map((date, dateIdx) => (
            <motion.div
              key={date}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: dateIdx * 0.1 }}
              className="space-y-4"
            >
              <h2 className="text-lg font-semibold text-muted-foreground flex items-center gap-2">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {new Date(date).toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </h2>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {groupedJobs[date].map((job, idx) => {
                  const completedResults = job.results.filter(
                    (r) => r.status === "completed"
                  );
                  const totalChars = completedResults.reduce(
                    (sum, r) => sum + (r.content?.length || 0),
                    0
                  );

                  return (
                    <motion.div
                      key={job.id}
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      transition={{ delay: idx * 0.05 }}
                    >
                      <Card className="h-full hover:shadow-lg transition-shadow">
                        <CardHeader className="pb-2">
                          <div className="flex items-start justify-between">
                            <div>
                              <CardTitle className="text-lg">{job.company}</CardTitle>
                              <CardDescription className="mt-1">
                                {job.prompt_name}
                              </CardDescription>
                            </div>
                            <span
                              className={cn(
                                "px-2 py-1 text-xs font-medium rounded-full",
                                job.mode === "deep"
                                  ? "bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300"
                                  : "bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300"
                              )}
                            >
                              {job.mode === "deep" ? "Deep" : "Basic"}
                            </span>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-3">
                            {/* Providers used */}
                            <div className="flex flex-wrap gap-1">
                              {completedResults.map((result) => (
                                <span
                                  key={result.provider}
                                  className="px-2 py-0.5 text-xs bg-muted rounded-full"
                                >
                                  {PROVIDER_NAMES[result.provider] || result.provider}
                                </span>
                              ))}
                            </div>

                            {/* Stats */}
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                </svg>
                                {(totalChars / 1000).toFixed(1)}k chars
                              </span>
                              <span className="flex items-center gap-1">
                                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                {job.completed_at &&
                                  new Date(job.completed_at).toLocaleTimeString([], {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                  })}
                              </span>
                            </div>

                            {/* Actions */}
                            <div className="flex gap-2 pt-2">
                              <Link href={`/research/${job.id}/results`} className="flex-1">
                                <Button variant="default" size="sm" className="w-full">
                                  View Report
                                </Button>
                              </Link>
                              <a
                                href={`${API_BASE}/api/research/${job.id}/export/${completedResults[0]?.provider}?format=pdf`}
                              >
                                <Button variant="outline" size="sm">
                                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                  </svg>
                                </Button>
                              </a>
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
