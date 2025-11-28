"use client";

import { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

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

const API_BASE = "http://localhost:8000";

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
    } catch (err) {
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
    } catch (err) {
      setPromptContent("Failed to load prompt content.");
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading prompts...</p>
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
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Prompt Library</h1>
        <p className="text-muted-foreground">
          View available research prompts and templates
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-6">
          {categories.map((category) => (
            <Card key={category.id}>
              <CardHeader>
                <CardTitle>{category.name}</CardTitle>
                <CardDescription>
                  {category.prompts.length} prompts available
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {category.prompts.map((prompt) => (
                    <div
                      key={prompt.id}
                      className={`p-3 rounded-md border cursor-pointer transition-colors ${
                        selectedPrompt?.id === prompt.id
                          ? "border-primary bg-primary/5"
                          : "border-transparent hover:bg-muted"
                      }`}
                      onClick={() => loadPromptContent(prompt)}
                    >
                      <div className="font-medium text-sm">{prompt.name}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {prompt.description}
                      </div>
                      {prompt.requires_company && (
                        <span className="inline-block mt-2 text-xs bg-secondary px-2 py-0.5 rounded">
                          Requires company
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="lg:sticky lg:top-8 lg:self-start">
          <Card>
            <CardHeader>
              <CardTitle>
                {selectedPrompt ? selectedPrompt.name : "Select a Prompt"}
              </CardTitle>
              {selectedPrompt && (
                <CardDescription>{selectedPrompt.description}</CardDescription>
              )}
            </CardHeader>
            <CardContent>
              {selectedPrompt ? (
                promptContent ? (
                  <pre className="text-sm whitespace-pre-wrap bg-muted p-4 rounded-md overflow-auto max-h-[60vh]">
                    {promptContent}
                  </pre>
                ) : (
                  <p className="text-muted-foreground">Loading content...</p>
                )
              ) : (
                <p className="text-muted-foreground">
                  Click on a prompt to view its content
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
