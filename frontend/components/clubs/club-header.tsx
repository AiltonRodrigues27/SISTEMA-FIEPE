import { Shirt } from "lucide-react";
import type { ReactNode } from "react";
import { ClubTile } from "@/components/shared/club-tile";
import { Badge } from "@/components/ui/badge";
import type { ClubDetail } from "@/types/clubs.types";

type ClubHeaderProps = {
  club: ClubDetail;
  squadLimit: number;
  actions: ReactNode;
};

export function ClubHeader({ club, squadLimit, actions }: ClubHeaderProps) {
  return (
    <header className="flex flex-col gap-4 sm:flex-row sm:items-center">
      <div className="flex min-w-0 flex-1 items-center gap-4">
        <ClubTile
          acronym={club.acronym}
          className="size-12 rounded-xl text-body-sm"
        />
        <div className="flex min-w-0 flex-col gap-1.5">
          <h1 className="text-heading-page-mobile md:text-heading-page">
            {club.name}
          </h1>
          <div className="flex flex-wrap items-center gap-2">
            <Badge variant="outline">Sigla {club.acronym}</Badge>
            <Badge variant="outline">
              <Shirt aria-hidden />
              {club.players.length} de {squadLimit} jogadores
            </Badge>
          </div>
        </div>
      </div>
      {actions}
    </header>
  );
}
