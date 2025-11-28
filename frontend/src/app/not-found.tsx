import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <div className="container mx-auto py-16 px-4">
      <div className="flex flex-col items-center justify-center text-center">
        <div className="mb-8">
          <h1 className="text-9xl font-bold text-muted-foreground/20">404</h1>
        </div>
        <h2 className="text-2xl font-bold mb-4">Page Not Found</h2>
        <p className="text-muted-foreground mb-8 max-w-md">
          The page you're looking for doesn't exist or has been moved.
          Check the URL or navigate back to the dashboard.
        </p>
        <div className="flex gap-4">
          <Link href="/">
            <Button>Go to Dashboard</Button>
          </Link>
          <Link href="/research">
            <Button variant="outline">New Research</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
