"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { cn } from "@/lib/utils";
import { API_BASE } from "@/lib/api";

interface TickerItem {
  id: string;
  headline: string;
  summary: string;
  company: string;
  category: string;
  importance: "critical" | "notable" | "routine";
  source_name?: string;
  source_url?: string;
  relevance_reason: string;
  created_at: string;
}

interface TickerData {
  items: TickerItem[];
  last_updated: string;
  is_stale?: boolean;
}

const IMPORTANCE_STYLES = {
  critical: "bg-red-600 text-white",
  notable: "bg-amber-500 text-white",
  routine: "bg-neutral-500 text-white",
};

const CATEGORY_ICONS: Record<string, string> = {
  contract: "📄",
  executive: "👔",
  technology: "🔬",
  acquisition: "🤝",
  partnership: "🔗",
  financial: "💰",
  product: "📦",
  general: "📰",
};

export function NewsTicker() {
  const [items, setItems] = useState<TickerItem[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  const fetchTicker = useCallback(async (forceRefresh = false) => {
    try {
      // First get current data
      const res = await fetch(`${API_BASE}/api/ticker`);
      if (!res.ok) throw new Error("Failed to fetch ticker");

      const data: TickerData = await res.json();

      // Check if we need to refresh (stale or empty)
      const statusRes = await fetch(`${API_BASE}/api/ticker/status`);
      const status = await statusRes.json();

      if (forceRefresh || status.is_stale || data.items.length === 0) {
        setIsRefreshing(true);
        // Trigger refresh
        const refreshRes = await fetch(`${API_BASE}/api/ticker/refresh`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ force: forceRefresh }),
        });

        if (refreshRes.ok) {
          const refreshedData: TickerData = await refreshRes.json();
          setItems(refreshedData.items);
          setLastUpdated(refreshedData.last_updated);
        }
        setIsRefreshing(false);
      } else {
        setItems(data.items);
        setLastUpdated(data.last_updated);
      }
    } catch (err) {
      console.error("Ticker fetch error:", err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchTicker();
  }, [fetchTicker]);

  // Auto-advance timer
  useEffect(() => {
    if (isPaused || items.length <= 1) return;

    timerRef.current = setInterval(() => {
      setIsVisible(false);
      setTimeout(() => {
        setCurrentIndex((prev) => (prev + 1) % items.length);
        setIsVisible(true);
      }, 300);
    }, 6000);

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPaused, items.length]);

  const goToPrev = useCallback(() => {
    setIsVisible(false);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev - 1 + items.length) % items.length);
      setIsVisible(true);
    }, 200);
  }, [items.length]);

  const goToNext = useCallback(() => {
    setIsVisible(false);
    setTimeout(() => {
      setCurrentIndex((prev) => (prev + 1) % items.length);
      setIsVisible(true);
    }, 200);
  }, [items.length]);

  const goToIndex = useCallback((index: number) => {
    if (index === currentIndex) return;
    setIsVisible(false);
    setTimeout(() => {
      setCurrentIndex(index);
      setIsVisible(true);
    }, 200);
  }, [currentIndex]);

  // Don't render if no items and not loading
  if (!isLoading && items.length === 0) {
    return null;
  }

  const currentItem = items[currentIndex];

  return (
    <div
      className="bg-neutral-900 dark:bg-neutral-950 border-b border-neutral-800"
      onMouseEnter={() => setIsPaused(true)}
      onMouseLeave={() => setIsPaused(false)}
    >
      <div className="container mx-auto px-4">
        <div className="flex items-center h-10 gap-3">
          {/* Intel Label */}
          <div className="flex-shrink-0 flex items-center gap-2">
            <span className="text-red-500 font-bold text-xs tracking-wider uppercase">
              INTEL
            </span>
            <div className="w-px h-4 bg-neutral-700" />
          </div>

          {/* Main Content Area */}
          <div className="flex-1 min-w-0 flex items-center">
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 border-2 border-red-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-neutral-400 text-sm">
                  Loading intelligence feed...
                </span>
              </div>
            ) : isRefreshing ? (
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
                <span className="text-neutral-400 text-sm">
                  Refreshing news feed...
                </span>
              </div>
            ) : currentItem ? (
              <div
                className={cn(
                  "flex items-center gap-3 transition-opacity duration-300 min-w-0",
                  isVisible ? "opacity-100" : "opacity-0"
                )}
              >
                {/* Importance Badge */}
                <span
                  className={cn(
                    "flex-shrink-0 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider",
                    IMPORTANCE_STYLES[currentItem.importance]
                  )}
                >
                  {currentItem.importance}
                </span>

                {/* Category Icon */}
                <span className="flex-shrink-0 text-sm">
                  {CATEGORY_ICONS[currentItem.category] || "📰"}
                </span>

                {/* Company */}
                <span className="flex-shrink-0 text-red-400 font-semibold text-sm">
                  {currentItem.company}
                </span>

                {/* Headline - clickable if source URL available */}
                {currentItem.source_url ? (
                  <a
                    href={currentItem.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-neutral-200 text-sm truncate hover:text-white hover:underline transition-colors cursor-pointer"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {currentItem.headline}
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="inline-block ml-1 opacity-50"
                    >
                      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
                      <polyline points="15 3 21 3 21 9" />
                      <line x1="10" y1="14" x2="21" y2="3" />
                    </svg>
                  </a>
                ) : (
                  <span className="text-neutral-200 text-sm truncate">
                    {currentItem.headline}
                  </span>
                )}

                {/* Relevance (hidden on small screens) */}
                <span className="hidden lg:block flex-shrink-0 text-neutral-500 text-xs italic truncate max-w-xs">
                  {currentItem.relevance_reason}
                </span>
              </div>
            ) : null}
          </div>

          {/* Navigation Controls */}
          {items.length > 1 && (
            <div className="flex-shrink-0 flex items-center gap-2">
              {/* Prev Button */}
              <button
                onClick={goToPrev}
                className="p-1 text-neutral-500 hover:text-white transition-colors"
                aria-label="Previous item"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="m15 18-6-6 6-6" />
                </svg>
              </button>

              {/* Position Indicator */}
              <div className="flex items-center gap-1">
                {items.slice(0, Math.min(items.length, 10)).map((_, idx) => (
                  <button
                    key={idx}
                    onClick={() => goToIndex(idx)}
                    className={cn(
                      "w-1.5 h-1.5 rounded-full transition-all",
                      idx === currentIndex
                        ? "bg-red-500 w-3"
                        : "bg-neutral-600 hover:bg-neutral-400"
                    )}
                    aria-label={`Go to item ${idx + 1}`}
                  />
                ))}
                {items.length > 10 && (
                  <span className="text-neutral-600 text-[10px] ml-1">
                    +{items.length - 10}
                  </span>
                )}
              </div>

              {/* Next Button */}
              <button
                onClick={goToNext}
                className="p-1 text-neutral-500 hover:text-white transition-colors"
                aria-label="Next item"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="m9 18 6-6-6-6" />
                </svg>
              </button>

              {/* Pause Indicator */}
              {isPaused && (
                <span className="text-neutral-500 text-[10px] uppercase tracking-wider ml-1">
                  Paused
                </span>
              )}
            </div>
          )}

          {/* Counter */}
          <div className="hidden sm:flex flex-shrink-0 items-center gap-2 text-neutral-600 text-xs">
            <span>
              {currentIndex + 1}/{items.length}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
