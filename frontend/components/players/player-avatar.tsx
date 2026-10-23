import { getInitials } from "@/utils/format";

const TONES = [
  "bg-avatar-violet text-avatar-violet-foreground",
  "bg-avatar-pink text-avatar-pink-foreground",
  "bg-avatar-cyan text-avatar-cyan-foreground",
  "bg-avatar-teal text-avatar-teal-foreground",
  "bg-avatar-zinc text-avatar-zinc-foreground",
];

type PlayerAvatarProps = {
  id: number;
  name: string;
};

export function PlayerAvatar({ id, name }: PlayerAvatarProps) {
  return (
    <span
      aria-hidden
      className={`flex size-8 shrink-0 items-center justify-center rounded-full text-caption font-medium ${TONES[id % TONES.length]}`}
    >
      {getInitials(name)}
    </span>
  );
}
