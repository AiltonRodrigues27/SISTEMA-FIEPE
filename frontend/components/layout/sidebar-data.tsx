import { Clock, Swords, Trophy } from "lucide-react";
import { NewClubIconButton } from "@/components/layout/new-club-icon-button";
import { SidebarNavItem } from "@/components/layout/sidebar-nav-item";
import { Separator } from "@/components/ui/separator";
import {
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarMenu,
} from "@/components/ui/sidebar";
import { getClubs } from "@/services/clubs.service";
import { getMatches } from "@/services/matches.service";
import { getPlayers } from "@/services/players.service";
import { pluralize } from "@/utils/format";
import { navigationGroups } from "@/utils/navigation";

export async function SidebarData() {
  const [players, clubs, matches] = await Promise.all([
    getPlayers({ limit: 1 }),
    getClubs(),
    getMatches(),
  ]);

  const playersTotal = players.ok ? players.data.meta.total_items : undefined;
  const clubsList = clubs.ok ? clubs.data : [];
  const matchesList = matches.ok ? matches.data : [];
  const lastMatch = matchesList[0];

  const counts: Record<string, number | undefined> = {
    "/players": playersTotal,
    "/clubs": clubs.ok ? clubsList.length : undefined,
    "/matches": matches.ok ? matchesList.length : undefined,
  };

  return (
    <>
      <SidebarContent>
        {navigationGroups.map((group) => (
          <SidebarGroup key={group.label}>
            <SidebarGroupLabel>{group.label}</SidebarGroupLabel>
            <SidebarMenu>
              {group.items.map(({ label, href, icon: Icon }) => (
                <SidebarNavItem
                  key={href}
                  href={href}
                  label={label}
                  icon={<Icon />}
                  count={counts[href]}
                />
              ))}
            </SidebarMenu>
          </SidebarGroup>
        ))}
        <SidebarGroup>
          <div className="flex items-center justify-between">
            <SidebarGroupLabel>Clubes</SidebarGroupLabel>
            <NewClubIconButton />
          </div>
          {clubsList.length === 0 ? (
            <p className="px-2 text-caption text-muted-foreground">
              Nenhum clube ainda.
            </p>
          ) : (
            <SidebarMenu>
              {clubsList.map((club) => (
                <SidebarNavItem
                  key={club.id}
                  href={`/clubs/${club.id}`}
                  label={club.name}
                  icon={
                    <span
                      aria-hidden
                      className="flex size-5 items-center justify-center rounded-sm border bg-background text-caption font-medium group-data-active/menu-button:border-primary group-data-active/menu-button:bg-primary group-data-active/menu-button:text-primary-foreground"
                    >
                      {club.name.charAt(0)}
                    </span>
                  }
                />
              ))}
            </SidebarMenu>
          )}
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <div className="flex flex-col gap-2.5 rounded-xl border border-sidebar-border bg-background p-3 shadow-xs">
          <div className="flex items-center gap-2.5">
            <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
              <Trophy className="size-4" aria-hidden />
            </span>
            <div className="flex min-w-0 flex-col">
              <span className="text-body-sm font-medium">
                Liga Fictícia 2026
              </span>
              {playersTotal !== undefined && clubs.ok && (
                <span className="text-caption text-muted-foreground">
                  {clubsList.length}{" "}
                  {pluralize(clubsList.length, "clube", "clubes")} ·{" "}
                  {playersTotal}{" "}
                  {pluralize(playersTotal, "jogador", "jogadores")}
                </span>
              )}
            </div>
          </div>
          {matches.ok && (
            <div className="flex items-center gap-2.5">
              <span className="flex size-8 shrink-0 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                <Swords className="size-4" aria-hidden />
              </span>
              <div className="flex min-w-0 flex-col">
                <span className="text-body-sm font-medium">Última partida</span>
                <span className="text-caption text-muted-foreground">
                  {lastMatch
                    ? `${lastMatch.home.club_name} ${lastMatch.home.goals} × ${lastMatch.away.goals} ${lastMatch.away.club_name}`
                    : "nenhuma ainda"}
                </span>
              </div>
            </div>
          )}
          <Separator />
          <p className="flex items-center gap-1.5 text-caption text-muted-foreground">
            <Clock className="size-3.5" aria-hidden />
            Horário de Brasília (UTC−3)
          </p>
        </div>
      </SidebarFooter>
    </>
  );
}
