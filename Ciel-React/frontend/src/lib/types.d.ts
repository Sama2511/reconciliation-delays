export {};

export default interface Config {
  journal_factures: string[];
  journal_paiements: string[];
  journal_report: string[];
  condition_default: number;
  conditions_fournisseur: { num: string; name: string; days: number }[];
  fournisseurs_exclus: { num: string; name: string }[];
}

declare global {
  interface Window {
    pywebview: {
      api: {
        load_config: () => Promise<Config>;
        save_config: (config) => Promise<config>;
      };
    };
  }
}
