import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function NotFound() {
  return (
    <main className="flex min-h-svh flex-col items-center justify-center gap-4 px-4 text-center">
      <h1 className="text-heading-page-mobile md:text-heading-page">
        Página não encontrada
      </h1>
      <p className="text-body text-muted-foreground">
        O endereço que você abriu não existe. Volte ao início para continuar.
      </p>
      <Button render={<Link href="/" />} nativeButton={false}>
        Voltar ao início
      </Button>
    </main>
  );
}
