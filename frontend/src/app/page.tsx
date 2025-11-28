"use client";

import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { FadeIn, StaggerChildren, StaggerItem, AnimatedList, AnimatedListItem } from "@/components/animations";

const quickResearchTopics = [
  "Recent News & Press Releases",
  "Financial Performance",
  "Key Personnel Changes",
  "Contract Awards",
  "Technology Investments",
];

const primaryCompetitors = [
  { name: "Lockheed Martin", sector: "Aerospace & Defense" },
  { name: "Northrop Grumman", sector: "Aerospace & Defense" },
  { name: "Boeing", sector: "Aerospace & Defense" },
  { name: "BAE Systems", sector: "Defense" },
  { name: "Raytheon", sector: "Defense Technology" },
  { name: "L3Harris", sector: "Communications & Electronics" },
];

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <FadeIn>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Competitive intelligence research for defense technology
          </p>
        </div>
      </FadeIn>

      <StaggerChildren className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <StaggerItem>
          <Card className="h-full transition-shadow hover:shadow-md">
            <CardHeader>
              <CardTitle>Start New Research</CardTitle>
              <CardDescription>
                Run competitive analysis on a company using AI-powered research
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/research">
                <Button className="w-full">New Research</Button>
              </Link>
            </CardContent>
          </Card>
        </StaggerItem>

        <StaggerItem>
          <Card className="h-full transition-shadow hover:shadow-md">
            <CardHeader>
              <CardTitle>View Reports</CardTitle>
              <CardDescription>
                Browse and download completed research reports
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/reports">
                <Button variant="outline" className="w-full">
                  Browse Reports
                </Button>
              </Link>
            </CardContent>
          </Card>
        </StaggerItem>

        <StaggerItem>
          <Card className="h-full transition-shadow hover:shadow-md">
            <CardHeader>
              <CardTitle>Prompt Library</CardTitle>
              <CardDescription>
                View available research prompts and templates
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Link href="/prompts">
                <Button variant="outline" className="w-full">
                  View Prompts
                </Button>
              </Link>
            </CardContent>
          </Card>
        </StaggerItem>
      </StaggerChildren>

      <div className="grid gap-6 md:grid-cols-2">
        <FadeIn delay={0.2}>
          <Card className="transition-shadow hover:shadow-md">
            <CardHeader>
              <CardTitle>Quick Research Topics</CardTitle>
              <CardDescription>
                Common research areas for competitive intelligence
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AnimatedList className="space-y-2">
                {quickResearchTopics.map((topic) => (
                  <AnimatedListItem key={topic}>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      {topic}
                    </div>
                  </AnimatedListItem>
                ))}
              </AnimatedList>
            </CardContent>
          </Card>
        </FadeIn>

        <FadeIn delay={0.3}>
          <Card className="transition-shadow hover:shadow-md">
            <CardHeader>
              <CardTitle>Primary Competitors</CardTitle>
              <CardDescription>
                Key companies in the defense technology sector
              </CardDescription>
            </CardHeader>
            <CardContent>
              <AnimatedList className="space-y-3">
                {primaryCompetitors.map((company) => (
                  <AnimatedListItem key={company.name}>
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{company.name}</span>
                      <span className="text-muted-foreground">{company.sector}</span>
                    </div>
                  </AnimatedListItem>
                ))}
              </AnimatedList>
            </CardContent>
          </Card>
        </FadeIn>
      </div>
    </div>
  );
}
