import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <Skeleton className="h-10 w-48 mx-auto mb-2" />
        <Skeleton className="h-5 w-96 mx-auto" />
      </div>

      {/* Progress Steps */}
      <div className="flex justify-between items-center px-8">
        {[1, 2, 3, 4].map((step, index) => (
          <div key={step} className="flex items-center">
            <div className="flex flex-col items-center">
              <Skeleton className="w-10 h-10 rounded-full" />
              <Skeleton className="h-3 w-16 mt-2" />
            </div>
            {index < 3 && <Skeleton className="h-0.5 w-16 mx-2" />}
          </div>
        ))}
      </div>

      {/* Step Content Card */}
      <div className="border rounded-lg min-h-[400px] p-6">
        <Skeleton className="h-8 w-64 mb-2" />
        <Skeleton className="h-5 w-80 mb-6" />

        {/* Company Cards Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <Skeleton key={i} className="h-20 w-full rounded-lg" />
          ))}
        </div>

        {/* Divider */}
        <div className="flex items-center my-6">
          <Skeleton className="h-px flex-1" />
          <Skeleton className="h-4 w-24 mx-4" />
          <Skeleton className="h-px flex-1" />
        </div>

        {/* Input */}
        <Skeleton className="h-14 w-full" />
      </div>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Skeleton className="h-10 w-24" />
        <Skeleton className="h-10 w-24" />
      </div>
    </div>
  );
}
