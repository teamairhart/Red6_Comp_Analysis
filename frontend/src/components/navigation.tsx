"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";

const navItems = [
  { href: "/", label: "Dashboard" },
  { href: "/research", label: "New Research" },
  { href: "/briefing", label: "Briefing" },
  { href: "/schedules", label: "Schedules" },
  { href: "/reports", label: "Reports" },
  { href: "/prompts", label: "Prompts" },
  { href: "/sources", label: "Sources" },
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

export function Navigation() {
  const pathname = usePathname();
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

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
    } catch (err) {
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
    <header className="border-b bg-background sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-4 lg:gap-8">
            <Link href="/" className="flex items-center gap-2">
              <span className="text-xl font-bold">Red 6</span>
              <span className="text-sm text-muted-foreground hidden sm:inline">
                Competitive Intel
              </span>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-6">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "text-sm font-medium transition-colors hover:text-primary",
                    pathname === item.href
                      ? "text-foreground"
                      : "text-muted-foreground"
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-2 sm:gap-4">
            {/* Notification Bell */}
            <div className="relative">
              <button
                onClick={() => setShowDropdown(!showDropdown)}
                className="relative p-2 hover:bg-muted rounded-md"
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
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {unreadCount > 9 ? "9+" : unreadCount}
                  </span>
                )}
              </button>

              {showDropdown && (
                <div className="absolute right-0 mt-2 w-80 bg-background border rounded-lg shadow-lg z-50">
                  <div className="p-3 border-b flex justify-between items-center">
                    <span className="font-medium">Notifications</span>
                    {unreadCount > 0 && (
                      <button
                        onClick={markAllRead}
                        className="text-xs text-blue-600 hover:underline"
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
                            "p-3 border-b last:border-b-0 hover:bg-muted/50",
                            !notif.is_read && "bg-blue-50/50 dark:bg-blue-950/50"
                          )}
                        >
                          <div className="flex items-start gap-2">
                            <span
                              className={cn(
                                "mt-1 w-2 h-2 rounded-full flex-shrink-0",
                                notif.type === "critical_finding"
                                  ? "bg-red-500"
                                  : notif.type === "error"
                                  ? "bg-orange-500"
                                  : "bg-green-500"
                              )}
                            />
                            <div className="min-w-0">
                              <p className="text-sm font-medium truncate">{notif.title}</p>
                              <p className="text-xs text-muted-foreground line-clamp-2">
                                {notif.message}
                              </p>
                              <p className="text-xs text-muted-foreground mt-1">
                                {new Date(notif.created_at).toLocaleString()}
                              </p>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="p-4 text-center text-sm text-muted-foreground">
                        No notifications
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>

            <ThemeToggle />

            <span className="text-sm text-muted-foreground hidden sm:inline">
              API: <span className="text-green-500">Connected</span>
            </span>

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              className="lg:hidden h-9 w-9"
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
          <nav className="lg:hidden py-4 border-t">
            <div className="flex flex-col gap-2">
              {navItems.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    "px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    pathname === item.href
                      ? "bg-muted text-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </nav>
        )}
      </div>
    </header>
  );
}
