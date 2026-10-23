import { ArrowLeft, SearchX } from "lucide-react";
import Link from "next/link";
import { EmptyState } from "@/components/shared/empty-state";
import { ListCard } from "@/components/shared/list-card";
import { Button } from "@/components/ui/button";

export function ClubNotFound() {
  return (
    <ListCard>
      <EmptyState
        icon={SearchX}
        title="Clube não encontrado"
        description="Clube não encontrado. O endereço pode estar errado ou o clube não existe."
        action={
          <Button
            variant="outline"
            size="sm"
            nativeButton={false}
            render={<Link href="/clubs" />}
          >
            <ArrowLeft aria-hidden />
            Voltar para clubes
          </Button>
        }
      />
    </ListCard>
  );
}
