"use client";

import { Search } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/input";

type PlayersSearchFieldProps = {
  urlValue: string;
  onSearch: (value: string) => void;
};

export function PlayersSearchField({
  urlValue,
  onSearch,
}: PlayersSearchFieldProps) {
  const [value, setValue] = useState(urlValue);
  const [syncedUrlValue, setSyncedUrlValue] = useState(urlValue);
  const onSearchRef = useRef(onSearch);

  // Se a URL mudou por outro caminho (ex.: remover o filtro), o campo acompanha.
  if (urlValue !== syncedUrlValue) {
    setSyncedUrlValue(urlValue);
    if (urlValue !== value.trim()) setValue(urlValue);
  }

  useEffect(() => {
    onSearchRef.current = onSearch;
  });

  useEffect(() => {
    const text = value.trim();
    // A API exige de 2 a 100 caracteres na busca.
    if (text === urlValue || text.length === 1) return;

    const timer = setTimeout(() => onSearchRef.current(text), 400);
    return () => clearTimeout(timer);
  }, [value, urlValue]);

  return (
    <div className="relative min-w-52 flex-1">
      <Search
        className="pointer-events-none absolute top-1/2 left-3 size-4 -translate-y-1/2 text-muted-foreground"
        aria-hidden
      />
      <Input
        type="search"
        value={value}
        onChange={(event) => setValue(event.target.value)}
        placeholder="Buscar por nome"
        aria-label="Buscar jogador pelo nome"
        maxLength={100}
        className="pl-9"
      />
    </div>
  );
}
