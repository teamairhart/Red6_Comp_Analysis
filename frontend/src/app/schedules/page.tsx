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
import { API_BASE } from "@/lib/api";

interface ScheduleConfig {
  frequency: string;
  time_of_day: string;
  days_of_week: string[];
  day_of_month: number;
  timezone: string;
}

interface Schedule {
  id: string;
  name: string;
  description?: string;
  status: "active" | "paused" | "disabled";
  company: string;
  prompt_id: string;
  providers: string[];
  mode: string;
  config: ScheduleConfig;
  created_at: string;
  updated_at: string;
  last_run_at?: string;
  next_run_at?: string;
  run_count: number;
  run_delta_analysis: boolean;
  notify_on_complete: boolean;
  notify_on_critical: boolean;
}

interface Prompt {
  id: string;
  name: string;
  category: string;
}

const FREQUENCY_LABELS: Record<string, string> = {
  daily: "Daily",
  weekly: "Weekly",
  biweekly: "Bi-weekly",
  monthly: "Monthly",
};

const STATUS_STYLES: Record<string, string> = {
  active: "bg-green-100 text-green-800",
  paused: "bg-yellow-100 text-yellow-800",
  disabled: "bg-gray-100 text-gray-600",
};

const DAYS_OF_WEEK = [
  { value: "monday", label: "Mon" },
  { value: "tuesday", label: "Tue" },
  { value: "wednesday", label: "Wed" },
  { value: "thursday", label: "Thu" },
  { value: "friday", label: "Fri" },
  { value: "saturday", label: "Sat" },
  { value: "sunday", label: "Sun" },
];

