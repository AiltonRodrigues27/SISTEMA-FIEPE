"use client";

import { ArrowRight } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { Button } from "@/components/ui/button";

const START_HREF = "/players";

export function StartAction() {
  const router = useRouter();

  useEffect(() => {
    function startOnEnter(event: KeyboardEvent) {
      // Com foco num link ou botão, o Enter já faz a ação dele.
      const isOnControl =
        event.target instanceof HTMLElement &&
        event.target.closest("a, button") !== null;

      if (event.key === "Enter" && !isOnControl) router.push(START_HREF);
    }

    window.addEventListener("keydown", startOnEnter);
    return () => window.removeEventListener("keydown", startOnEnter);
  }, [router]);

  return (
    <div className="flex w-full flex-col items-center gap-3.5 sm:w-auto sm:flex-row">
      <Button
        size="lg"
        nativeButton={false}
        render={<Link href={START_HREF} />}
        className="w-full gap-2 sm:w-[200px]"
      >
        Iniciar
        <ArrowRight />
      </Button>
      <p className="hidden items-center gap-1.5 text-body-sm text-muted-foreground sm:flex">
        ou tecle
        <kbd className="flex h-5 items-center rounded-[4px] border bg-muted px-[5px] text-caption font-medium">
          Enter
        </kbd>
      </p>
    </div>
  );
}
