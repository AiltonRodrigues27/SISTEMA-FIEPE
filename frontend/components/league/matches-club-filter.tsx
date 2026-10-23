"use client";

import { Shield } from "lucide-react";
import { useRouter } from "next/navigation";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const ALL_CLUBS = "all";

type MatchesClubFilterProps = {
  clubId?: number;
  clubs: { id: number; name: string }[];
};

export function MatchesClubFilter({ clubId, clubs }: MatchesClubFilterProps) {
  const router = useRouter();
  const items = [
    { value: ALL_CLUBS, label: "todos" },
    ...clubs.map((club) => ({ value: String(club.id), label: club.name })),
  ];

  return (
    <Select
      items={items}
      value={clubId ? String(clubId) : ALL_CLUBS}
      onValueChange={(value) =>
        router.replace(
          value === ALL_CLUBS ? "/matches" : `/matches?club_id=${value}`,
        )
      }
    >
      <SelectTrigger
        aria-label="Filtrar partidas por clube"
        className="h-9 w-56"
      >
        <Shield className="text-muted-foreground" aria-hidden />
        <span>Clube:</span>
        <SelectValue />
      </SelectTrigger>
      <SelectContent>
        {items.map((item) => (
          <SelectItem key={item.value} value={item.value}>
            {item.label}
          </SelectItem>
        ))}
      </SelectContent>
    </Select>
  );
}
