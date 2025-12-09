"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { API_BASE } from "@/lib/api";

interface Prompt {
  id: string;
  name: string;
  description: string;
  category: string;
  requires_company: boolean;
  content?: string;
}

interface PromptCategory {
  id: string;
  name: string;
  prompts: Prompt[];
}

export default function PromptsPage() {
  const [categories, setCategories] = useState<PromptCategory[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [promptContent, setPromptContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
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
    } catch {
      setError("Failed to load prompts. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  async function loadPromptContent(prompt: Prompt) {
    setSelectedPrompt(prompt);
    setPromptContent(null);

    try {
      const res = await fetch(`${API_BASE}/api/prompts/${prompt.id}`);
      if (!res.ok) throw new Error("Failed to fetch prompt content");
      const data = await res.json();
      setPromptContent(data.content);
    } catch {
      setPromptContent("Failed to load prompt content.");
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="flex items-center gap-3">
          <svg className="animate-spin h-5 w-5 text-red-600" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <p className="text-neutral-500 dark:text-neutral-400">Loading prompts...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card className="border-red-200 dark:border-red-900">
          <CardContent className="pt-6">
            <p className="text-red-600 dark:text-red-400">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-neutral-900 dark:text-white">
          Prompt Library
        </h1>
        <p className="text-base text-neutral-600 dark:text-neutral-400 mt-1">
          View available research prompts and templates
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Prompt Categories */}
        <div className="space-y-4">
          {categories.map((category) => (
            <Card key={category.id} className="border-neutral-200 dark:border-neutral-800">
              <CardHeader className="pb-2 pt-4 px-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base font-semibold text-neutral-900 dark:text-white">
                    {category.name}
                  </CardTitle>
                  <span className="text-xs text-neutral-500 dark:text-neutral-400">
                    {category.prompts.length} prompts
                  </span>
                </div>
              </CardHeader>
              <CardContent className="px-4 pb-3 pt-0">
                <div className="space-y-1">
                  {category.prompts.map((prompt) => (
                    <button
                      key={prompt.id}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-all ${
                        selectedPrompt?.id === prompt.id
                          ? "bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900"
                          : "hover:bg-neutral-50 dark:hover:bg-neutral-800/50 border border-transparent"
                      }`}
                      onClick={() => loadPromptContent(prompt)}
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className={`font-medium text-sm ${
                          selectedPrompt?.id === prompt.id
                            ? "text-red-700 dark:text-red-400"
                            : "text-neutral-800 dark:text-neutral-200"
                        }`}>
                          {prompt.name}
                        </span>
                        {prompt.requires_company && (
                          <span className="text-[10px] font-medium px-1.5 py-0.5 rounded bg-neutral-100 dark:bg-neutral-800 text-neutral-500 dark:text-neutral-400 flex-shrink-0">
                            Company
                          </span>
                        )}
                      </div>
                      {prompt.description && (
                        <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-0.5 line-clamp-1">
                          {prompt.description}
                        </p>
                      )}
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Prompt Content Preview */}
        <div className="lg:sticky lg:top-20 lg:self-start">
          <Card className="border-neutral-200 dark:border-neutral-800">
            <CardHeader className="pb-3 border-b border-neutral-100 dark:border-neutral-800">
              <CardTitle className="text-lg font-semibold text-neutral-900 dark:text-white">
                {selectedPrompt ? selectedPrompt.name : "Select a Prompt"}
              </CardTitle>
              {selectedPrompt && (
                <CardDescription className="text-sm text-neutral-600 dark:text-neutral-400">
                  {selectedPrompt.description}
                </CardDescription>
              )}
            </CardHeader>
            <CardContent className="pt-4">
              {selectedPrompt ? (
                promptContent ? (
                  <pre className="text-sm whitespace-pre-wrap bg-neutral-50 dark:bg-neutral-900 text-neutral-700 dark:text-neutral-300 p-4 rounded-lg overflow-auto max-h-[60vh] border border-neutral-200 dark:border-neutral-800">
                    {promptContent}
                  </pre>
                ) : (
                  <div className="flex items-center gap-2 text-neutral-500">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <span className="text-sm">Loading content...</span>
                  </div>
                )
              ) : (
                <div className="text-center py-8">
                  <div className="w-12 h-12 bg-neutral-100 dark:bg-neutral-800 rounded-full flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <p className="text-sm text-neutral-500 dark:text-neutral-400">
                    Click on a prompt to view its content
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
