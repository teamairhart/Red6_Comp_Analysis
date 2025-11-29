"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { cn } from "@/lib/utils";

const API_BASE = "http://localhost:8000";

// All companies - primaries first
const COMPANIES = [
  // Primary Competitors
  { name: "Elbit Systems", sector: "Defense Electronics", primary: true },
  { name: "Thales", sector: "Defense & Aerospace", primary: true },
  { name: "BAE Systems", sector: "Defense & Security", primary: true },
  // Other Key Competitors
  { name: "Lockheed Martin", sector: "Aerospace & Defense", primary: false },
  { name: "Northrop Grumman", sector: "Aerospace & Defense", primary: false },
  { name: "Raytheon", sector: "Defense Technology", primary: false },
  { name: "Boeing", sector: "Aerospace & Defense", primary: false },
  { name: "L3Harris", sector: "Defense Technology", primary: false },
  { name: "General Dynamics", sector: "Aerospace & Defense", primary: false },
  { name: "Leonardo", sector: "Defense & Aerospace", primary: false },
  { name: "SAAB", sector: "Defense & Aerospace", primary: false },
  { name: "Rheinmetall", sector: "Defense & Automotive", primary: false },
  { name: "Hensoldt", sector: "Defense Electronics", primary: false },
  { name: "Rafael", sector: "Defense Technology", primary: false },
  { name: "IAI (Israel Aerospace Industries)", sector: "Aerospace & Defense", primary: false },
];

const PROVIDERS = [
  { id: "google", name: "Google Gemini", description: "Fast, good for general research" },
  { id: "perplexity", name: "Perplexity", description: "Best for current news & citations" },
  { id: "openai", name: "OpenAI GPT-4", description: "Strong analysis & reasoning" },
  { id: "anthropic", name: "Anthropic Claude", description: "Detailed, nuanced analysis" },
  { id: "xai", name: "xAI Grok", description: "Real-time data access" },
];

interface Prompt {
  id: string;
  name: string;
  description: string;
  category: string;
  requires_company: boolean;
}

interface PromptCategory {
  id: string;
  name: string;
  prompts: Prompt[];
}

interface RecentJob {
  id: string;
  company: string;
  prompt_name: string;
  status: string;
  progress: number;
  created_at: string;
  completed_at?: string;
}

interface ProviderAvailability {
  [key: string]: boolean;
}

interface Source {
  id: string;
  name: string;
  url: string;
  description: string;
  keywords: string[];
}

interface SourceCategory {
  id: string;
  name: string;
  sources: Source[];
}

