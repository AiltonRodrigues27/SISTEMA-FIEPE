import { NewMatchButton } from "@/components/league/new-match-button";
import { getClubs } from "@/services/clubs.service";

type NewMatchActionProps = {
  variant?: "default" | "outline";
};

export async function NewMatchAction({ variant }: NewMatchActionProps) {
  const clubs = await getClubs();

  return (
    <NewMatchButton clubs={clubs.ok ? clubs.data : []} variant={variant} />
  );
}
