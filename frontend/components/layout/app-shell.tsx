import { Suspense, type ReactNode } from "react";
import { AppSidebar } from "@/components/layout/app-sidebar";
import { AppTopbar } from "@/components/layout/app-topbar";
import { SidebarInset, SidebarProvider } from "@/components/ui/sidebar";
import { Toaster } from "@/components/ui/sonner";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <SidebarProvider>
      <AppSidebar />
      <SidebarInset className="md:peer-data-[variant=inset]:rounded-xl">
        <Suspense fallback={<div className="h-14 shrink-0 border-b" />}>
          <AppTopbar />
        </Suspense>
        <div className="flex flex-1 flex-col gap-6 px-4 pt-6 pb-10 md:px-8 md:pt-7">
          {children}
        </div>
      </SidebarInset>
      <Toaster />
    </SidebarProvider>
  );
}
