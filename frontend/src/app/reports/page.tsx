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
import { Input } from "@/components/ui/input";

interface Report {
  id: string;
  company: string;
  prompt_name: string;
  provider: string;
  date: string;
  filename: string;
}

const API_BASE = "http://localhost:8000";

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchReports();
  }, []);

  async function fetchReports() {
    try {
      const res = await fetch(`${API_BASE}/api/reports`);
      if (!res.ok) throw new Error("Failed to fetch reports");
      const data = await res.json();
      setReports(data.reports);
    } catch (err) {
      setError("Failed to load reports. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  const filteredReports = reports.filter(
    (report) =>
      report.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.prompt_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      report.provider.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const groupedReports = filteredReports.reduce(
    (acc, report) => {
      const date = report.date;
      if (!acc[date]) {
        acc[date] = [];
      }
      acc[date].push(report);
      return acc;
    },
    {} as Record<string, Report[]>
  );

  const sortedDates = Object.keys(groupedReports).sort(
    (a, b) => new Date(b).getTime() - new Date(a).getTime()
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading reports...</p>
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
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground">
            Browse and download completed research reports
          </p>
        </div>
        <Link href="/research">
          <Button>New Research</Button>
        </Link>
      </div>

      <div className="max-w-md">
        <Input
          placeholder="Search reports..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {reports.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-muted-foreground text-center">
              No reports found. Start a new research to generate reports.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-8">
          {sortedDates.map((date) => (
            <div key={date} className="space-y-4">
              <h2 className="text-lg font-semibold text-muted-foreground">
                {new Date(date).toLocaleDateString("en-US", {
                  weekday: "long",
                  year: "numeric",
                  month: "long",
                  day: "numeric",
                })}
              </h2>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {groupedReports[date].map((report) => (
                  <Card key={report.id}>
                    <CardHeader className="pb-2">
                      <CardTitle className="text-base">{report.company}</CardTitle>
                      <CardDescription>{report.prompt_name}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          {report.provider}
                        </span>
                        <div className="flex gap-2">
                          <Link href={`/reports/${report.id}`}>
                            <Button variant="outline" size="sm">
                              View
                            </Button>
                          </Link>
                          <a
                            href={`${API_BASE}/api/reports/${report.id}/download`}
                            download
                          >
                            <Button variant="ghost" size="sm">
                              Download
                            </Button>
                          </a>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
