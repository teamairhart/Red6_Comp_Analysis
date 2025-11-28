"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface Prompt {
  id: string;
  name: string;
  description: string;
  category: string;
  requires_company: boolean;
}

interface PromptCategory {
  id: string;
  name: string;
  prompts: Prompt[];
}

const API_BASE = "http://localhost:8000";

const STEPS = [
  { id: 1, name: "Company", description: "Select target company" },
  { id: 2, name: "Research Type", description: "Choose research prompt" },
  { id: 3, name: "Providers", description: "Configure AI providers" },
  { id: 4, name: "Review", description: "Confirm and launch" },
];

const PRIORITY_COMPANIES = [
  // Primary Competitors
  { name: "Elbit Systems", sector: "Defense Electronics", primary: true },
  { name: "Thales", sector: "Defense & Aerospace", primary: true },
  { name: "BAE Systems", sector: "Defense & Security", primary: true },
  // Other Competitors
  { name: "Lockheed Martin", sector: "Aerospace & Defense" },
  { name: "Northrop Grumman", sector: "Aerospace & Defense" },
  { name: "Boeing", sector: "Aerospace & Defense" },
  { name: "Raytheon", sector: "Defense Technology" },
  { name: "L3Harris", sector: "Communications" },
];

const PROVIDERS = [
  {
    id: "xai",
    name: "xAI Grok",
    description: "Real-time data from X/Twitter",
    icon: "X",
    color: "bg-black text-white",
  },
  {
    id: "google",
    name: "Google Gemini",
    description: "Comprehensive web search",
    icon: "G",
    color: "bg-blue-500 text-white",
  },
];

