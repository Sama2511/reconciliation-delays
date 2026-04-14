import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type Config from "@/lib/types";
import { CheckIcon, PlusIcon, XIcon } from "lucide-react";
import { useState } from "react";

interface ExcludeSupplierProps {
  config: Config | undefined;
  setRefreshConfig: React.Dispatch<React.SetStateAction<number>>;
}

export function SupplierExcluded({
  config,
  setRefreshConfig,
}: ExcludeSupplierProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [numImput, setNumInput] = useState("");
  const [nameInput, setNameInput] = useState("");
  const [isNumError, setIsNumError] = useState(false);
  async function addSupllier(supplierNumber: string, supplierName: string) {
    if (!config) return;
    if (!numImput) return;
    const clean_config = Object.entries(config).map(([key, values]) => {
      if (key === "fournisseurs_exclus") {
        const added_supplier = [
          ...values,
          { num: supplierNumber, name: supplierName },
        ];
        return [key, added_supplier];
      } else {
        return [key, values];
      }
    });
    await window.pywebview.api.save_config(Object.fromEntries(clean_config));
    setRefreshConfig((prev) => prev + 1);
    setNumInput("");
    setNameInput("");
    setIsAdding(false);
  }

  async function deleteSupplier(supplierNumber: string) {
    if (!config) return;
    const updated_config = {
      ...config,
      fournisseurs_exclus: config.fournisseurs_exclus.filter(
        (s) => s.num !== supplierNumber,
      ),
    };
    await window.pywebview.api.save_config(updated_config);
    setRefreshConfig((prev) => prev + 1);
  }

  return (
    <Card className="pt-2 gap-0 max-w-110 pb-2">
      <CardHeader className="border-b font-bold text-lg py-2! px-4! ">
        <div className="flex justify-between items-center">
          Fournisseurs exclus
          <Button
            variant="outline"
            className="cursor-pointer"
            onClick={() => setIsAdding(true)}
          >
            <PlusIcon className="h-3.5 w-3.5" />
            Ajouter
          </Button>
        </div>
      </CardHeader>
      <div className="grid grid-cols-[1fr_2fr_auto] text-xs font-semibold text-muted-foreground tracking-widest px-4 py-2.5 bg-muted border-b ">
        <span>N° COMPTE</span>
        <span>FOURNISSEUR</span>
        <span />
      </div>
      <CardContent className="p-0! overflow-y-auto max-h-30">
        {config?.fournisseurs_exclus.length === 0 && !isAdding && (
          <p className="px-4 py-4 text-sm text-muted-foreground flex justify-center">
            Aucun fournisseur exclu
          </p>
        )}
        {config?.fournisseurs_exclus.map((supplier, i) => (
          <div
            key={supplier.num}
            className={`grid grid-cols-[1fr_2fr_auto]  items-center px-4 py-3 ${i < config.fournisseurs_exclus.length - 1 ? "border-b" : ""}`}
          >
            <span className="text-sm text-muted-foreground">
              {supplier.num}
            </span>
            <span className="text-sm font-semibold">{supplier.name}</span>
            <button
              className="text-muted-foreground hover:text-destructive cursor-pointer"
              onClick={() => deleteSupplier(supplier.num)}
            >
              <XIcon className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
        {isAdding && (
          <div className="grid grid-cols-[1fr_2fr_auto] items-center px-4 py-2 border-t gap-2">
            <input
              autoFocus
              placeholder="N° compte"
              className={`h-7 px-2 text-sm border border-border bg-muted w-full ${isNumError ? "border-red-500" : "border-border"}`}
              maxLength={12}
              value={numImput}
              onChange={(event) => {
                setNumInput(event.target.value);
                setIsNumError(false);
              }}
            />
            <input
              placeholder="Nom fournisseur"
              className="h-7 px-2 text-sm border border-border bg-muted w-full"
              value={nameInput}
              maxLength={25}
              onChange={(event) => setNameInput(event.target.value)}
            />
            <div className="flex items-center gap-1">
              <button
                className="h-7 w-7 flex items-center justify-center text-green-600 hover:text-green-700 hover:bg-green-50 cursor-pointer"
                onClick={() => {
                  if (!numImput) {
                    setIsNumError(true);
                    return;
                  }
                  addSupllier(numImput, nameInput);
                }}
              >
                <CheckIcon className="h-3.5 w-3.5" />
              </button>
              <button
                className="h-7 w-7 flex items-center justify-center text-muted-foreground hover:text-destructive hover:bg-destructive/10 cursor-pointer"
                onClick={() => {
                  setIsAdding(false);
                  setNameInput("");
                  setNumInput("");
                }}
              >
                <XIcon className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
