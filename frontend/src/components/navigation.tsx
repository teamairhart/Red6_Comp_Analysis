"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/", label: "Dashboard", icon: "dashboard" },
  { href: "/reports", label: "Reports", icon: "reports" },
  { href: "/briefing", label: "Briefing", icon: "briefing" },
  { href: "/prompts", label: "Prompts", icon: "prompts" },
];

const API_BASE = "http://localhost:8000";

interface Notification {
  id: string;
  type: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

interface ActiveJob {
  id: string;
  company: string;
  status: string;
  progress: number;
}

export function Navigation() {
  const pathname = usePathname();
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [activeJobs, setActiveJobs] = useState<ActiveJob[]>([]);

  useEffect(() => {
    fetchNotifications();
    fetchActiveJobs();
    const notifInterval = setInterval(fetchNotifications, 30000);
    const jobsInterval = setInterval(fetchActiveJobs, 3000);
    return () => {
      clearInterval(notifInterval);
      clearInterval(jobsInterval);
    };
  }, []);

  async function fetchActiveJobs() {
    try {
      const res = await fetch(`${API_BASE}/api/research`);
      if (res.ok) {
        const data = await res.json();
        setActiveJobs(data.filter((j: ActiveJob) => j.status === "running" || j.status === "pending"));
      }
    } catch {
      // Silent fail
    }
  }

  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  async function fetchNotifications() {
    try {
      const [countRes, notifRes] = await Promise.all([
        fetch(`${API_BASE}/api/schedules/notifications/count`),
        fetch(`${API_BASE}/api/schedules/notifications/all?limit=5`),
      ]);
      if (countRes.ok) {
        const data = await countRes.json();
        setUnreadCount(data.unread_count);
      }
      if (notifRes.ok) {
        const data = await notifRes.json();
        setNotifications(data);
      }
    } catch {
      // Silent fail for notifications
    }
  }

  async function markAllRead() {
    try {
      await fetch(`${API_BASE}/api/schedules/notifications/read-all`, {
        method: "POST",
      });
      setUnreadCount(0);
      setNotifications(notifications.map((n) => ({ ...n, is_read: true })));
    } catch (err) {
      console.error("Failed to mark notifications as read:", err);
    }
  }

  return (
    <header className="border-b border-neutral-200 dark:border-neutral-800 bg-white dark:bg-neutral-950 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4 lg:px-6">
        <div className="flex h-16 items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center gap-6 lg:gap-10">
            <Link href="/" className="flex items-center gap-3 group">
              {/* Red 6 Logo Mark */}
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-red-700 rounded-lg flex items-center justify-center shadow-lg shadow-red-500/20 group-hover:shadow-red-500/40 transition-shadow">
                  <span className="text-white font-black text-lg tracking-tighter">R6</span>
                </div>
                {activeJobs.length > 0 && (
                  <span className="absolute -top-1 -right-1 flex h-4 w-4">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                    <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 text-white text-[9px] font-bold items-center justify-center">
                      {activeJobs.length}
                    </span>
                  </span>
                )}
              </div>
              <div className="hidden sm:block">
                <div className="text-lg font-bold tracking-tight text-neutral-900 dark:text-white">
                  Red 6
                </div>
                <div className="text-xs font-medium text-neutral-500 dark:text-neutral-400 -mt-0.5 tracking-wide uppercase">
                  Competitive Intel
                </div>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 relative",
                    pathname === item.href
                      ? "bg-red-600 text-white shadow-md shadow-red-500/25"
                      : "text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-white hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          {/* Right Side Actions */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Notification Bell */}
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className={cn(
                  "relative p-2.5 rounded-lg transition-colors",
                  showDropdown
                    ? "bg-red-100 dark:bg-red-900/30 text-red-600"
                    : "hover:bg-neutral-100 dark:hover:bg-neutral-800 text-neutral-600 dark:text-neutral-400"
                )}
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
                  <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
                </svg>
                {unreadCount > 0 && (
                  <span className="absolute -top-0.5 -right-0.5 bg-red-600 text-white text-[10px] font-bold rounded-full min-w-[18px] h-[18px] flex items-center justify-center px-1 shadow-lg">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </button>

              {showDropdown && (
                <div className="absolute right-0 mt-2 w-80 bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl shadow-xl shadow-neutral-200/50 dark:shadow-black/50 z-50 overflow-hidden">
                  <div className="p-4 border-b border-neutral-200 dark:border-neutral-800 flex justify-between items-center bg-neutral-50 dark:bg-neutral-900">
                    <span className="font-semibold text-neutral-900 dark:text-white">Notifications</span>
                    {unreadCount > 0 && (
                      <button
                        onClick={markAllRead}
                        className="text-xs font-medium text-red-600 hover:text-red-700 dark:text-red-500 dark:hover:text-red-400"
                      >
                        Mark all read
                      </button>
                    )}
                  </div>
                  <div className="max-h-80 overflow-y-auto">
                    {notifications.length > 0 ? (
                      notifications.map((notif) => (
                        <div
                          key={notif.id}
                          className={cn(
                            "p-4 border-b border-neutral-100 dark:border-neutral-800 last:border-b-0 hover:bg-neutral-50 dark:hover:bg-neutral-800/50 transition-colors",
                            !notif.is_read && "bg-red-50/50 dark:bg-red-950/20"
                          )}
                        >
                          <div className="flex items-start gap-3">
                            <span
                              className={cn(
                                "mt-1.5 w-2 h-2 rounded-full flex-shrink-0",
                                notif.type === "critical_finding"
                                  ? "bg-red-500"
                                  : notif.type === "error"
                                  ? "bg-amber-500"
                                  : "bg-emerald-500"
                              )}
                            />
                            <div className="min-w-0 flex-1">
                              <p className="text-sm font-medium text-neutral-900 dark:text-white truncate">{notif.title}</p>
                              <p className="text-sm text-neutral-600 dark:text-neutral-400 line-clamp-2 mt-0.5">
                                {notif.message}
                              </p>
                              <p className="text-xs text-neutral-500 dark:text-neutral-500 mt-1.5">
                                {new Date(notif.created_at).toLocaleString()}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-8 text-center">
                        <div className="w-12 h-12 bg-neutral-100 dark:bg-neutral-800 rounded-full flex items-center justify-center mx-auto mb-3">
                          <svg className="w-6 h-6 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                          </svg>
                        </div>
                        <p className="text-sm text-neutral-500 dark:text-neutral-400">No notifications</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Divider */}
            <div className="hidden sm:block w-px h-6 bg-neutral-200 dark:bg-neutral-800" />

            {/* Theme Toggle */}
            <ThemeToggle />

            {/* API Status */}
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="text-xs font-medium text-emerald-700 dark:text-emerald-400">API Connected</span>
            </div>

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden h-10 w-10"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <path d="M18 6 6 18" />
                  <path d="m6 6 12 12" />
                </svg>
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="4" x2="20" y1="12" y2="12" />
                  <line x1="4" x2="20" y1="6" y2="6" />
                  <line x1="4" x2="20" y1="18" y2="18" />
                </svg>
              )}
              <span className="sr-only">Toggle menu</span>
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {mobileMenuOpen && (
          <nav className="lg:hidden py-4 border-t border-neutral-200 dark:border-neutral-800">
            <div className="flex flex-col gap-1">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "px-4 py-3 rounded-lg text-base font-medium transition-all flex items-center justify-between",
                    pathname === item.href
                      ? "bg-red-600 text-white"
                      : "text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800"
                  )}
                >
                  {item.label}
                  {item.href === "/" && activeJobs.length > 0 && (
                    <span className="flex items-center gap-2 text-xs">
                      <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
                      </span>
                      {activeJobs.length} running
                    </span>
                  )}
                </Link>
              ))}
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
