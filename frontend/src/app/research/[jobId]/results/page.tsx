"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

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

export default function ResultsPage() {
  const params = useParams();
  const jobId = params.jobId as string;

  const [job, setJob] = useState<ResearchJob | null>(null);
  const [activeTab, setActiveTab] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [curatedSources, setCuratedSources] = useState<CuratedSource[]>([]);

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

        // Set first completed provider as active tab
        const firstCompleted = data.results.find(r => r.status === "completed");
        if (firstCompleted) {
          setActiveTab(firstCompleted.provider);
        }

        // Fetch curated source details if there are cited sources
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
        <p className="text-muted-foreground">Loading results...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-red-500">{error}</p>
            <Link href="/research">
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

  // If job is not completed, redirect back to progress page
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
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{job.company}</h1>
          <p className="text-muted-foreground">{job.prompt_name}</p>
          <p className="text-sm text-muted-foreground mt-1">
            {job.completed_at && new Date(job.completed_at).toLocaleDateString("en-US", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
              hour: "numeric",
              minute: "2-digit",
            })}
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/research">
            <Button variant="outline">New Research</Button>
          </Link>
          <Link href="/reports">
            <Button variant="ghost">All Reports</Button>
          </Link>
        </div>
      </div>

      {/* Metrics Summary */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Providers</CardDescription>
            <CardTitle className="text-2xl">{completedResults.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Mode</CardDescription>
            <CardTitle className="text-2xl capitalize">{job.mode}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Characters</CardDescription>
            <CardTitle className="text-2xl">
              {completedResults
                .reduce((sum, r) => sum + (r.content?.length || 0), 0)
                .toLocaleString()}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Curated Sources</CardDescription>
            <CardTitle className="text-2xl text-green-600">
              {curatedSources.length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Status</CardDescription>
            <CardTitle className="text-2xl text-green-600">Complete</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Provider Tabs */}
      <div className="border-b">
        <nav className="flex gap-4" aria-label="Provider tabs">
          {completedResults.map((result) => (
            <button
              key={result.provider}
              onClick={() => setActiveTab(result.provider)}
              className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === result.provider
                  ? "border-primary text-foreground"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground"
              }`}
            >
              {PROVIDER_NAMES[result.provider] || result.provider}
              <span className="ml-2 text-xs text-muted-foreground">
                ({(result.content?.length || 0).toLocaleString()} chars)
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Active Result Content */}
      {activeResult && activeResult.content && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>{PROVIDER_NAMES[activeResult.provider] || activeResult.provider}</CardTitle>
                <CardDescription>
                  {activeResult.content.length.toLocaleString()} characters
                  {activeResult.model && ` • ${activeResult.model}`}
                  {activeResult.citations && activeResult.citations.length > 0 &&
                    ` • ${activeResult.citations.length} citations`}
                </CardDescription>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    navigator.clipboard.writeText(activeResult.content || "");
                  }}
                >
                  Copy
                </Button>
                <a
                  href={`${API_BASE}/api/research/${jobId}/export/${activeResult.provider}?format=md`}
                  download
                >
                  <Button variant="outline" size="sm">
                    Export MD
                  </Button>
                </a>
                <a
                  href={`${API_BASE}/api/research/${jobId}/export/${activeResult.provider}?format=html`}
                  download
                >
                  <Button variant="outline" size="sm">
                    Export HTML
                  </Button>
                </a>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none dark:prose-invert prose-headings:font-semibold prose-h1:text-xl prose-h2:text-lg prose-h3:text-base prose-table:text-sm">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {activeResult.content}
              </ReactMarkdown>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Citations */}
      {activeResult && activeResult.citations && activeResult.citations.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Sources & Citations</CardTitle>
            <CardDescription>
              {activeResult.citations.length} sources referenced
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {activeResult.citations.map((citation, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm">
                  <span className="text-muted-foreground font-mono text-xs mt-0.5">
                    [{idx + 1}]
                  </span>
                  <a
                    href={citation.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline break-all"
                  >
                    {citation.title || citation.url}
                  </a>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}

      {/* Curated Sources Used */}
      {curatedSources.length > 0 && (
        <Card className="border-green-200 bg-green-50/50">
          <CardHeader>
            <CardTitle className="text-base text-green-800">Curated Sources Cited</CardTitle>
            <CardDescription>
              {curatedSources.length} of your curated intelligence sources were used in this research
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-3 md:grid-cols-2">
              {curatedSources.map((source) => (
                <div
                  key={source.id}
                  className="p-3 bg-white rounded-lg border border-green-200"
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
      )}

      {/* Failed Results */}
      {job.results.filter(r => r.status === "failed").length > 0 && (
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-base text-red-700">Failed Providers</CardTitle>
          </CardHeader>
          <CardContent>
            {job.results
              .filter(r => r.status === "failed")
              .map((result) => (
                <div key={result.provider} className="text-sm text-red-600">
                  <strong>{PROVIDER_NAMES[result.provider] || result.provider}:</strong>{" "}
                  {result.error || "Unknown error"}
                </div>
              ))}
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <Link href={`/research/${jobId}`}>
          <Button variant="outline">View Job Details</Button>
        </Link>
        <Link href="/research">
          <Button variant="outline">New Research</Button>
        </Link>
      </div>
    </div>
  );
}