export default function ResearchWizard() {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState(1);
  const [company, setCompany] = useState("");
  const [customCompany, setCustomCompany] = useState("");
  const [selectedPrompt, setSelectedPrompt] = useState<Prompt | null>(null);
  const [selectedProviders, setSelectedProviders] = useState<string[]>(["xai", "google"]);
  const [mode, setMode] = useState<"basic" | "deep">("basic");
  const [categories, setCategories] = useState<PromptCategory[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [expandedCategory, setExpandedCategory] = useState<string | null>(null);

  useEffect(() => {
    fetchPrompts();
  }, []);

  async function fetchPrompts() {
    try {
      const res = await fetch(`${API_BASE}/api/prompts`);
      if (!res.ok) throw new Error("Failed to fetch prompts");
      const data = await res.json();
      setCategories(data.categories);
      if (data.categories.length > 0) {
        setExpandedCategory(data.categories[0].id);
      }
    } catch (err) {
      setError("Failed to load prompts. Is the API running?");
    }
  }

  async function handleSubmit() {
    const finalCompany = company || customCompany;
    if (!finalCompany.trim() || !selectedPrompt) {
      setError("Please complete all required fields");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/api/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company: finalCompany.trim(),
          prompt_id: selectedPrompt.id,
          providers: selectedProviders,
          mode,
        }),
      });

      if (!res.ok) throw new Error("Failed to start research");

      const data = await res.json();
      router.push(`/research/${data.job_id}`);
    } catch (err) {
      setError("Failed to start research. Please try again.");
      setLoading(false);
    }
  }

  function toggleProvider(providerId: string) {
    setSelectedProviders((prev) =>
      prev.includes(providerId)
        ? prev.filter((p) => p !== providerId)
        : [...prev, providerId]
    );
  }

  function canProceed() {
    switch (currentStep) {
      case 1:
        return company || customCompany.trim();
      case 2:
        return selectedPrompt !== null;
      case 3:
        return selectedProviders.length > 0;
      case 4:
        return true;
      default:
        return false;
    }
  }

  function nextStep() {
    if (canProceed() && currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  }

  function prevStep() {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  }

  const slideVariants = {
    enter: (direction: number) => ({
      x: direction > 0 ? 300 : -300,
      opacity: 0,
    }),
    center: {
      x: 0,
      opacity: 1,
    },
    exit: (direction: number) => ({
      x: direction < 0 ? 300 : -300,
      opacity: 0,
    }),
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold tracking-tight">New Research</h1>
        <p className="text-muted-foreground mt-2">
          Configure your competitive intelligence research in a few simple steps
        </p>
      </div>

      {/* Progress Steps */}
      <div className="flex justify-between items-center px-8">
        {STEPS.map((step, index) => (
          <div key={step.id} className="flex items-center">
            <div className="flex flex-col items-center">
              <div
                className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all duration-300",
                  currentStep === step.id
                    ? "bg-primary text-primary-foreground scale-110"
                    : currentStep > step.id
                    ? "bg-green-500 text-white"
                    : "bg-muted text-muted-foreground"
                )}
              >
                {currentStep > step.id ? (
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  step.id
                )}
              </div>
              <span
                className={cn(
                  "text-xs mt-2 font-medium",
                  currentStep === step.id ? "text-foreground" : "text-muted-foreground"
                )}
              >
                {step.name}
              </span>
            </div>
            {index < STEPS.length - 1 && (
              <div
                className={cn(
                  "h-0.5 w-16 mx-2 transition-colors duration-300",
                  currentStep > step.id ? "bg-green-500" : "bg-muted"
                )}
              />
            )}
          </div>
        ))}
      </div>

      {/* Step Content */}
      <Card className="min-h-[400px]">
        <AnimatePresence mode="wait" custom={currentStep}>
          <motion.div
            key={currentStep}
            custom={currentStep}
            variants={slideVariants}
            initial="enter"
            animate="center"
            exit="exit"
            transition={{ duration: 0.3, ease: "easeInOut" }}
          >
            {/* Step 1: Company Selection */}
            {currentStep === 1 && (
              <div>
                <CardHeader>
                  <CardTitle>Select Target Company</CardTitle>
                  <CardDescription>
                    Choose a priority competitor or enter a custom company name
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  {/* Primary Competitors */}
                  <div>
                    <div className="text-xs font-semibold text-primary mb-2 uppercase tracking-wide">
                      Primary Competitors
                    </div>
                    <div className="grid grid-cols-3 gap-3">
                      {PRIORITY_COMPANIES.filter((c) => c.primary).map((comp) => (
                        <motion.button
                          key={comp.name}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => {
                            setCompany(comp.name);
                            setCustomCompany("");
                          }}
                          className={cn(
                            "p-4 rounded-lg border-2 text-left transition-all relative",
                            company === comp.name
                              ? "border-primary bg-primary/10 ring-2 ring-primary/20"
                              : "border-primary/30 bg-primary/5 hover:border-primary hover:bg-primary/10"
                          )}
                        >
                          <div className="absolute -top-1 -right-1 w-3 h-3 bg-primary rounded-full" />
                          <div className="font-semibold text-sm">{comp.name}</div>
                          <div className="text-xs text-muted-foreground mt-1">
                            {comp.sector}
                          </div>
                        </motion.button>
                      ))}
                    </div>
                  </div>

                  {/* Other Competitors */}
                  <div>
                    <div className="text-xs font-semibold text-muted-foreground mb-2 uppercase tracking-wide">
                      Other Competitors
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-2">
                      {PRIORITY_COMPANIES.filter((c) => !c.primary).map((comp) => (
                        <motion.button
                          key={comp.name}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => {
                            setCompany(comp.name);
                            setCustomCompany("");
                          }}
                          className={cn(
                            "p-3 rounded-lg border text-left transition-all",
                            company === comp.name
                              ? "border-primary bg-primary/5"
                              : "border-border hover:border-primary/50"
                          )}
                        >
                          <div className="font-medium text-sm">{comp.name}</div>
                          <div className="text-xs text-muted-foreground mt-0.5">
                            {comp.sector}
                          </div>
                        </motion.button>
                      ))}
                    </div>
                  </div>

                  <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                      <span className="w-full border-t" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                      <span className="bg-background px-2 text-muted-foreground">
                        Or enter custom
                      </span>
                    </div>
                  </div>

                  <Input
                    placeholder="Enter company name..."
                    value={customCompany}
                    onChange={(e) => {
                      setCustomCompany(e.target.value);
                      setCompany("");
                    }}
                    className="text-lg py-6"
                  />

                  {(company || customCompany) && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800"
                    >
                      <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="font-medium">
                          Selected: {company || customCompany}
                        </span>
                      </div>
                    </motion.div>
                  )}
                </CardContent>
              </div>
            )}

            {/* Step 2: Prompt Selection */}
            {currentStep === 2 && (
              <div>
                <CardHeader>
                  <CardTitle>Choose Research Type</CardTitle>
                  <CardDescription>
                    Select the type of intelligence you want to gather
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2">
                    {categories.map((category) => (
                      <div key={category.id} className="border rounded-lg overflow-hidden">
                        <button
                          onClick={() =>
                            setExpandedCategory(
                              expandedCategory === category.id ? null : category.id
                            )
                          }
                          className="w-full p-4 flex items-center justify-between bg-muted/50 hover:bg-muted transition-colors"
                        >
                          <span className="font-medium">{category.name}</span>
                          <svg
                            className={cn(
                              "w-5 h-5 transition-transform",
                              expandedCategory === category.id && "rotate-180"
                            )}
                            fill="none"
                            viewBox="0 0 24 24"
                            stroke="currentColor"
                          >
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                        <AnimatePresence>
                          {expandedCategory === category.id && (
                            <motion.div
                              initial={{ height: 0, opacity: 0 }}
                              animate={{ height: "auto", opacity: 1 }}
                              exit={{ height: 0, opacity: 0 }}
                              transition={{ duration: 0.2 }}
                            >
                              <div className="p-2 space-y-2">
                                {category.prompts.map((prompt) => (
                                  <motion.button
                                    key={prompt.id}
                                    whileHover={{ x: 4 }}
                                    onClick={() => setSelectedPrompt(prompt)}
                                    className={cn(
                                      "w-full p-3 rounded-lg text-left transition-all",
                                      selectedPrompt?.id === prompt.id
                                        ? "bg-primary text-primary-foreground"
                                        : "hover:bg-muted"
                                    )}
                                  >
                                    <div className="font-medium text-sm">{prompt.name}</div>
                                    {prompt.description && (
                                      <div
                                        className={cn(
                                          "text-xs mt-1",
                                          selectedPrompt?.id === prompt.id
                                            ? "text-primary-foreground/80"
                                            : "text-muted-foreground"
                                        )}
                                      >
                                        {prompt.description}
                                      </div>
                                    )}
                                  </motion.button>
                                ))}
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    ))}
                  </div>

                  {selectedPrompt && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="mt-4 p-4 bg-green-50 dark:bg-green-950 rounded-lg border border-green-200 dark:border-green-800"
                    >
                      <div className="flex items-center gap-2 text-green-700 dark:text-green-300">
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span className="font-medium">Selected: {selectedPrompt.name}</span>
                      </div>
                    </motion.div>
                  )}
                </CardContent>
              </div>
            )}

            {/* Step 3: Provider & Mode Selection */}
            {currentStep === 3 && (
              <div>
                <CardHeader>
                  <CardTitle>Configure Providers & Mode</CardTitle>
                  <CardDescription>
                    Select AI providers and research depth
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-8">
                  {/* Provider Selection */}
                  <div>
                    <h3 className="font-medium mb-4">AI Providers</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {PROVIDERS.map((provider) => (
                        <motion.button
                          key={provider.id}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.98 }}
                          onClick={() => toggleProvider(provider.id)}
                          className={cn(
                            "p-4 rounded-lg border-2 text-left transition-all",
                            selectedProviders.includes(provider.id)
                              ? "border-primary bg-primary/5"
                              : "border-border hover:border-primary/50"
                          )}
                        >
                          <div className="flex items-center gap-3">
                            <div
                              className={cn(
                                "w-10 h-10 rounded-lg flex items-center justify-center font-bold",
                                provider.color
                              )}
                            >
                              {provider.icon}
                            </div>
                            <div className="flex-1">
                              <div className="font-medium">{provider.name}</div>
                              <div className="text-xs text-muted-foreground">
                                {provider.description}
                              </div>
                            </div>
                            <div
                              className={cn(
                                "w-6 h-6 rounded-full border-2 flex items-center justify-center transition-colors",
                                selectedProviders.includes(provider.id)
                                  ? "border-primary bg-primary"
                                  : "border-muted-foreground"
                              )}
                            >
                              {selectedProviders.includes(provider.id) && (
                                <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                                </svg>
                              )}
                            </div>
                          </div>
                        </motion.button>
                      ))}
                    </div>
                  </div>

                  {/* Mode Selection */}
                  <div>
                    <h3 className="font-medium mb-4">Research Mode</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setMode("basic")}
                        className={cn(
                          "p-4 rounded-lg border-2 text-left transition-all",
                          mode === "basic"
                            ? "border-primary bg-primary/5"
                            : "border-border hover:border-primary/50"
                        )}
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                            <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                            </svg>
                          </div>
                          <div>
                            <div className="font-medium">Basic</div>
                            <div className="text-xs text-muted-foreground">
                              Fast, focused research
                            </div>
                          </div>
                        </div>
                      </motion.button>

                      <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        onClick={() => setMode("deep")}
                        className={cn(
                          "p-4 rounded-lg border-2 text-left transition-all",
                          mode === "deep"
                            ? "border-primary bg-primary/5"
                            : "border-border hover:border-primary/50"
                        )}
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                            <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
                            </svg>
                          </div>
                          <div>
                            <div className="font-medium">Deep Research</div>
                            <div className="text-xs text-muted-foreground">
                              Comprehensive analysis
                            </div>
                          </div>
                        </div>
                      </motion.button>
                    </div>
                  </div>
                </CardContent>
              </div>
            )}

            {/* Step 4: Review */}
            {currentStep === 4 && (
              <div>
                <CardHeader>
                  <CardTitle>Review & Launch</CardTitle>
                  <CardDescription>
                    Confirm your research configuration
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-muted">
                      <div className="text-sm text-muted-foreground">Target Company</div>
                      <div className="font-semibold text-lg">{company || customCompany}</div>
                    </div>

                    <div className="p-4 rounded-lg bg-muted">
                      <div className="text-sm text-muted-foreground">Research Type</div>
                      <div className="font-semibold text-lg">{selectedPrompt?.name}</div>
                      {selectedPrompt?.description && (
                        <div className="text-sm text-muted-foreground mt-1">
                          {selectedPrompt.description}
                        </div>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg bg-muted">
                        <div className="text-sm text-muted-foreground">AI Providers</div>
                        <div className="font-semibold">
                          {selectedProviders
                            .map((p) => PROVIDERS.find((pr) => pr.id === p)?.name)
                            .join(", ")}
                        </div>
                      </div>

                      <div className="p-4 rounded-lg bg-muted">
                        <div className="text-sm text-muted-foreground">Research Mode</div>
                        <div className="font-semibold capitalize">{mode}</div>
                      </div>
                    </div>
                  </div>

                  {error && (
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="p-4 text-red-600 bg-red-50 dark:bg-red-950 dark:text-red-400 rounded-lg"
                    >
                      {error}
                    </motion.div>
                  )}

                  <motion.div
                    whileHover={{ scale: 1.01 }}
                    whileTap={{ scale: 0.99 }}
                  >
                    <Button
                      onClick={handleSubmit}
                      disabled={loading}
                      className="w-full h-14 text-lg"
                    >
                      {loading ? (
                        <div className="flex items-center gap-2">
                          <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                          Launching Research...
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                          </svg>
                          Launch Research
                        </div>
                      )}
                    </Button>
                  </motion.div>
                </CardContent>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={prevStep}
          disabled={currentStep === 1}
          className={cn(currentStep === 1 && "invisible")}
        >
          <svg className="w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
          </svg>
          Back
        </Button>

        {currentStep < 4 && (
          <Button onClick={nextStep} disabled={!canProceed()}>
            Next
            <svg className="w-4 h-4 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </Button>
        )}
      </div>
    </div>
  );
}
