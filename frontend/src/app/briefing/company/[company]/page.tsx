"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface DeltaFinding {
  id: string;
  report_id: string;
  company: string;
  finding_text: string;
  finding_type: "NEW" | "UPDATED" | "CONTRADICTED";
  confidence: "HIGH" | "MEDIUM" | "LOW";
  importance: "CRITICAL" | "NOTABLE" | "MINOR";
  category?: string;
  previous_text?: string;
  source_url?: string;
  created_at: string;
}

const API_BASE = "http://localhost:8000";

const IMPORTANCE_STYLES = {
  CRITICAL: "border-l-red-500 bg-red-50/50",
  NOTABLE: "border-l-yellow-500 bg-yellow-50/50",
  MINOR: "border-l-gray-300 bg-gray-50/50",
};

const TYPE_STYLES = {
  NEW: "bg-green-100 text-green-800",
  UPDATED: "bg-blue-100 text-blue-800",
  CONTRADICTED: "bg-orange-100 text-orange-800",
};

const TYPE_LABELS = {
  NEW: "New Information",
  UPDATED: "Updated",
  CONTRADICTED: "Contradicted",
};

const CONFIDENCE_STYLES = {
  HIGH: "text-green-600",
  MEDIUM: "text-yellow-600",
  LOW: "text-gray-500",
};

export default function CompanyTimelinePage() {
  const params = useParams();
  const company = decodeURIComponent(params.company as string);

  const [findings, setFindings] = useState<DeltaFinding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodDays, setPeriodDays] = useState("90");
  const [categoryFilter, setCategoryFilter] = useState("all");

  useEffect(() => {
    fetchTimeline();
  }, [company, periodDays]);

  async function fetchTimeline() {
    setLoading(true);
    try {
      const res = await fetch(
        `${API_BASE}/api/delta/company/${encodeURIComponent(company)}/timeline?days=${periodDays}`
      );
      if (!res.ok) throw new Error("Failed to fetch timeline");
      const data: DeltaFinding[] = await res.json();
      setFindings(data);
      setError(null);
    } catch (err) {
      setError("Failed to load timeline. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  // Get unique categories for filter
  const categories = [...new Set(findings.map((f) => f.category).filter(Boolean))];

  // Apply category filter
  const filteredFindings =
    categoryFilter === "all"
      ? findings
      : findings.filter((f) => f.category === categoryFilter);

  // Group findings by date
  const findingsByDate: Record<string, DeltaFinding[]> = {};
  for (const finding of filteredFindings) {
    const date = new Date(finding.created_at).toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
    if (!findingsByDate[date]) {
      findingsByDate[date] = [];
    }
    findingsByDate[date].push(finding);
  }

  const dates = Object.keys(findingsByDate);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading timeline...</p>
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <Link href="/briefing">
              <Button variant="ghost" size="sm">
                &larr; Briefing
              </Button>
            </Link>
          </div>
          <h1 className="text-3xl font-bold tracking-tight">{company}</h1>
          <p className="text-muted-foreground">
            Intelligence timeline - {findings.length} findings
          </p>
        </div>

        <div className="flex items-center gap-4">
          {categories.length > 0 && (
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((cat) => (
                  <SelectItem key={cat} value={cat!}>
                    {cat}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}

          <Select value={periodDays} onValueChange={setPeriodDays}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Time period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
              <SelectItem value="180">Last 6 months</SelectItem>
              <SelectItem value="365">Last year</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Findings</CardDescription>
            <CardTitle className="text-2xl">{findings.length}</CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Critical</CardDescription>
            <CardTitle className="text-2xl text-red-600">
              {findings.filter((f) => f.importance === "CRITICAL").length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>New Info</CardDescription>
            <CardTitle className="text-2xl text-green-600">
              {findings.filter((f) => f.finding_type === "NEW").length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Updates</CardDescription>
            <CardTitle className="text-2xl text-blue-600">
              {findings.filter((f) => f.finding_type === "UPDATED").length}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Timeline */}
      {dates.length > 0 ? (
        <div className="relative">
          {/* Timeline line */}
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-border" />

          <div className="space-y-8">
            {dates.map((date) => (
              <div key={date} className="relative">
                {/* Date marker */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-8 h-8 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold z-10">
                    {findingsByDate[date].length}
                  </div>
                  <h3 className="font-semibold text-lg">{date}</h3>
                </div>

                {/* Findings for this date */}
                <div className="ml-12 space-y-3">
                  {findingsByDate[date].map((finding) => (
                    <Card
                      key={finding.id}
                      className={`border-l-4 ${IMPORTANCE_STYLES[finding.importance]}`}
                    >
                      <CardContent className="pt-4">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span
                                className={`text-xs px-2 py-0.5 rounded ${TYPE_STYLES[finding.finding_type]}`}
                              >
                                {TYPE_LABELS[finding.finding_type]}
                              </span>
                              {finding.category && (
                                <span className="text-xs bg-muted px-2 py-0.5 rounded">
                                  {finding.category}
                                </span>
                              )}
                              <span
                                className={`text-xs ${CONFIDENCE_STYLES[finding.confidence]}`}
                              >
                                {finding.confidence} confidence
                              </span>
                            </div>

                            <p className="text-sm">{finding.finding_text}</p>

                            {finding.previous_text && (
                              <div className="mt-2 p-2 bg-muted/50 rounded text-xs">
                                <span className="font-medium">Previously:</span>{" "}
                                {finding.previous_text}
                              </div>
                            )}

                            {finding.source_url && (
                              <a
                                href={finding.source_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-xs text-blue-600 hover:underline mt-2 inline-block"
                              >
                                View source
                              </a>
                            )}
                          </div>

                          <div className="text-right">
                            <span
                              className={`text-xs font-medium ${
                                finding.importance === "CRITICAL"
                                  ? "text-red-600"
                                  : finding.importance === "NOTABLE"
                                  ? "text-yellow-600"
                                  : "text-gray-500"
                              }`}
                            >
                              {finding.importance}
                            </span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">
              No findings for {company} in the selected time period.
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Run research on this company to generate delta intelligence.
            </p>
            <Link href="/">
              <Button className="mt-4">Start Research</Button>
            </Link>
          </CardContent>
        </Card>
      )}

      {/* Actions */}
      <div className="flex gap-4">
        <Link href="/briefing">
          <Button variant="outline">Back to Briefing</Button>
        </Link>
        <Link href="/">
          <Button>New Research on {company}</Button>
        </Link>
      </div>
    </div>
  );
}
