"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
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
import { Loader2 } from "lucide-react";
import { API_BASE } from "@/lib/api";

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

/**
 * Strip markdown code fences from content if present.
 * Some AI responses wrap entire content in ```markdown...``` which breaks rendering.
 */
function stripMarkdownCodeFence(content: string): string {
  if (!content) return content;

  // Check if content starts with ```markdown or ``` and ends with ```
  const trimmed = content.trim();
  const codeBlockRegex = /^```(?:markdown|md)?\s*\n([\s\S]*?)\n```$/;
  const match = trimmed.match(codeBlockRegex);

  if (match) {
    return match[1].trim();
  }

  // Also handle case where it starts with ``` but doesn't have proper closing
  if (trimmed.startsWith('```markdown\n') || trimmed.startsWith('```md\n') || trimmed.startsWith('```\n')) {
    let cleaned = trimmed.replace(/^```(?:markdown|md)?\n/, '');
    if (cleaned.endsWith('\n```')) {
      cleaned = cleaned.slice(0, -4);
    } else if (cleaned.endsWith('```')) {
      cleaned = cleaned.slice(0, -3);
    }
    return cleaned.trim();
  }

  return content;
}

const PROVIDER_NAMES: Record<string, string> = {
  xai: "xAI (Grok)",
  google: "Google (Gemini)",
  openai: "OpenAI (GPT-4)",
  anthropic: "Anthropic (Claude)",
  perplexity: "Perplexity",
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
  const [generatingPptx, setGeneratingPptx] = useState(false);

  const downloadSlideContent = useCallback(async (provider: string) => {
    if (!jobId || generatingPptx) return;

    setGeneratingPptx(true);
    try {
      const response = await fetch(
        `${API_BASE}/api/research/${jobId}/presentation?provider=${provider}`,
        { method: "POST" }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to generate slide content");
      }

      const text = await response.text();
      const blob = new Blob([text], { type: "text/plain" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const filename = job?.company
        ? `${job.company}_${job.prompt_name}_slides.txt`.replace(/\s+/g, "_")
        : "slides.txt";
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("Failed to download slide content:", err);
      alert(err instanceof Error ? err.message : "Failed to generate slide content");
    } finally {
      setGeneratingPptx(false);
    }
  }, [jobId, job, generatingPptx]);

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
                disabled={generatingPptx}
                onClick={() => downloadSlideContent("combined")}
              >
                {generatingPptx ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 13v-1m4 1v-3m4 3V8M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                )}
                Slides
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => {
                  navigator.clipboard.writeText(stripMarkdownCodeFence(job.synthesized_report?.content || ""));
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
                disabled={generatingPptx}
                onClick={() => downloadSlideContent(activeResult.provider)}
              >
                {generatingPptx ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 13v-1m4 1v-3m4 3V8M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
                  </svg>
                )}
                Slides
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="gap-2"
                onClick={() => {
                  navigator.clipboard.writeText(stripMarkdownCodeFence(activeResult.content || ""));
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

              {/* Document Content - Paper-like styling */}
              <div className="bg-white dark:bg-gray-900">
                <div className="max-w-4xl mx-auto px-12 py-16 min-h-[600px]">
                  <article className="prose prose-lg max-w-none dark:prose-invert
                    prose-headings:font-semibold
                    prose-h1:text-3xl prose-h1:text-blue-900 prose-h1:dark:text-blue-100 prose-h1:border-b-2 prose-h1:border-blue-200 prose-h1:dark:border-blue-800 prose-h1:pb-4 prose-h1:mb-8 prose-h1:mt-8
                    prose-h2:text-2xl prose-h2:text-gray-800 prose-h2:dark:text-gray-200 prose-h2:border-b prose-h2:border-gray-200 prose-h2:dark:border-gray-700 prose-h2:pb-2 prose-h2:mb-6 prose-h2:mt-10
                    prose-h3:text-xl prose-h3:text-gray-700 prose-h3:dark:text-gray-300 prose-h3:mb-4 prose-h3:mt-8
                    prose-h4:text-lg prose-h4:text-gray-600 prose-h4:dark:text-gray-400 prose-h4:mb-3 prose-h4:mt-6
                    prose-p:text-gray-700 prose-p:dark:text-gray-300 prose-p:leading-7 prose-p:mb-4
                    prose-li:text-gray-700 prose-li:dark:text-gray-300 prose-li:my-1
                    prose-strong:text-gray-900 prose-strong:dark:text-gray-100
                    prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:bg-blue-50 prose-blockquote:dark:bg-blue-950/50 prose-blockquote:py-2 prose-blockquote:px-4 prose-blockquote:not-italic
                    prose-table:text-sm
                    prose-th:bg-gray-100 prose-th:dark:bg-gray-800 prose-th:px-4 prose-th:py-3 prose-th:text-left prose-th:font-semibold
                    prose-td:px-4 prose-td:py-3 prose-td:border-b prose-td:border-gray-200 prose-td:dark:border-gray-700
                    prose-a:text-blue-600 prose-a:dark:text-blue-400 prose-a:no-underline hover:prose-a:underline
                    prose-code:bg-gray-100 prose-code:dark:bg-gray-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm
                    prose-pre:bg-gray-900 prose-pre:text-gray-100">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {stripMarkdownCodeFence(job.synthesized_report.content)}
                    </ReactMarkdown>
                  </article>
                </div>
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
                  {stripMarkdownCodeFence(job.synthesized_report.content).length.toLocaleString()} characters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="p-4 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto text-sm font-mono whitespace-pre-wrap">
                  {stripMarkdownCodeFence(job.synthesized_report.content)}
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

              {/* Document Content - Paper-like styling */}
              <div className="bg-white dark:bg-gray-900">
                <div className="max-w-4xl mx-auto px-12 py-16 min-h-[600px]">
                  <article className="prose prose-lg max-w-none dark:prose-invert
                    prose-headings:font-semibold
                    prose-h1:text-3xl prose-h1:text-blue-900 prose-h1:dark:text-blue-100 prose-h1:border-b-2 prose-h1:border-blue-200 prose-h1:dark:border-blue-800 prose-h1:pb-4 prose-h1:mb-8 prose-h1:mt-8
                    prose-h2:text-2xl prose-h2:text-gray-800 prose-h2:dark:text-gray-200 prose-h2:border-b prose-h2:border-gray-200 prose-h2:dark:border-gray-700 prose-h2:pb-2 prose-h2:mb-6 prose-h2:mt-10
                    prose-h3:text-xl prose-h3:text-gray-700 prose-h3:dark:text-gray-300 prose-h3:mb-4 prose-h3:mt-8
                    prose-h4:text-lg prose-h4:text-gray-600 prose-h4:dark:text-gray-400 prose-h4:mb-3 prose-h4:mt-6
                    prose-p:text-gray-700 prose-p:dark:text-gray-300 prose-p:leading-7 prose-p:mb-4
                    prose-li:text-gray-700 prose-li:dark:text-gray-300 prose-li:my-1
                    prose-strong:text-gray-900 prose-strong:dark:text-gray-100
                    prose-blockquote:border-l-4 prose-blockquote:border-blue-500 prose-blockquote:bg-blue-50 prose-blockquote:dark:bg-blue-950/50 prose-blockquote:py-2 prose-blockquote:px-4 prose-blockquote:not-italic
                    prose-table:text-sm
                    prose-th:bg-gray-100 prose-th:dark:bg-gray-800 prose-th:px-4 prose-th:py-3 prose-th:text-left prose-th:font-semibold
                    prose-td:px-4 prose-td:py-3 prose-td:border-b prose-td:border-gray-200 prose-td:dark:border-gray-700
                    prose-a:text-blue-600 prose-a:dark:text-blue-400 prose-a:no-underline hover:prose-a:underline
                    prose-code:bg-gray-100 prose-code:dark:bg-gray-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm
                    prose-pre:bg-gray-900 prose-pre:text-gray-100">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {stripMarkdownCodeFence(activeResult.content)}
                    </ReactMarkdown>
                  </article>
                </div>
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
                  {stripMarkdownCodeFence(activeResult.content).length.toLocaleString()} characters
                </CardDescription>
              </CardHeader>
              <CardContent>
                <pre className="p-4 bg-gray-900 text-gray-100 rounded-lg overflow-x-auto text-sm font-mono whitespace-pre-wrap">
                  {stripMarkdownCodeFence(activeResult.content)}
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
