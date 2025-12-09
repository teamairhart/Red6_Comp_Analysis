"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import Link from "next/link";

interface DeltaFinding {
  id: string;
  report_id: string;
  company: string;
  finding_text: string;
  finding_type: "NEW" | "UPDATED" | "CONTRADICTED";
  confidence: "HIGH" | "MEDIUM" | "LOW";
  importance: "CRITICAL" | "NOTABLE" | "MINOR";
  category?: string;
  event_date?: string;
  previous_text?: string;
  source_url?: string;
  created_at: string;
  // Enhanced context fields
  importance_reasoning?: string;
  competitive_impact?: string;
  supporting_evidence?: string[];
  source_urls?: string[];
  confidence_reasoning?: string;
  action_items?: string[];
}

interface FindingDetailModalProps {
  finding: DeltaFinding | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const IMPORTANCE_STYLES = {
  CRITICAL: "bg-red-100 text-red-800 border-red-300",
  NOTABLE: "bg-yellow-100 text-yellow-800 border-yellow-300",
  MINOR: "bg-gray-100 text-gray-700 border-gray-300",
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

const TYPE_DESCRIPTIONS = {
  NEW: "This is new intelligence not found in previous reports.",
  UPDATED: "This updates previously known information.",
  CONTRADICTED: "This contradicts information from previous reports.",
};

const CONFIDENCE_STYLES = {
  HIGH: "text-green-600",
  MEDIUM: "text-yellow-600",
  LOW: "text-gray-500",
};

export function FindingDetailModal({
  finding,
  open,
  onOpenChange,
}: FindingDetailModalProps) {
  if (!finding) return null;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center gap-2 flex-wrap">
            <span
              className={cn(
                "px-2 py-1 rounded text-xs font-semibold",
                IMPORTANCE_STYLES[finding.importance]
              )}
            >
              {finding.importance}
            </span>
            <span
              className={cn(
                "px-2 py-1 rounded text-xs font-medium",
                TYPE_STYLES[finding.finding_type]
              )}
            >
              {TYPE_LABELS[finding.finding_type]}
            </span>
            {finding.category && (
              <span className="px-2 py-1 rounded text-xs bg-muted text-muted-foreground">
                {finding.category}
              </span>
            )}
          </div>
          <DialogTitle className="text-xl mt-2">{finding.company}</DialogTitle>
          <DialogDescription>
            {TYPE_DESCRIPTIONS[finding.finding_type]}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 mt-4">
          {/* Main Finding */}
          <div className="space-y-2">
            <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
              Finding
            </h4>
            <p className="text-base leading-relaxed">{finding.finding_text}</p>
          </div>

          {/* Why This Matters - Key new section */}
          {finding.importance_reasoning && (
            <div className="space-y-2 p-4 bg-amber-50 dark:bg-amber-950/30 rounded-lg border border-amber-200 dark:border-amber-800">
              <h4 className="text-sm font-semibold text-amber-800 dark:text-amber-200 uppercase tracking-wider flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="16" x2="12" y2="12" />
                  <line x1="12" y1="8" x2="12.01" y2="8" />
                </svg>
                Why This Matters
              </h4>
              <p className="text-sm text-amber-900 dark:text-amber-100">{finding.importance_reasoning}</p>
            </div>
          )}

          {/* Competitive Impact */}
          {finding.competitive_impact && (
            <div className="space-y-2 p-4 bg-blue-50 dark:bg-blue-950/30 rounded-lg border border-blue-200 dark:border-blue-800">
              <h4 className="text-sm font-semibold text-blue-800 dark:text-blue-200 uppercase tracking-wider flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
                  <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
                </svg>
                Competitive Impact
              </h4>
              <p className="text-sm text-blue-900 dark:text-blue-100">{finding.competitive_impact}</p>
            </div>
          )}

          {/* Supporting Evidence */}
          {finding.supporting_evidence && finding.supporting_evidence.length > 0 && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                  <polyline points="10 9 9 9 8 9" />
                </svg>
                Supporting Evidence
              </h4>
              <ul className="space-y-2">
                {finding.supporting_evidence.map((evidence, idx) => (
                  <li key={idx} className="p-3 bg-muted/50 rounded-lg border-l-2 border-green-500">
                    <p className="text-sm italic">&ldquo;{evidence}&rdquo;</p>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Previous Text (for updates/contradictions) */}
          {finding.previous_text && (
            <div className="space-y-2">
              <h4 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                Previous Information
              </h4>
              <div className="p-3 bg-muted/50 rounded-lg border border-dashed">
                <p className="text-sm text-muted-foreground italic">
                  {finding.previous_text}
                </p>
              </div>
            </div>
          )}

          {/* Suggested Action Items */}
          {finding.action_items && finding.action_items.length > 0 && (
            <div className="space-y-2 p-4 bg-green-50 dark:bg-green-950/30 rounded-lg border border-green-200 dark:border-green-800">
              <h4 className="text-sm font-semibold text-green-800 dark:text-green-200 uppercase tracking-wider flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M9 11l3 3L22 4" />
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11" />
                </svg>
                Suggested Actions
              </h4>
              <ul className="space-y-1">
                {finding.action_items.map((action, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-sm text-green-900 dark:text-green-100">
                    <span className="text-green-600 mt-1">
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                        <polyline points="9 11 12 14 22 4" />
                      </svg>
                    </span>
                    {action}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t">
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                Confidence
              </h4>
              <p className={cn("text-sm font-medium", CONFIDENCE_STYLES[finding.confidence])}>
                {finding.confidence}
              </p>
              {finding.confidence_reasoning && (
                <p className="text-xs text-muted-foreground mt-1">{finding.confidence_reasoning}</p>
              )}
            </div>

            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                Detected
              </h4>
              <p className="text-sm">
                {new Date(finding.created_at).toLocaleDateString("en-US", {
                  year: "numeric",
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </p>
            </div>

            {finding.event_date && (
              <div>
                <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                  Event Date
                </h4>
                <p className="text-sm">
                  {new Date(finding.event_date).toLocaleDateString("en-US", {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </p>
              </div>
            )}

            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">
                Report ID
              </h4>
              <p className="text-xs font-mono text-muted-foreground truncate">
                {finding.report_id}
              </p>
            </div>
          </div>

          {/* Source URLs - Enhanced to show multiple */}
          {(finding.source_urls?.length || finding.source_url) && (
            <div className="pt-4 border-t">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-2">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
                </svg>
                Sources ({finding.source_urls?.length || 1})
              </h4>
              <ul className="space-y-2">
                {(finding.source_urls || [finding.source_url]).filter(Boolean).map((url, idx) => (
                  <li key={idx}>
                    <a
                      href={url!}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline break-all flex items-center gap-1"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="flex-shrink-0">
                        <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                        <polyline points="15 3 21 3 21 9" />
                        <line x1="10" y1="14" x2="21" y2="3" />
                      </svg>
                      {url}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-4 border-t">
            <Link href={`/briefing/company/${encodeURIComponent(finding.company)}`}>
              <Button variant="outline" size="sm">
                View {finding.company} Timeline
              </Button>
            </Link>
            {(finding.source_urls?.[0] || finding.source_url) && (
              <a
                href={finding.source_urls?.[0] || finding.source_url}
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="outline" size="sm">
                  Open Primary Source
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="ml-1"
                  >
                    <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                    <polyline points="15 3 21 3 21 9" />
                    <line x1="10" y1="14" x2="21" y2="3" />
                  </svg>
                </Button>
              </a>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onOpenChange(false)}
              className="ml-auto"
            >
              Close
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
