import axios from "axios";

// Sem timeout, um backend travado deixaria a tela carregando para sempre.
export const api = axios.create({
  baseURL: `${process.env.NEXT_PUBLIC_API_URL}/api/v1`,
  timeout: 10_000,
});

// A API recusa parâmetro vazio (ex.: position=) com 400, então ele nunca é enviado.
api.interceptors.request.use((config) => {
  if (config.params) {
    config.params = Object.fromEntries(
      Object.entries(config.params).filter(
        ([, value]) => value !== undefined && value !== null && value !== "",
      ),
    );
  }

  return config;
});
