"use client";

import { useState, useEffect, ReactNode } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import ReactMarkdown, { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import { motion } from "framer-motion";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Citation {
  url: string;
  title?: string;
}

interface ProviderResult {
  provider: string;
  status: "pending" | "running" | "completed" | "failed";
  content?: string;
  citations?: Citation[];
  model?: string;
  error?: string;
}

interface SynthesizedReport {
  content: string;
  models_used: string[];
  high_confidence_findings: string[];
  areas_of_disagreement: string[];
  unique_insights: Record<string, string[]>;
  generated_at?: string;
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
  synthesized_report?: SynthesizedReport;
  created_at: string;
  completed_at?: string;
  result_file?: string;
  error?: string;
  recommended_sources?: string[];
  cited_sources?: string[];
}

interface CuratedSource {
  id: string;
  name: string;
  url: string;
  description: string;
  category_name: string;
}

const API_BASE = "http://localhost:8000";

const PROVIDER_NAMES: Record<string, string> = {
  xai: "xAI (Grok)",
  google: "Google (Gemini)",
  openai: "OpenAI (GPT-4)",
  anthropic: "Anthropic (Claude)",
  perplexity: "Perplexity",
};

// Custom markdown components for professional rendering
const markdownComponents: Components = {
  h1: ({ children }) => (
    <h1 className="text-2xl font-bold text-blue-900 dark:text-blue-100 border-b-2 border-blue-200 dark:border-blue-800 pb-3 mb-6 mt-8 first:mt-0">
      {children}
    </h1>
  ),
  h2: ({ children }) => (
    <h2 className="text-xl font-bold text-gray-800 dark:text-gray-200 mt-10 mb-4 pb-2 border-b border-gray-200 dark:border-gray-700">
      {children}
    </h2>
  ),
  h3: ({ children }) => (
    <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mt-8 mb-3">
      {children}
    </h3>
  ),
  h4: ({ children }) => (
    <h4 className="text-base font-semibold text-gray-600 dark:text-gray-400 mt-6 mb-2 uppercase tracking-wide text-sm">
      {children}
    </h4>
  ),
  p: ({ children }) => (
    <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4 text-base">
      {children}
    </p>
  ),
  ul: ({ children }) => (
    <ul className="list-none space-y-2 mb-6 ml-0">
      {children}
    </ul>
  ),
  ol: ({ children }) => (
    <ol className="list-decimal list-outside space-y-2 mb-6 ml-6 text-gray-700 dark:text-gray-300">
      {children}
    </ol>
  ),
  li: ({ children }) => (
    <li className="text-gray-700 dark:text-gray-300 leading-relaxed flex items-start gap-3">
      <span className="text-blue-500 mt-1.5 flex-shrink-0">•</span>
      <span className="flex-1">{children}</span>
    </li>
  ),
  strong: ({ children }) => (
    <strong className="font-semibold text-gray-900 dark:text-gray-100">
      {children}
    </strong>
  ),
  em: ({ children }) => (
    <em className="italic text-gray-600 dark:text-gray-400">
      {children}
    </em>
  ),
  blockquote: ({ children }) => (
    <blockquote className="border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-950/50 py-3 px-5 my-6 rounded-r-lg">
      <div className="text-gray-700 dark:text-gray-300 italic">
        {children}
      </div>
    </blockquote>
  ),
  a: ({ href, children }) => (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
    >
      {children}
    </a>
  ),
  hr: () => (
    <hr className="my-8 border-t-2 border-gray-200 dark:border-gray-700" />
  ),
  // Professional table rendering
  table: ({ children }) => (
    <div className="my-6 overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
      <table className="w-full text-sm">
        {children}
      </table>
    </div>
  ),
  thead: ({ children }) => (
    <thead className="bg-gradient-to-r from-blue-900 to-blue-800 text-white">
      {children}
    </thead>
  ),
  tbody: ({ children }) => (
    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
      {children}
    </tbody>
  ),
  tr: ({ children }) => (
    <tr className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors even:bg-gray-50/50 dark:even:bg-gray-800/30">
      {children}
    </tr>
  ),
  th: ({ children }) => (
    <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider whitespace-nowrap">
      {children}
    </th>
  ),
  td: ({ children }) => (
    <td className="px-4 py-3 text-gray-700 dark:text-gray-300 align-top">
      {children}
    </td>
  ),
  // Code blocks
  code: ({ className, children }) => {
    const isBlock = className?.includes('language-');
    if (isBlock) {
      return (
        <code className="block bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm font-mono">
          {children}
        </code>
      );
    }
    return (
      <code className="bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200 px-1.5 py-0.5 rounded text-sm font-mono">
        {children}
      </code>
    );
  },
  pre: ({ children }) => (
    <pre className="my-4 overflow-x-auto">
      {children}
    </pre>
  ),
};

export default function ResultsPage() {
  const params = useParams();
  const jobId = params.jobId as string;

  const [job, setJob] = useState<ResearchJob | null>(null);
  const [activeTab, setActiveTab] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [curatedSources, setCuratedSources] = useState<CuratedSource[]>([]);
  const [viewMode, setViewMode] = useState<"document" | "raw">("document");

  useEffect(() => {
    if (!jobId) return;

    async function fetchJob() {
      try {
        const res = await fetch(`${API_BASE}/api/research/${jobId}`);
        if (!res.ok) {
          if (res.status === 404) {
            setError("Research job not found");
          } else {
            throw new Error("Failed to fetch job");
          }
          return;
        }
        const data: ResearchJob = await res.json();
        setJob(data);

        // If there's a synthesized report, show it first
        if (data.synthesized_report) {
          setActiveTab("combined");
        } else {
          const firstCompleted = data.results.find(r => r.status === "completed");
          if (firstCompleted) {
            setActiveTab(firstCompleted.provider);
          }
        }

        if (data.cited_sources && data.cited_sources.length > 0) {
          const sourcesRes = await fetch(`${API_BASE}/api/sources`);
          if (sourcesRes.ok) {
            const sourcesData = await sourcesRes.json();
            const allSources: CuratedSource[] = [];
            for (const category of sourcesData.categories || []) {
              for (const source of category.sources || []) {
                if (data.cited_sources.includes(source.id)) {
                  allSources.push({
                    ...source,
                    category_name: category.name,
                  });
                }
              }
            }
            setCuratedSources(allSources);
          }
        }
      } catch (err) {
        setError("Failed to load results. Is the API running?");
      } finally {
        setLoading(false);
      }
    }

    fetchJob();
  }, [jobId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary" />
          <p className="text-muted-foreground">Loading results...</p>
        </div>
      </div>
    );
  }

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
    return null;
  }

  if (job.status !== "completed") {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground">
              Research is still in progress. Please wait for it to complete.
            </p>
            <Link href={`/research/${jobId}`}>
              <Button className="mt-4">View Progress</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const completedResults = job.results.filter(r => r.status === "completed");
  const activeResult = job.results.find(r => r.provider === activeTab);

  return (
    <div className="space-y-6">
      {/* Toolbar */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-wrap items-center justify-between gap-4 p-4 bg-muted/50 rounded-lg border"
      >
        <div className="flex items-center gap-4">
          <Link href="/">
            <Button variant="ghost" size="sm">
              <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back
            </Button>
          </Link>
          <div className="h-6 w-px bg-border" />
          <div className="flex rounded-lg border bg-background p-1">
            <button
              onClick={() => setViewMode("document")}
              className={cn(
                "px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
                viewMode === "document"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              Document View
            </button>
            <button
              onClick={() => setViewMode("raw")}
              className={cn(
                "px-3 py-1.5 text-sm font-medium rounded-md transition-colors",
                viewMode === "raw"
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:text-foreground"
              )}
            >
              Raw Markdown
            </button>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-sm text-muted-foreground mr-2">Export:</span>
          {/* Combined report export buttons */}
          {activeTab === "combined" && job.synthesized_report && (
            <>
              <a href={`${API_BASE}/api/research/${jobId}/export/combined?format=pdf`}>
                <Button variant="outline" size="sm" className="gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  PDF
                </Button>
              </a>
              <a href={`${API_BASE}/api/research/${jobId}/export/combined?format=docx`}>
                <Button variant="outline" size="sm" className="gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Word
                </Button>
              </a>
              <a href={`${API_BASE}/api/research/${jobId}/export/combined?format=html`}>
                <Button variant="outline" size="sm" className="gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  HTML
                </Button>
              </a>
              <Button
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => {
                  navigator.clipboard.writeText(job.synthesized_report?.content || "");
                }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </Button>
            </>
          )}
          {/* Individual provider export buttons */}
          {activeTab !== "combined" && activeResult && (
            <>
              <a href={`${API_BASE}/api/research/${jobId}/export/${activeResult.provider}?format=pdf`}>
                <Button variant="outline" size="sm" className="gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                  </svg>
                  PDF
                </Button>
              </a>
              <a href={`${API_BASE}/api/research/${jobId}/export/${activeResult.provider}?format=docx`}>
                <Button variant="outline" size="sm" className="gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Word
                </Button>
              </a>
              <a href={`${API_BASE}/api/research/${jobId}/export/${activeResult.provider}?format=html`}>
                <Button variant="outline" size="sm" className="gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                  </svg>
                  HTML
                </Button>
              </a>
              <Button
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => {
                  navigator.clipboard.writeText(activeResult.content || "");
                }}
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Copy
              </Button>
            </>
          )}
        </div>
      </motion.div>

      {/* Provider Tabs */}
      {(completedResults.length > 1 || job.synthesized_report) && (
        <div className="flex flex-wrap gap-2">
          {/* Combined Report Tab - shows first when available */}
          {job.synthesized_report && (
            <button
              onClick={() => setActiveTab("combined")}
              className={cn(
                "px-4 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-2",
                activeTab === "combined"
                  ? "bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-md"
                  : "bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 hover:bg-purple-200 dark:hover:bg-purple-800"
              )}
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Combined Report
            </button>
          )}
          {/* Individual provider tabs */}
          {completedResults.map((result) => (
            <button
              key={result.provider}
              onClick={() => setActiveTab(result.provider)}
              className={cn(
                "px-4 py-2 rounded-lg font-medium text-sm transition-all",
                activeTab === result.provider
                  ? "bg-primary text-primary-foreground shadow-md"
                  : "bg-muted text-muted-foreground hover:bg-muted/80"
              )}
            >
              {PROVIDER_NAMES[result.provider] || result.provider}
            </button>
          ))}
        </div>
      )}

      {/* Combined Report View */}
      {activeTab === "combined" && job.synthesized_report && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {/* Synthesis Metadata Card */}
          <Card className="mb-6 border-purple-200 dark:border-purple-800 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-950/50 dark:to-blue-950/50">
            <CardContent className="pt-6">
              <div className="grid gap-6 md:grid-cols-3">
                {/* Models Used */}
                <div>
                  <h4 className="text-sm font-semibold text-purple-800 dark:text-purple-200 mb-2 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Models Contributing
                  </h4>
                  <div className="flex flex-wrap gap-1">
                    {job.synthesized_report.models_used.map((model) => (
                      <span key={model} className="px-2 py-1 text-xs bg-white dark:bg-gray-800 rounded-full border">
                        {PROVIDER_NAMES[model] || model}
                      </span>
                    ))}
                  </div>
                </div>

                {/* High Confidence Count */}
                <div>
                  <h4 className="text-sm font-semibold text-green-700 dark:text-green-300 mb-2 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    High Confidence Findings
                  </h4>
                  <p className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {job.synthesized_report.high_confidence_findings.length}
                    <span className="text-sm font-normal text-muted-foreground ml-2">points of agreement</span>
                  </p>
                </div>

                {/* Areas of Disagreement */}
                <div>
                  <h4 className="text-sm font-semibold text-amber-700 dark:text-amber-300 mb-2 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    Areas Needing Attention
                  </h4>
                  <p className="text-2xl font-bold text-amber-600 dark:text-amber-400">
                    {job.synthesized_report.areas_of_disagreement.length}
                    <span className="text-sm font-normal text-muted-foreground ml-2">conflicting points</span>
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {viewMode === "document" ? (
            <div className="bg-white dark:bg-gray-900 shadow-xl rounded-lg overflow-hidden border">
              {/* Document Header - Combined Report Style */}
              <div className="bg-gradient-to-r from-purple-900 via-blue-900 to-blue-800 text-white p-8">
                <div className="max-w-4xl mx-auto">
                  <div className="text-purple-200 text-sm font-semibold tracking-wider mb-4 flex items-center gap-2">
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    RED 6 COMBINED INTELLIGENCE REPORT
                  </div>
                  <h1 className="text-4xl font-bold mb-3">{job.company}</h1>
                  <p className="text-xl text-blue-100 mb-6">{job.prompt_name}</p>
                  <div className="flex flex-wrap gap-6 text-sm text-blue-200">
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {job.completed_at && new Date(job.completed_at).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </div>
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      Combined from {job.synthesized_report.models_used.length} AI Models
                    </div>
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                      Internal Use Only
                    </div>
                  </div>
                </div>
              </div>

              {/* Document Content */}
              <div className="max-w-4xl mx-auto px-8 py-12">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={markdownComponents}
                >
                  {job.synthesized_report.content}
                </ReactMarkdown>
              </div>

              {/* Document Footer */}
              <div className="border-t border-gray-200 dark:border-gray-700 px-8 py-6 bg-gray-50 dark:bg-gray-800">
                <div className="max-w-4xl mx-auto text-center text-sm text-gray-500 dark:text-gray-400">
                  <p>Synthesized from: {job.synthesized_report.models_used.map(m => PROVIDER_NAMES[m] || m).join(", ")}</p>
                  <p className="mt-1">Generated by Red 6 Competitive Intelligence Platform - Confidential</p>
                </div>
              </div>
            </div>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Raw Markdown - Combined Report</CardTitle>
                <CardDescription>
                  {job.synthesized_report.content.length.toLocaleString()} characters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="p-4 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto text-sm font-mono whitespace-pre-wrap">
                  {job.synthesized_report.content}
                </pre>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}

      {/* Individual Provider Document View */}
      {activeTab !== "combined" && activeResult && activeResult.content && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
        >
          {viewMode === "document" ? (
            <div className="bg-white dark:bg-gray-900 shadow-xl rounded-lg overflow-hidden border">
              {/* Document Header - looks like a PDF cover */}
              <div className="bg-gradient-to-r from-blue-900 to-blue-800 text-white p-8">
                <div className="max-w-4xl mx-auto">
                  <div className="text-blue-200 text-sm font-semibold tracking-wider mb-4">
                    RED 6 COMPETITIVE INTELLIGENCE
                  </div>
                  <h1 className="text-4xl font-bold mb-3">{job.company}</h1>
                  <p className="text-xl text-blue-100 mb-6">{job.prompt_name}</p>
                  <div className="flex flex-wrap gap-6 text-sm text-blue-200">
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      {job.completed_at && new Date(job.completed_at).toLocaleDateString("en-US", {
                        year: "numeric",
                        month: "long",
                        day: "numeric",
                      })}
                    </div>
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                      </svg>
                      {PROVIDER_NAMES[activeResult.provider] || activeResult.provider}
                    </div>
                    <div className="flex items-center gap-2">
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                      Internal Use Only
                    </div>
                  </div>
                </div>
              </div>

              {/* Document Content */}
              <div className="max-w-4xl mx-auto px-8 py-12">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={markdownComponents}
                >
                  {activeResult.content}
                </ReactMarkdown>
              </div>

              {/* Document Footer */}
              <div className="border-t border-gray-200 dark:border-gray-700 px-8 py-6 bg-gray-50 dark:bg-gray-800">
                <div className="max-w-4xl mx-auto text-center text-sm text-gray-500 dark:text-gray-400">
                  <p>Generated by Red 6 Competitive Intelligence Platform</p>
                  <p className="mt-1">Confidential - For Internal Use Only</p>
                </div>
              </div>
            </div>
          ) : (
            /* Raw Markdown View */
            <Card>
              <CardHeader>
                <CardTitle>Raw Markdown</CardTitle>
                <CardDescription>
                  {activeResult.content.length.toLocaleString()} characters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="p-4 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto text-sm font-mono whitespace-pre-wrap">
                  {activeResult.content}
                </pre>
              </CardContent>
            </Card>
          )}
        </motion.div>
      )}

      {/* Citations Section */}
      {activeResult && activeResult.citations && activeResult.citations.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                Sources & Citations
              </CardTitle>
              <CardDescription>
                {activeResult.citations.length} sources referenced in this report
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 sm:grid-cols-2">
                {activeResult.citations.map((citation, idx) => (
                  <a
                    key={idx}
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-start gap-3 p-3 rounded-lg border hover:border-blue-300 hover:bg-blue-50 dark:hover:bg-blue-950 transition-colors group"
                  >
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-400 text-xs font-semibold flex items-center justify-center">
                      {idx + 1}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 truncate">
                        {citation.title || citation.url}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {citation.url}
                      </p>
                    </div>
                    <svg className="w-4 h-4 text-gray-400 group-hover:text-blue-600 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Curated Sources */}
      {curatedSources.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card className="border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-950/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-800 dark:text-green-200">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Curated Sources Cited
              </CardTitle>
              <CardDescription>
                {curatedSources.length} verified intelligence sources were used
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-2">
                {curatedSources.map((source) => (
                  <div
                    key={source.id}
                    className="p-3 bg-white dark:bg-gray-900 rounded-lg border border-green-200 dark:border-green-800"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="font-medium text-sm">{source.name}</h4>
                        <p className="text-xs text-muted-foreground">{source.category_name}</p>
                      </div>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">{source.description}</p>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-xs text-blue-600 hover:underline mt-1 inline-block"
                    >
                      {source.url}
                    </a>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* Failed Providers */}
      {job.results.filter(r => r.status === "failed").length > 0 && (
        <Card className="border-red-200 dark:border-red-800">
          <CardHeader>
            <CardTitle className="text-base text-red-700 dark:text-red-300">Failed Providers</CardTitle>
          </CardHeader>
          <CardContent>
            {job.results
              .filter(r => r.status === "failed")
              .map((result) => (
                <div key={result.provider} className="text-sm text-red-600 dark:text-red-400">
                  <strong>{PROVIDER_NAMES[result.provider] || result.provider}:</strong>{" "}
                  {result.error || "Unknown error"}
                </div>
              ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