export default function Dashboard() {
  const router = useRouter();

  // Form state
  const [selectedCompany, setSelectedCompany] = useState<string>("");
  const [customCompany, setCustomCompany] = useState<string>("");
  const [selectedPrompt, setSelectedPrompt] = useState<string>("");
  const [selectedProviders, setSelectedProviders] = useState<string[]>(["google"]);
  const [combineResults, setCombineResults] = useState(false);

  // Data state
  const [categories, setCategories] = useState<PromptCategory[]>([]);
  const [recentJobs, setRecentJobs] = useState<RecentJob[]>([]);
  const [providerAvailability, setProviderAvailability] = useState<ProviderAvailability>({});
  const [sourceCategories, setSourceCategories] = useState<SourceCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPrompts();
    fetchRecentJobs();
    fetchProviderAvailability();
    fetchSources();
  }, []);

  async function fetchPrompts() {
    try {
      const res = await fetch(`${API_BASE}/api/prompts`);
      if (res.ok) {
        const data = await res.json();
        setCategories(data.categories || []);
      }
    } catch (err) {
      console.error("Failed to fetch prompts:", err);
    }
  }

  async function fetchRecentJobs() {
    try {
      const res = await fetch(`${API_BASE}/api/research?limit=5`);
      if (res.ok) {
        const data = await res.json();
        setRecentJobs(data);
      }
    } catch (err) {
      console.error("Failed to fetch recent jobs:", err);
    }
  }

  async function fetchProviderAvailability() {
    try {
      const res = await fetch(`${API_BASE}/api/research/providers`);
      if (res.ok) {
        const data = await res.json();
        setProviderAvailability(data.providers || {});
        // Auto-select first available provider if current selection is unavailable
        if (selectedProviders.length === 1 && !data.providers[selectedProviders[0]]) {
          const firstAvailable = Object.entries(data.providers).find(([_, available]) => available)?.[0];
          if (firstAvailable) {
            setSelectedProviders([firstAvailable]);
          }
        }
      }
    } catch (err) {
      console.error("Failed to fetch provider availability:", err);
    }
  }

  async function fetchSources() {
    try {
      const res = await fetch(`${API_BASE}/api/sources`);
      if (res.ok) {
        const data = await res.json();
        setSourceCategories(data.categories || []);
      }
    } catch (err) {
      console.error("Failed to fetch sources:", err);
    }
  }

  function toggleProvider(providerId: string) {
    // Don't allow toggling unavailable providers
    if (providerAvailability[providerId] === false) return;

    setSelectedProviders(prev =>
      prev.includes(providerId)
        ? prev.filter(p => p !== providerId)
        : [...prev, providerId]
    );
  }

  async function startResearch() {
    const company = selectedCompany === "__custom__" ? customCompany : selectedCompany;

    if (!company || !selectedPrompt || selectedProviders.length === 0) {
      setError("Please select a company, prompt, and at least one model");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company,
          prompt_id: selectedPrompt,
          providers: selectedProviders,
          mode: combineResults ? "combined" : "basic",
        }),
      });

      if (!res.ok) throw new Error("Failed to start research");

      const data = await res.json();
      router.push(`/research/${data.job_id}`);
    } catch {
      setError("Failed to start research. Please try again.");
      setLoading(false);
    }
  }

  const selectedPromptDetails = categories
    .flatMap(c => c.prompts)
    .find(p => p.id === selectedPrompt);

  // Flatten all sources for the list
  const allSources = sourceCategories.flatMap(cat =>
    cat.sources.map(src => ({ ...src, categoryName: cat.name }))
  );

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="relative">
        <div className="absolute inset-0 -z-10 bg-gradient-to-r from-red-600/5 via-transparent to-transparent rounded-2xl" />
        <div className="py-2">
          <h1 className="text-4xl font-bold tracking-tight text-neutral-900 dark:text-white">
            Intelligence Dashboard
          </h1>
          <p className="text-lg text-neutral-600 dark:text-neutral-400 mt-2">
            Research defense technology competitors with AI-powered analysis
          </p>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-5">
        {/* Left Sidebar - Quick Links & Recent Research */}
        <div className="lg:col-span-1 space-y-6 order-2 lg:order-1">
          {/* Quick Links */}
          <Card className="border-neutral-200 dark:border-neutral-800 shadow-sm">
            <CardHeader className="pb-3 pt-4 px-4">
              <CardTitle className="text-base font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                Quick Links
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-1 px-4 pb-4">
              <Link href="/reports" className="block">
                <Button variant="ghost" size="sm" className="w-full justify-start h-9 text-sm font-medium hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600">
                  <svg className="w-4 h-4 mr-2 text-neutral-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Reports
                </Button>
              </Link>
              <Link href="/prompts" className="block">
                <Button variant="ghost" size="sm" className="w-full justify-start h-9 text-sm font-medium hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600">
                  <svg className="w-4 h-4 mr-2 text-neutral-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h7" />
                  </svg>
                  Prompts
                </Button>
              </Link>
              <Link href="/briefing" className="block">
                <Button variant="ghost" size="sm" className="w-full justify-start h-9 text-sm font-medium hover:bg-red-50 dark:hover:bg-red-950/30 hover:text-red-600">
                  <svg className="w-4 h-4 mr-2 text-neutral-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Briefing
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Recent Research */}
          <Card className="border-neutral-200 dark:border-neutral-800 shadow-sm">
            <CardHeader className="pb-3 pt-4 px-4">
              <CardTitle className="text-base font-bold text-neutral-900 dark:text-white flex items-center gap-2">
                <svg className="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                Recent Research
              </CardTitle>
            </CardHeader>
            <CardContent className="px-4 pb-4">
              {recentJobs.length === 0 ? (
                <div className="text-center py-6">
                  <div className="w-10 h-10 bg-neutral-100 dark:bg-neutral-800 rounded-full flex items-center justify-center mx-auto mb-2">
                    <svg className="w-5 h-5 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p className="text-sm text-neutral-500">No recent research</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {recentJobs.slice(0, 6).map(job => (
                    <Link
                      key={job.id}
                      href={job.status === "completed" ? `/research/${job.id}/results` : `/research/${job.id}`}
                      className="block"
                    >
                      <div className="p-2.5 -mx-1 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-800/50 transition-colors border border-transparent hover:border-neutral-200 dark:hover:border-neutral-700">
                        <div className="flex items-center gap-2">
                          <span className={cn(
                            "w-2 h-2 rounded-full flex-shrink-0",
                            job.status === "completed" ? "bg-emerald-500" :
                            job.status === "running" ? "bg-red-500 animate-pulse" :
                            job.status === "failed" ? "bg-red-600" :
                            "bg-neutral-400"
                          )} />
                          <span className="font-medium text-sm text-neutral-900 dark:text-white truncate">{job.company}</span>
                        </div>
                        <div className="text-xs text-neutral-500 dark:text-neutral-400 truncate pl-4 mt-0.5">
                          {job.prompt_name}
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Main Content - New Research & Sources */}
        <div className="lg:col-span-4 space-y-6 order-1 lg:order-2">
          {/* Two-column grid for Research Form and Sources */}
          <div className="grid gap-6 xl:grid-cols-2">
            {/* New Research Form */}
            <Card className="border-neutral-200 dark:border-neutral-800 shadow-md">
              <CardHeader className="border-b border-neutral-100 dark:border-neutral-800 bg-gradient-to-r from-neutral-50 to-white dark:from-neutral-900 dark:to-neutral-900">
                <CardTitle className="text-xl font-bold text-neutral-900 dark:text-white flex items-center gap-3">
                  <div className="w-10 h-10 bg-red-600 rounded-lg flex items-center justify-center shadow-lg shadow-red-500/20">
                    <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  New Research
                </CardTitle>
                <CardDescription className="text-base text-neutral-600 dark:text-neutral-400">
                  Select a company, research type, and AI models to generate intelligence
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6 pt-6">
                {/* Company Selection */}
                <div className="space-y-2">
                  <Label htmlFor="company" className="text-sm font-semibold text-neutral-700 dark:text-neutral-300">
                    Target Company
                  </Label>
                  <Select value={selectedCompany} onValueChange={setSelectedCompany}>
                    <SelectTrigger id="company" className="w-full h-11 text-base">
                      <SelectValue placeholder="Select a company to research..." />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectGroup>
                        <SelectLabel className="text-red-600 dark:text-red-500 font-bold text-sm py-2 px-2 bg-red-50 dark:bg-red-950/50 -mx-1 mb-1 flex items-center gap-2">
                          <span className="w-2 h-2 rounded-full bg-red-500" />
                          PRIMARY COMPETITORS
                        </SelectLabel>
                        {COMPANIES.filter(c => c.primary).map(company => (
                          <SelectItem key={company.name} value={company.name} className="py-2.5">
                            <div className="flex items-center gap-2">
                              <span className="font-medium text-neutral-900 dark:text-white">{company.name}</span>
                              <span className="text-neutral-500 text-sm">— {company.sector}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectGroup>
                      <SelectGroup>
                        <SelectLabel className="text-neutral-600 dark:text-neutral-400 font-bold text-sm py-2 px-2 bg-neutral-100 dark:bg-neutral-800 -mx-1 mb-1 mt-2">
                          OTHER COMPETITORS
                        </SelectLabel>
                        {COMPANIES.filter(c => !c.primary).map(company => (
                          <SelectItem key={company.name} value={company.name} className="py-2.5">
                            <div className="flex items-center gap-2">
                              <span>{company.name}</span>
                              <span className="text-neutral-500 text-sm">— {company.sector}</span>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectGroup>
                      <SelectGroup>
                        <SelectLabel className="text-neutral-500 dark:text-neutral-500 font-bold text-sm py-2 px-2 bg-neutral-50 dark:bg-neutral-900 -mx-1 mb-1 mt-2">
                          CUSTOM ENTRY
                        </SelectLabel>
                        <SelectItem value="__custom__">
                          <span className="italic text-neutral-600 dark:text-neutral-400">Enter custom company...</span>
                        </SelectItem>
                      </SelectGroup>
                    </SelectContent>
                  </Select>
                  {selectedCompany === "__custom__" && (
                    <input
                      type="text"
                      placeholder="Enter company name..."
                      value={customCompany}
                      onChange={(e) => setCustomCompany(e.target.value)}
                      className="mt-2 w-full px-4 py-3 border border-neutral-300 dark:border-neutral-700 rounded-lg text-base bg-white dark:bg-neutral-900 focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    />
                  )}
                </div>

                {/* Prompt Selection */}
                <div className="space-y-2">
                  <Label htmlFor="prompt" className="text-sm font-semibold text-neutral-700 dark:text-neutral-300">
                    Research Type
                  </Label>
                  <Select value={selectedPrompt} onValueChange={setSelectedPrompt}>
                    <SelectTrigger id="prompt" className="w-full h-11 text-base">
                      <SelectValue placeholder="Select research type..." />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map(category => (
                        <SelectGroup key={category.id}>
                          <SelectLabel className="font-bold text-sm py-2 px-2 bg-neutral-100 dark:bg-neutral-800 -mx-1 mb-1 mt-1 first:mt-0 text-neutral-700 dark:text-neutral-300 uppercase tracking-wide">
                            {category.name}
                          </SelectLabel>
                          {category.prompts.map(prompt => (
                            <SelectItem key={prompt.id} value={prompt.id} className="py-2.5">
                              <div>
                                <span className="font-medium text-neutral-900 dark:text-white">{prompt.name}</span>
                                {prompt.description && (
                                  <span className="text-neutral-500 text-sm ml-2">
                                    — {prompt.description}
                                  </span>
                                )}
                              </div>
                            </SelectItem>
                          ))}
                        </SelectGroup>
                      ))}
                    </SelectContent>
                  </Select>
                  {selectedPromptDetails && (
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 mt-2 p-3 bg-neutral-50 dark:bg-neutral-800/50 rounded-lg">
                      {selectedPromptDetails.description}
                    </p>
                  )}
                </div>

                {/* Model Selection */}
                <div className="space-y-3">
                  <Label className="text-sm font-semibold text-neutral-700 dark:text-neutral-300">
                    AI Models
                  </Label>
                  <p className="text-sm text-neutral-500 dark:text-neutral-400">
                    Select one or more AI models to run the research
                  </p>
                  <div className="grid gap-3 sm:grid-cols-2">
                    {PROVIDERS.map(provider => {
                      const isAvailable = providerAvailability[provider.id] !== false;
                      const isSelected = selectedProviders.includes(provider.id);

                      return (
                        <button
                          key={provider.id}
                          type="button"
                          onClick={() => toggleProvider(provider.id)}
                          disabled={!isAvailable}
                          className={cn(
                            "flex items-start gap-3 p-4 rounded-xl border-2 text-left transition-all relative",
                            !isAvailable
                              ? "border-neutral-200 dark:border-neutral-800 bg-neutral-100 dark:bg-neutral-900 opacity-50 cursor-not-allowed"
                              : isSelected
                                ? "border-red-500 bg-red-50 dark:bg-red-950/30 shadow-md shadow-red-500/10"
                                : "border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600 hover:shadow-sm"
                          )}
                        >
                          <div className={cn(
                            "w-5 h-5 rounded-md border-2 flex items-center justify-center flex-shrink-0 mt-0.5 transition-colors",
                            !isAvailable
                              ? "border-neutral-300 dark:border-neutral-600 bg-neutral-200 dark:bg-neutral-700"
                              : isSelected
                                ? "border-red-500 bg-red-500"
                                : "border-neutral-300 dark:border-neutral-600"
                          )}>
                            {isSelected && isAvailable && (
                              <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                              </svg>
                            )}
                            {!isAvailable && (
                              <svg className="w-3 h-3 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                              </svg>
                            )}
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className={cn(
                              "font-semibold text-sm",
                              !isAvailable ? "text-neutral-400 dark:text-neutral-500" : "text-neutral-900 dark:text-white"
                            )}>
                              {provider.name}
                            </div>
                            <div className={cn(
                              "text-sm mt-0.5",
                              !isAvailable
                                ? "text-neutral-400 dark:text-neutral-600"
                                : "text-neutral-500 dark:text-neutral-400"
                            )}>
                              {!isAvailable ? "API key not configured" : provider.description}
                            </div>
                          </div>
                          {!isAvailable && (
                            <span className="absolute top-2 right-2 px-2 py-1 text-xs font-semibold bg-neutral-200 dark:bg-neutral-700 text-neutral-500 dark:text-neutral-400 rounded-md">
                              Unavailable
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Combined Report Option */}
                {selectedProviders.length > 1 && (
                  <div className="flex items-center gap-4 p-4 bg-gradient-to-r from-red-50 to-orange-50 dark:from-red-950/20 dark:to-orange-950/20 border border-red-200 dark:border-red-900/50 rounded-xl">
                    <button
                      type="button"
                      onClick={() => setCombineResults(!combineResults)}
                      className={cn(
                        "w-6 h-6 rounded-md border-2 flex items-center justify-center flex-shrink-0 transition-colors",
                        combineResults
                          ? "border-red-500 bg-red-500"
                          : "border-neutral-300 dark:border-neutral-600"
                      )}
                    >
                      {combineResults && (
                        <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </button>
                    <div>
                      <div className="font-semibold text-sm text-neutral-900 dark:text-white">Generate Combined Report</div>
                      <div className="text-sm text-neutral-600 dark:text-neutral-400">
                        Merge results from all models into a single comprehensive report
                      </div>
                    </div>
                  </div>
                )}

                {/* Error Message */}
                {error && (
                  <div className="p-4 bg-red-50 dark:bg-red-950/50 border border-red-200 dark:border-red-800 rounded-xl text-sm text-red-600 dark:text-red-400 flex items-center gap-3">
                    <svg className="w-5 h-5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {error}
                  </div>
                )}

                {/* Submit Button */}
                <Button
                  onClick={startResearch}
                  disabled={loading || !selectedCompany || !selectedPrompt || selectedProviders.length === 0}
                  className="w-full h-12 text-base font-semibold bg-red-600 hover:bg-red-700 text-white shadow-lg shadow-red-500/25 hover:shadow-red-500/40 transition-all disabled:opacity-50 disabled:shadow-none"
                  size="lg"
                >
                  {loading ? (
                    <>
                      <svg className="animate-spin -ml-1 mr-3 h-5 w-5" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                      </svg>
                      Starting Research...
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      Start Research
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>

            {/* Intelligence Sources */}
            <Card className="h-fit border-neutral-200 dark:border-neutral-800 shadow-md">
              <CardHeader className="border-b border-neutral-100 dark:border-neutral-800 pb-4">
                <CardTitle className="text-xl font-bold text-neutral-900 dark:text-white flex items-center gap-3">
                  <div className="w-8 h-8 bg-neutral-900 dark:bg-white rounded-lg flex items-center justify-center">
                    <svg className="w-4 h-4 text-white dark:text-neutral-900" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                  </div>
                  Intelligence Sources
                </CardTitle>
                <CardDescription className="text-sm text-neutral-500 dark:text-neutral-400">
                  {allSources.length} curated sources for competitive research
                </CardDescription>
              </CardHeader>
              <CardContent className="pt-4">
                <div className="max-h-[500px] overflow-y-auto pr-2 -mr-2">
                  <div className="space-y-4">
                    {sourceCategories.map(category => (
                      <div key={category.id}>
                        <div className="text-sm font-bold text-neutral-700 dark:text-neutral-300 uppercase tracking-wider py-2 sticky top-0 bg-white dark:bg-neutral-900 border-b border-neutral-100 dark:border-neutral-800 mb-2">
                          {category.name}
                        </div>
                        <div className="space-y-1">
                          {category.sources.map(source => (
                            <a
                              key={source.id}
                              href={source.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-2 py-2 px-2 -mx-2 rounded-lg hover:bg-neutral-50 dark:hover:bg-neutral-800/50 transition-colors group"
                            >
                              <svg className="w-4 h-4 text-neutral-400 group-hover:text-red-600 flex-shrink-0 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                              </svg>
                              <span className="text-sm text-neutral-700 dark:text-neutral-300 group-hover:text-red-600 dark:group-hover:text-red-500 truncate transition-colors font-medium">
                                {source.name}
                              </span>
                            </a>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
