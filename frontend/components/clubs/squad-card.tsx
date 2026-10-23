import { SquadTable } from "@/components/clubs/squad-table";
import type { SquadMember } from "@/types/clubs.types";
import { formatNow } from "@/utils/format";

type SquadCardProps = {
  squad: SquadMember[];
  clubName: string;
  starterIds: number[];
};

export function SquadCard({ squad, clubName, starterIds }: SquadCardProps) {
  return (
    <>
      <div className="flex flex-col gap-1 p-4">
        <h2 className="text-heading-card">Elenco</h2>
        <p className="text-caption text-muted-foreground">
          Ordem por posição (GOL, ZAG, LAT, MEI, ATA), depois pelo nome.
          Contrato calculado para uma venda agora.
        </p>
      </div>
      <SquadTable squad={squad} clubName={clubName} starterIds={starterIds} />
      <p className="border-t px-4 py-3 text-caption text-muted-foreground">
        Valor de mercado, dias restantes e % de multa calculados para uma venda
        agora ({formatNow()}). A multa tem teto de 10,00.
      </p>
    </>
  );
}
