"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { SidebarMenuButton, SidebarMenuItem } from "@/components/ui/sidebar";

type SidebarNavItemProps = {
  href: string;
  label: string;
  icon: ReactNode;
  count?: number;
};

export function SidebarNavItem({
  href,
  label,
  icon,
  count,
}: SidebarNavItemProps) {
  const pathname = usePathname();
  const isActive = pathname === href || pathname.startsWith(`${href}/`);

  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        render={<Link href={href} />}
        isActive={isActive}
        className="h-8 rounded-md px-2 data-active:border data-active:border-sidebar-border data-active:bg-background data-active:shadow-xs"
      >
        {icon}
        <span className="flex-1">{label}</span>
        {count !== undefined && (
          <span className="text-caption font-normal text-muted-foreground">
            {count}
          </span>
        )}
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}
