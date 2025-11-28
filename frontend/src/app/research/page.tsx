"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

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

const API_BASE = "http://localhost:8000";

export default function ResearchPage() {
  const router = useRouter();
  const [company, setCompany] = useState("");
  const [selectedPrompt, setSelectedPrompt] = useState("");
  const [selectedProviders, setSelectedProviders] = useState<string[]>(["xai", "google"]);
  const [mode, setMode] = useState("basic");
  const [categories, setCategories] = useState<PromptCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPrompts();
  }, []);

  async function fetchPrompts() {
    try {
      const res = await fetch(`${API_BASE}/api/prompts`);
      if (!res.ok) throw new Error("Failed to fetch prompts");
      const data = await res.json();
      setCategories(data.categories);
    } catch (err) {
      setError("Failed to load prompts. Is the API running?");
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!company.trim() || !selectedPrompt) {
      setError("Please enter a company name and select a prompt");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company: company.trim(),
          prompt_id: selectedPrompt,
          providers: selectedProviders,
          mode,
        }),
      });

      if (!res.ok) throw new Error("Failed to start research");

      const data = await res.json();
      router.push(`/research/${data.job_id}`);
    } catch (err) {
      setError("Failed to start research. Please try again.");
      setLoading(false);
    }
  }

  function toggleProvider(provider: string) {
    setSelectedProviders((prev) =>
      prev.includes(provider)
        ? prev.filter((p) => p !== provider)
        : [...prev, provider]
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">New Research</h1>
        <p className="text-muted-foreground">
          Configure and start a new competitive intelligence research job
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Research Configuration</CardTitle>
          <CardDescription>
            Select a company, research prompt, and providers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="company">Company Name</Label>
              <Input
                id="company"
                placeholder="e.g., Lockheed Martin"
                value={company}
                onChange={(e) => setCompany(e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="prompt">Research Prompt</Label>
              <Select value={selectedPrompt} onValueChange={setSelectedPrompt}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a research prompt" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <div key={category.id}>
                      <div className="px-2 py-1.5 text-xs font-semibold text-muted-foreground">
                        {category.name}
                      </div>
                      {category.prompts.map((prompt) => (
                        <SelectItem key={prompt.id} value={prompt.id}>
                          {prompt.name}
                        </SelectItem>
                      ))}
                    </div>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>AI Providers</Label>
              <div className="flex gap-4">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedProviders.includes("xai")}
                    onChange={() => toggleProvider("xai")}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm">xAI (Grok)</span>
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedProviders.includes("google")}
                    onChange={() => toggleProvider("google")}
                    className="rounded border-gray-300"
                  />
                  <span className="text-sm">Google (Gemini)</span>
                </label>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="mode">Research Mode</Label>
              <Select value={mode} onValueChange={setMode}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="basic">Basic</SelectItem>
                  <SelectItem value="deep">Deep Research</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {error && (
              <div className="p-3 text-sm text-red-500 bg-red-50 rounded-md">
                {error}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? "Starting Research..." : "Start Research"}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
