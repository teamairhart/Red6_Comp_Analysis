import { Skeleton } from "@/components/ui/skeleton";

export default function Loading() {
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="mb-8">
        <Skeleton className="h-10 w-48 mb-2" />
        <Skeleton className="h-5 w-64" />
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <Skeleton className="h-10 w-full max-w-md" />
      </div>

      {/* Reports List */}
      <div className="space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="border rounded-lg p-4">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <Skeleton className="h-6 w-64 mb-2" />
                <Skeleton className="h-4 w-48 mb-1" />
                <Skeleton className="h-4 w-32" />
              </div>
              <div className="flex gap-2">
                <Skeleton className="h-9 w-20" />
                <Skeleton className="h-9 w-24" />
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