export default function SchedulesPage() {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [saving, setSaving] = useState(false);

  // New schedule form state
  const [newSchedule, setNewSchedule] = useState({
    name: "",
    description: "",
    company: "",
    prompt_id: "",
    providers: ["xai", "google"],
    mode: "basic",
    frequency: "weekly",
    time_of_day: "09:00",
    days_of_week: ["monday"],
    day_of_month: 1,
    run_delta_analysis: true,
    notify_on_complete: true,
    notify_on_critical: true,
  });

  useEffect(() => {
    fetchSchedules();
    fetchPrompts();
  }, []);

  async function fetchSchedules() {
    try {
      const res = await fetch(`${API_BASE}/api/schedules`);
      if (!res.ok) throw new Error("Failed to fetch schedules");
      const data = await res.json();
      setSchedules(data);
    } catch (err) {
      setError("Failed to load schedules. Is the API running?");
    } finally {
      setLoading(false);
    }
  }

  async function fetchPrompts() {
    try {
      const res = await fetch(`${API_BASE}/api/prompts`);
      if (!res.ok) throw new Error("Failed to fetch prompts");
      const data = await res.json();
      setPrompts(data.prompts || []);
    } catch (err) {
      console.error("Failed to load prompts:", err);
    }
  }

  async function handleCreateSchedule() {
    setSaving(true);
    try {
      const res = await fetch(`${API_BASE}/api/schedules`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: newSchedule.name,
          description: newSchedule.description || null,
          company: newSchedule.company,
          prompt_id: newSchedule.prompt_id,
          providers: newSchedule.providers,
          mode: newSchedule.mode,
          config: {
            frequency: newSchedule.frequency,
            time_of_day: newSchedule.time_of_day,
            days_of_week: newSchedule.days_of_week,
            day_of_month: newSchedule.day_of_month,
            timezone: "America/New_York",
          },
          run_delta_analysis: newSchedule.run_delta_analysis,
          notify_on_complete: newSchedule.notify_on_complete,
          notify_on_critical: newSchedule.notify_on_critical,
        }),
      });

      if (!res.ok) throw new Error("Failed to create schedule");

      // Reset form and close dialog
      setNewSchedule({
        name: "",
        description: "",
        company: "",
        prompt_id: "",
        providers: ["xai", "google"],
        mode: "basic",
        frequency: "weekly",
        time_of_day: "09:00",
        days_of_week: ["monday"],
        day_of_month: 1,
        run_delta_analysis: true,
        notify_on_complete: true,
        notify_on_critical: true,
      });
      setDialogOpen(false);
      fetchSchedules();
    } catch (err) {
      console.error("Failed to create schedule:", err);
    } finally {
      setSaving(false);
    }
  }

  async function handlePauseResume(schedule: Schedule) {
    const endpoint = schedule.status === "active" ? "pause" : "resume";
    try {
      await fetch(`${API_BASE}/api/schedules/${schedule.id}/${endpoint}`, {
        method: "POST",
      });
      fetchSchedules();
    } catch (err) {
      console.error(`Failed to ${endpoint} schedule:`, err);
    }
  }

  async function handleRunNow(scheduleId: string) {
    try {
      await fetch(`${API_BASE}/api/schedules/${scheduleId}/run`, {
        method: "POST",
      });
      fetchSchedules();
    } catch (err) {
      console.error("Failed to trigger schedule:", err);
    }
  }

  async function handleDelete(scheduleId: string) {
    if (!confirm("Are you sure you want to delete this schedule?")) return;

    try {
      await fetch(`${API_BASE}/api/schedules/${scheduleId}`, {
        method: "DELETE",
      });
      fetchSchedules();
    } catch (err) {
      console.error("Failed to delete schedule:", err);
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-muted-foreground">Loading schedules...</p>
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
          <h1 className="text-3xl font-bold tracking-tight">Scheduled Research</h1>
          <p className="text-muted-foreground">
            Automate recurring competitive intelligence research
          </p>
        </div>

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button>New Schedule</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-[600px]">
            <DialogHeader>
              <DialogTitle>Create Research Schedule</DialogTitle>
              <DialogDescription>
                Set up automated research that runs on a recurring schedule.
              </DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
              <div className="grid gap-2">
                <Label htmlFor="name">Schedule Name</Label>
                <Input
                  id="name"
                  value={newSchedule.name}
                  onChange={(e) =>
                    setNewSchedule({ ...newSchedule, name: e.target.value })
                  }
                  placeholder="e.g., Weekly Competitor Update"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="company">Company</Label>
                <Input
                  id="company"
                  value={newSchedule.company}
                  onChange={(e) =>
                    setNewSchedule({ ...newSchedule, company: e.target.value })
                  }
                  placeholder="Company name"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="prompt">Research Prompt</Label>
                <Select
                  value={newSchedule.prompt_id}
                  onValueChange={(v) =>
                    setNewSchedule({ ...newSchedule, prompt_id: v })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a prompt" />
                  </SelectTrigger>
                  <SelectContent>
                    {prompts.map((prompt) => (
                      <SelectItem key={prompt.id} value={prompt.id}>
                        {prompt.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label htmlFor="frequency">Frequency</Label>
                  <Select
                    value={newSchedule.frequency}
                    onValueChange={(v) =>
                      setNewSchedule({ ...newSchedule, frequency: v })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="biweekly">Bi-weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid gap-2">
                  <Label htmlFor="time">Time of Day</Label>
                  <Input
                    id="time"
                    type="time"
                    value={newSchedule.time_of_day}
                    onChange={(e) =>
                      setNewSchedule({ ...newSchedule, time_of_day: e.target.value })
                    }
                  />
                </div>
              </div>

              {(newSchedule.frequency === "weekly" ||
                newSchedule.frequency === "biweekly") && (
                <div className="grid gap-2">
                  <Label>Days of Week</Label>
                  <div className="flex flex-wrap gap-2">
                    {DAYS_OF_WEEK.map((day) => (
                      <button
                        key={day.value}
                        type="button"
                        onClick={() => {
                          const days = newSchedule.days_of_week.includes(day.value)
                            ? newSchedule.days_of_week.filter((d) => d !== day.value)
                            : [...newSchedule.days_of_week, day.value];
                          setNewSchedule({ ...newSchedule, days_of_week: days });
                        }}
                        className={`px-3 py-1 rounded-md text-sm ${
                          newSchedule.days_of_week.includes(day.value)
                            ? "bg-primary text-primary-foreground"
                            : "bg-muted"
                        }`}
                      >
                        {day.label}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {newSchedule.frequency === "monthly" && (
                <div className="grid gap-2">
                  <Label htmlFor="dayOfMonth">Day of Month</Label>
                  <Select
                    value={String(newSchedule.day_of_month)}
                    onValueChange={(v) =>
                      setNewSchedule({ ...newSchedule, day_of_month: parseInt(v) })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {Array.from({ length: 28 }, (_, i) => i + 1).map((day) => (
                        <SelectItem key={day} value={String(day)}>
                          {day}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              )}

              <div className="grid gap-2">
                <Label htmlFor="mode">Research Mode</Label>
                <Select
                  value={newSchedule.mode}
                  onValueChange={(v) =>
                    setNewSchedule({ ...newSchedule, mode: v })
                  }
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="basic">Basic</SelectItem>
                    <SelectItem value="deep">Deep</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Options</Label>
                <div className="space-y-2">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={newSchedule.run_delta_analysis}
                      onChange={(e) =>
                        setNewSchedule({
                          ...newSchedule,
                          run_delta_analysis: e.target.checked,
                        })
                      }
                      className="rounded"
                    />
                    Run delta analysis after completion
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={newSchedule.notify_on_complete}
                      onChange={(e) =>
                        setNewSchedule({
                          ...newSchedule,
                          notify_on_complete: e.target.checked,
                        })
                      }
                      className="rounded"
                    />
                    Notify when complete
                  </label>
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={newSchedule.notify_on_critical}
                      onChange={(e) =>
                        setNewSchedule({
                          ...newSchedule,
                          notify_on_critical: e.target.checked,
                        })
                      }
                      className="rounded"
                    />
                    Notify on critical findings
                  </label>
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>
                Cancel
              </Button>
              <Button
                onClick={handleCreateSchedule}
                disabled={
                  saving ||
                  !newSchedule.name ||
                  !newSchedule.company ||
                  !newSchedule.prompt_id
                }
              >
                {saving ? "Creating..." : "Create Schedule"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Active Schedules</CardDescription>
            <CardTitle className="text-2xl text-green-600">
              {schedules.filter((s) => s.status === "active").length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Paused</CardDescription>
            <CardTitle className="text-2xl text-yellow-600">
              {schedules.filter((s) => s.status === "paused").length}
            </CardTitle>
          </CardHeader>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardDescription>Total Runs</CardDescription>
            <CardTitle className="text-2xl">
              {schedules.reduce((sum, s) => sum + s.run_count, 0)}
            </CardTitle>
          </CardHeader>
        </Card>
      </div>

      {/* Schedules List */}
      {schedules.length > 0 ? (
        <div className="space-y-4">
          {schedules.map((schedule) => (
            <Card key={schedule.id}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="text-lg flex items-center gap-2">
                      {schedule.name}
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${STATUS_STYLES[schedule.status]}`}
                      >
                        {schedule.status}
                      </span>
                    </CardTitle>
                    <CardDescription>
                      {schedule.company} - {schedule.prompt_id.replace(/_/g, " ")}
                    </CardDescription>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePauseResume(schedule)}
                    >
                      {schedule.status === "active" ? "Pause" : "Resume"}
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRunNow(schedule.id)}
                    >
                      Run Now
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-red-600"
                      onClick={() => handleDelete(schedule.id)}
                    >
                      Delete
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-4 gap-4 text-sm">
                  <div>
                    <span className="text-muted-foreground">Frequency:</span>
                    <p className="font-medium">
                      {FREQUENCY_LABELS[schedule.config.frequency]} at{" "}
                      {schedule.config.time_of_day}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Last Run:</span>
                    <p className="font-medium">
                      {schedule.last_run_at
                        ? new Date(schedule.last_run_at).toLocaleDateString()
                        : "Never"}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Next Run:</span>
                    <p className="font-medium">
                      {schedule.next_run_at
                        ? new Date(schedule.next_run_at).toLocaleString()
                        : "N/A"}
                    </p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Total Runs:</span>
                    <p className="font-medium">{schedule.run_count}</p>
                  </div>
                </div>
                <div className="mt-3 flex gap-2 text-xs">
                  {schedule.run_delta_analysis && (
                    <span className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded">
                      Delta Analysis
                    </span>
                  )}
                  {schedule.notify_on_complete && (
                    <span className="px-2 py-0.5 bg-green-100 text-green-800 rounded">
                      Notifications
                    </span>
                  )}
                  {schedule.notify_on_critical && (
                    <span className="px-2 py-0.5 bg-red-100 text-red-800 rounded">
                      Critical Alerts
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card>
          <CardContent className="pt-6 text-center">
            <p className="text-muted-foreground">
              No schedules yet. Create your first automated research schedule.
            </p>
            <Button className="mt-4" onClick={() => setDialogOpen(true)}>
              Create Schedule
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
