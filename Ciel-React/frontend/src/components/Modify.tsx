import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import type Config from "@/lib/types";
import { PlusIcon, XIcon } from "lucide-react";
import type React from "react";
import { useEffect, useState } from "react";

interface DialogModifyProps {
  config: Config | undefined;
  setRefreshConfig: React.Dispatch<React.SetStateAction<number>>;
}

export function DialogModify({ config, setRefreshConfig }: DialogModifyProps) {
  const [localConfig, setLocalConfig] = useState(config);

  async function save() {
    // setRefreshConfig((prev) => prev + 1);
    // await window.pywebview.api.save_config(localConfig);
    console.log(localConfig);
  }

  function deleteCode(code: string) {
    if (!localConfig) return;
    const clean_config = Object.entries(localConfig).map(([key, values]) => {
      if (Array.isArray(values)) {
        const clean_array = values.filter((value) => value != code);
        return [key, clean_array];
      } else {
        return [key, values];
      }
    });
    setLocalConfig(Object.fromEntries(clean_config));
  }

  function addCode(configKey: string, code: string) {
    if (!localConfig) return;
    const clean_config = Object.entries(localConfig).map(([key, values]) => {
      if (key == configKey && Array.isArray(values)) {
        const new_values = [...values, code];
        return [key, new_values];
      } else {
        return [key, values];
      }
    });
    setLocalConfig(Object.fromEntries(clean_config));
  }
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="outline" className="cursor-pointer">
          Modifier
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle className="font-semibold">
            Modifier les codes journaux
          </DialogTitle>
          <DialogDescription>
            Modifiez les codes journaux utilisés pour les factures, paiements et
            reports à nouveau.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col gap-4">
          {[
            {
              label: "Factures",
              codes: localConfig?.journal_factures,
              configKey: "journal_factures",
            },
            {
              label: "Paiements",
              codes: localConfig?.journal_paiements,
              configKey: "journal_paiements",
            },
            {
              label: "Report à nouveau",
              codes: localConfig?.journal_report,
              configKey: "journal_report",
            },
          ].map((section) => (
            <div key={section.label} className="flex flex-col gap-1.5">
              <span className="text-sm font-medium">{section.label}</span>
              <div className="flex flex-wrap items-center gap-2">
                {section.codes?.map((code) => (
                  <Button
                    variant="secondary"
                    key={code}
                    className="flex items-center gap-1 rounded border px-2 py-0.5 text-sm hover:bg-destructive"
                    onClick={() => deleteCode(code)}
                  >
                    {code}
                    <XIcon className="h-3 w-3 cursor-pointer text-muted-foreground" />
                  </Button>
                ))}
                <Button
                  variant="ghost"
                  className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground border border-foreground border-dashed"
                >
                  <PlusIcon className="h-3.5 w-3.5" />
                  Ajouter
                </Button>
              </div>
            </div>
          ))}
        </div>

        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Annuler</Button>
          </DialogClose>
          <Button onClick={() => save()}>Sauvegarder</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
