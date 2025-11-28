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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface Source {
  id: string;
  name: string;
  url: string;
  description: string;
  keywords: string[];
  reliability: "high" | "medium" | "low";
  update_frequency: string;
  hit_count: number;
}

interface SourceCategory {
  id: string;
  name: string;
  icon: string;
  description: string;
  sources: Source[];
}

interface SourceLibrary {
  categories: SourceCategory[];
  version: string;
  last_updated: string;
}

const API_BASE = "http://localhost:8000";

const CATEGORY_ICONS: Record<string, string> = {
  government: "🏛️",
  defense: "🛡️",
  business: "💼",
  patents: "📄",
  talent: "👥",
  research: "🔍",
};

const RELIABILITY_COLORS: Record<string, string> = {
  high: "bg-green-100 text-green-800",
  medium: "bg-yellow-100 text-yellow-800",
  low: "bg-red-100 text-red-800",
};

export default function SourcesPage() {
  const [library, setLibrary] = useState<SourceLibrary | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Add Source Dialog State
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newSource, setNewSource] = useState({
    category_id: "",
    name: "",
    url: "",
    description: "",
    keywords: "",
    reliability: "medium",
    update_frequency: "daily",
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetchSources();
  }, []);

  async function fetchSources() {
    try {
      const res = await fetch(`${API_BASE}/api/sources`);
      if (!res.ok) throw new Error("Failed to fetch sources");
      const data = await res.json();
      setLibrary(data);
      if (data.categories.length > 0) {
        setSelectedCategory(data.categories[0].id);
      }
    } catch (err) {
      setError("Failed to load sources. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  async function handleSearch(query: string) {
    setSearchQuery(query);
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/sources/search?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error("Search failed");
      const data = await res.json();
      setSearchResults(data.results);
    } catch (err) {
      console.error("Search error:", err);
    }
  }

  async function handleAddSource() {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/api/sources/source`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newSource,
          keywords: newSource.keywords.split(",").map(k => k.trim()).filter(k => k),
        }),
      });

      if (!res.ok) throw new Error("Failed to create source");

      // Reset form and close dialog
      setNewSource({
        category_id: "",
        name: "",
        url: "",
        description: "",
        keywords: "",
        reliability: "medium",
        update_frequency: "daily",
      });
      setDialogOpen(false);

      // Refresh sources
      fetchSources();
    } catch (err) {
      console.error("Failed to add source:", err);
    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading sources...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-red-500">{error}</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const selectedCategoryData = library?.categories.find(c => c.id === selectedCategory);
  const displaySources = searchQuery.length >= 2
    ? searchResults.map(r => r.source)
    : selectedCategoryData?.sources || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Source Library</h1>
          <p className="text-muted-foreground">
            Curated intelligence sources for competitive research
          </p>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>Add Source</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[500px]">
            <DialogHeader>
              <DialogTitle>Add New Source</DialogTitle>
              <DialogDescription>
                Add a curated intelligence source to the library.
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="grid gap-2">
                <Label htmlFor="category">Category</Label>
                <Select
                  value={newSource.category_id}
                  onValueChange={(v) => setNewSource({ ...newSource, category_id: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a category" />
                  </SelectTrigger>
                  <SelectContent>
                    {library?.categories.map((cat) => (
                      <SelectItem key={cat.id} value={cat.id}>
                        {CATEGORY_ICONS[cat.id] || "📁"} {cat.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="name">Source Name</Label>
                <Input
                  id="name"
                  value={newSource.name}
                  onChange={(e) => setNewSource({ ...newSource, name: e.target.value })}
                  placeholder="e.g., Defense News"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="url">URL</Label>
                <Input
                  id="url"
                  value={newSource.url}
                  onChange={(e) => setNewSource({ ...newSource, url: e.target.value })}
                  placeholder="https://..."
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={newSource.description}
                  onChange={(e) => setNewSource({ ...newSource, description: e.target.value })}
                  placeholder="Brief description of the source"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="keywords">Keywords (comma-separated)</Label>
                <Input
                  id="keywords"
                  value={newSource.keywords}
                  onChange={(e) => setNewSource({ ...newSource, keywords: e.target.value })}
                  placeholder="defense, military, contracts"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="reliability">Reliability</Label>
                  <Select
                    value={newSource.reliability}
                    onValueChange={(v) => setNewSource({ ...newSource, reliability: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="low">Low</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="frequency">Update Frequency</Label>
                  <Select
                    value={newSource.update_frequency}
                    onValueChange={(v) => setNewSource({ ...newSource, update_frequency: v })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="real-time">Real-time</SelectItem>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="varies">Varies</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleAddSource}
                disabled={saving || !newSource.category_id || !newSource.name || !newSource.url}
              >
                {saving ? "Adding..." : "Add Source"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Search */}
      <div className="max-w-md">
        <Input
          placeholder="Search sources by name or keyword..."
          value={searchQuery}
          onChange={(e) => handleSearch(e.target.value)}
        />
        {searchQuery.length >= 2 && (
          <p className="text-sm text-muted-foreground mt-1">
            Found {searchResults.length} results for "{searchQuery}"
          </p>
        )}
      </div>

      <div className="grid md:grid-cols-[250px_1fr] gap-6">
        {/* Category Sidebar */}
        <div className="space-y-2">
          <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wider mb-3">
            Categories
          </h3>
          {library?.categories.map((category) => (
            <button
              key={category.id}
              onClick={() => {
                setSelectedCategory(category.id);
                setSearchQuery("");
                setSearchResults([]);
              }}
              className={`w-full text-left px-3 py-2 rounded-md text-sm transition-colors ${
                selectedCategory === category.id && searchQuery.length < 2
                  ? "bg-primary text-primary-foreground"
                  : "hover:bg-muted"
              }`}
            >
              <span className="mr-2">{CATEGORY_ICONS[category.id] || "📁"}</span>
              {category.name}
              <span className="ml-2 text-xs opacity-70">
                ({category.sources.length})
              </span>
            </button>
          ))}
        </div>

        {/* Sources Grid */}
        <div>
          {searchQuery.length < 2 && selectedCategoryData && (
            <div className="mb-4">
              <h2 className="text-xl font-semibold">
                {CATEGORY_ICONS[selectedCategoryData.id] || "📁"} {selectedCategoryData.name}
              </h2>
              <p className="text-sm text-muted-foreground">
                {selectedCategoryData.description}
              </p>
            </div>
          )}

          <div className="grid gap-4 md:grid-cols-2">
            {displaySources.map((source) => (
              <Card key={source.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base">{source.name}</CardTitle>
                    <span className={`text-xs px-2 py-1 rounded-full ${RELIABILITY_COLORS[source.reliability]}`}>
                      {source.reliability}
                    </span>
                  </div>
                  <CardDescription className="text-xs">
                    {source.update_frequency} updates
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground mb-3">
                    {source.description}
                  </p>
                  <div className="flex flex-wrap gap-1 mb-3">
                    {source.keywords.slice(0, 4).map((kw) => (
                      <span
                        key={kw}
                        className="text-xs bg-muted px-2 py-0.5 rounded"
                      >
                        {kw}
                      </span>
                    ))}
                    {source.keywords.length > 4 && (
                      <span className="text-xs text-muted-foreground">
                        +{source.keywords.length - 4} more
                      </span>
                    )}
                  </div>
                  <div className="flex items-center justify-between">
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline"
                    >
                      Visit Source →
                    </a>
                    {source.hit_count > 0 && (
                      <span className="text-xs text-muted-foreground">
                        {source.hit_count} citations
                      </span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {displaySources.length === 0 && (
            <div className="text-center py-12 text-muted-foreground">
              {searchQuery.length >= 2
                ? "No sources found matching your search."
                : "No sources in this category yet."}
            </div>
          )}
        </div>
      </div>

      {/* Stats Footer */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between text-sm text-muted-foreground">
            <span>
              {library?.categories.reduce((sum, c) => sum + c.sources.length, 0)} sources across{" "}
              {library?.categories.length} categories
            </span>
            <span>Version {library?.version} • Last updated: {library?.last_updated}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
