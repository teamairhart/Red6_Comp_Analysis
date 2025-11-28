import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="mb-8">
        <Skeleton className="h-10 w-48 mb-2" />
        <Skeleton className="h-5 w-80" />
      </div>

      <div className="border rounded-lg p-6 space-y-6">
        {/* Company Input */}
        <div>
          <Skeleton className="h-5 w-24 mb-2" />
          <Skeleton className="h-10 w-full" />
        </div>

        {/* Prompt Selection */}
        <div>
          <Skeleton className="h-5 w-32 mb-2" />
          <Skeleton className="h-10 w-full" />
        </div>

        {/* Provider Selection */}
        <div>
          <Skeleton className="h-5 w-28 mb-2" />
          <div className="flex gap-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-6 w-24" />
            ))}
          </div>
        </div>

        {/* Mode Selection */}
        <div>
          <Skeleton className="h-5 w-20 mb-2" />
          <div className="flex gap-4">
            <Skeleton className="h-10 w-32" />
            <Skeleton className="h-10 w-32" />
          </div>
        </div>

        {/* Submit Button */}
        <Skeleton className="h-12 w-full" />
      </div>
    </div>
  );
}
