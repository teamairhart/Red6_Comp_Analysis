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

interface Report {
  id: string;
  company: string;
  prompt_name: string;
  provider: string;
  date: string;
  filename: string;
  content: string;
}

const API_BASE = "http://localhost:8000";

export default function ReportDetailPage() {
  const params = useParams();
  const reportId = params.id as string;

  const [report, setReport] = useState<Report | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!reportId) return;

    async function fetchReport() {
      try {
        const res = await fetch(`${API_BASE}/api/reports/${reportId}`);
        if (!res.ok) {
          if (res.status === 404) {
            setError("Report not found");
          } else {
            throw new Error("Failed to fetch report");
          }
          return;
        }
        const data = await res.json();
        setReport(data);
      } catch (err) {
        setError("Failed to load report. Is the API running?");
      } finally {
        setLoading(false);
      }
    }

    fetchReport();
  }, [reportId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading report...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        <Card>
          <CardContent className="pt-6">
            <p className="text-red-500">{error}</p>
            <Link href="/reports">
              <Button className="mt-4">Back to Reports</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!report) {
    return null;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{report.company}</h1>
          <p className="text-muted-foreground">
            {report.prompt_name} - {report.provider}
          </p>
          <p className="text-sm text-muted-foreground mt-1">
            {new Date(report.date).toLocaleDateString("en-US", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </p>
        </div>
        <div className="flex gap-2">
          <a
            href={`${API_BASE}/api/reports/${report.id}/download`}
            download
          >
            <Button>Download</Button>
          </a>
          <Link href="/reports">
            <Button variant="outline">Back to Reports</Button>
          </Link>
        </div>
      </div>

      {/* Report content */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Report Content</CardTitle>
          <CardDescription>
            {report.content.length.toLocaleString()} characters
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <pre className="whitespace-pre-wrap text-sm bg-muted p-4 rounded-md overflow-auto max-h-[70vh]">
              {report.content}
            </pre>
          </div>
        </CardContent>
      </Card>

      {/* Actions */}
      <div className="flex gap-4">
        <Link href="/research">
          <Button variant="outline">New Research</Button>
        </Link>
        <Link href="/reports">
          <Button variant="ghost">View All Reports</Button>
        </Link>
      </div>
    </div>
  );
}
