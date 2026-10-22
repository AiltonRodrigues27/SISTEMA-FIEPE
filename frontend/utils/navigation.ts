import {
  ListOrdered,
  Shield,
  Swords,
  Users,
  type LucideIcon,
} from "lucide-react";

export type NavigationItem = {
  label: string;
  href: string;
  icon: LucideIcon;
};

export type NavigationGroup = {
  label: string;
  items: NavigationItem[];
};

export const navigationGroups: NavigationGroup[] = [
  {
    label: "Mercado",
    items: [
      { label: "Jogadores", href: "/players", icon: Users },
      { label: "Clubes", href: "/clubs", icon: Shield },
    ],
  },
  {
    label: "Liga",
    items: [
      { label: "Partidas", href: "/matches", icon: Swords },
      { label: "Classificação", href: "/standings", icon: ListOrdered },
    ],
  },
];
