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
        save_config: (config) => Promise<Config>;
        generate_report: (
          currentYearFile: string,
          pastYearFile: string,
          excludedSuppliers: string[],
          start: string,
          endDate: string,
        ) => Promise<boolean>;
        pick_current_year_file: () => Promise<string | null>;
        pick_past_year_file: () => Promise<string | null>;
      };
    };
  }
}
