"use client";

import { useState, useEffect } from "react";
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

interface DeltaSummary {
  total_findings: number;
  critical_count: number;
  notable_count: number;
  minor_count: number;
  new_count: number;
  updated_count: number;
  contradicted_count: number;
}

interface BriefingData {
  period_days: number;
  summary: DeltaSummary;
  critical_findings: DeltaFinding[];
  findings_by_company: Record<string, DeltaFinding[]>;
  recent_reports: any[];
}

const API_BASE = "http://localhost:8000";

const IMPORTANCE_STYLES = {
  CRITICAL: "bg-red-100 text-red-800 border-red-200",
  NOTABLE: "bg-yellow-100 text-yellow-800 border-yellow-200",
  MINOR: "bg-gray-100 text-gray-700 border-gray-200",
};

const TYPE_STYLES = {
  NEW: "bg-green-100 text-green-800",
  UPDATED: "bg-blue-100 text-blue-800",
  CONTRADICTED: "bg-orange-100 text-orange-800",
};

const TYPE_ICONS = {
  NEW: "+",
  UPDATED: "~",
  CONTRADICTED: "!",
};

export default function BriefingPage() {
  const [briefing, setBriefing] = useState<BriefingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [periodDays, setPeriodDays] = useState("7");

  useEffect(() => {
    fetchBriefing(parseInt(periodDays));
  }, [periodDays]);

  async function fetchBriefing(days: number) {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/delta/briefing?days=${days}`);
      if (!res.ok) throw new Error("Failed to fetch briefing");
      const data: BriefingData = await res.json();
      setBriefing(data);
      setError(null);
    } catch (err) {
      setError("Failed to load briefing. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading intelligence briefing...</p>
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

  const summary = briefing?.summary;
  const companies = Object.keys(briefing?.findings_by_company || {});

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Intelligence Briefing</h1>
          <p className="text-muted-foreground">
            What&apos;s new in competitive intelligence
          </p>
        </div>

        <div className="flex items-center gap-4">
          <Select value={periodDays} onValueChange={setPeriodDays}>
            <SelectTrigger className="w-[140px]">
              <SelectValue placeholder="Time period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Last 7 days</SelectItem>
              <SelectItem value="14">Last 14 days</SelectItem>
              <SelectItem value="30">Last 30 days</SelectItem>
              <SelectItem value="90">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Findings</CardDescription>
            <CardTitle className="text-3xl">{summary?.total_findings || 0}</CardTitle>
          </CardHeader>
        </Card>
        <Card className={summary?.critical_count ? "border-red-200 bg-red-50/50" : ""}>
          <CardHeader className="pb-2">
            <CardDescription>Critical</CardDescription>
            <CardTitle className="text-3xl text-red-600">
              {summary?.critical_count || 0}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Notable</CardDescription>
            <CardTitle className="text-3xl text-yellow-600">
              {summary?.notable_count || 0}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Companies Tracked</CardDescription>
            <CardTitle className="text-3xl">{companies.length}</CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Type Breakdown */}
      <div className="flex gap-4 text-sm">
        <span className="flex items-center gap-2">
          <span className={`px-2 py-1 rounded ${TYPE_STYLES.NEW}`}>
            {TYPE_ICONS.NEW} New: {summary?.new_count || 0}
          </span>
        </span>
        <span className="flex items-center gap-2">
          <span className={`px-2 py-1 rounded ${TYPE_STYLES.UPDATED}`}>
            {TYPE_ICONS.UPDATED} Updated: {summary?.updated_count || 0}
          </span>
        </span>
        <span className="flex items-center gap-2">
          <span className={`px-2 py-1 rounded ${TYPE_STYLES.CONTRADICTED}`}>
            {TYPE_ICONS.CONTRADICTED} Contradicted: {summary?.contradicted_count || 0}
          </span>
        </span>
      </div>

      {/* Critical Findings Section */}
      {briefing?.critical_findings && briefing.critical_findings.length > 0 && (
        <Card className="border-red-200 bg-red-50/30">
          <CardHeader>
            <CardTitle className="text-lg text-red-800">Critical Updates</CardTitle>
            <CardDescription>
              Findings requiring immediate attention
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {briefing.critical_findings.map((finding) => (
                <div
                  key={finding.id}
                  className="p-4 bg-white rounded-lg border border-red-200"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-medium text-red-700">
                          {finding.company}
                        </span>
                        <span className={`text-xs px-2 py-0.5 rounded ${TYPE_STYLES[finding.finding_type]}`}>
                          {finding.finding_type}
                        </span>
                        {finding.category && (
                          <span className="text-xs text-muted-foreground">
                            {finding.category}
                          </span>
                        )}
                      </div>
                      <p className="text-sm">{finding.finding_text}</p>
                      {finding.previous_text && (
                        <p className="text-xs text-muted-foreground mt-2 italic">
                          Previously: {finding.previous_text}
                        </p>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground whitespace-nowrap">
                      {new Date(finding.created_at).toLocaleDateString()}
                    </div>
                  </div>
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
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Findings by Company */}
      {companies.length > 0 ? (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold">Findings by Company</h2>
          {companies.map((company) => {
            const companyFindings = briefing!.findings_by_company[company];
            const criticalCount = companyFindings.filter(
              (f) => f.importance === "CRITICAL"
            ).length;

            return (
              <Card key={company}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{company}</CardTitle>
                    <div className="flex items-center gap-2">
                      <span className="text-sm text-muted-foreground">
                        {companyFindings.length} findings
                      </span>
                      {criticalCount > 0 && (
                        <span className="text-xs px-2 py-0.5 rounded bg-red-100 text-red-800">
                          {criticalCount} critical
                        </span>
                      )}
                      <Link href={`/briefing/company/${encodeURIComponent(company)}`}>
                        <Button variant="outline" size="sm">
                          View Timeline
                        </Button>
                      </Link>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {companyFindings.slice(0, 5).map((finding) => (
                      <div
                        key={finding.id}
                        className={`p-3 rounded-lg border ${IMPORTANCE_STYLES[finding.importance]}`}
                      >
                        <div className="flex items-start gap-2">
                          <span
                            className={`text-xs px-1.5 py-0.5 rounded font-mono ${TYPE_STYLES[finding.finding_type]}`}
                          >
                            {TYPE_ICONS[finding.finding_type]}
                          </span>
                          <div className="flex-1">
                            <p className="text-sm">{finding.finding_text}</p>
                            <div className="flex items-center gap-2 mt-1">
                              {finding.category && (
                                <span className="text-xs text-muted-foreground">
                                  {finding.category}
                                </span>
                              )}
                              <span className="text-xs text-muted-foreground">
                                {finding.confidence} confidence
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                    {companyFindings.length > 5 && (
                      <p className="text-sm text-muted-foreground text-center pt-2">
                        +{companyFindings.length - 5} more findings
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">
              No findings in the selected time period.
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Run research on companies to generate delta intelligence.
            </p>
            <Link href="/research">
              <Button className="mt-4">Start Research</Button>
            </Link>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
