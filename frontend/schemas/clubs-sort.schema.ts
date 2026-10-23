import { z } from "zod";
import type { ClubSort } from "@/types/clubs.types";

const clubSortSchema = z
  .enum(["name", "net_worth_asc", "net_worth_desc"])
  .catch("name");

export function parseClubSort(raw: string | string[] | undefined): ClubSort {
  return clubSortSchema.parse(Array.isArray(raw) ? raw[0] : raw);
}
