import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type Config from "@/lib/types";
import { CheckIcon, PlusIcon, Trash2, XIcon } from "lucide-react";
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
  const [numInput, setNumInput] = useState("");
  const [nameInput, setNameInput] = useState("");
  const [isNumError, setIsNumError] = useState(false);

  async function addSupplier(supplierNumber: string, supplierName: string) {
    if (!config) return;
    if (!numInput) {
      setIsNumError(true);
      return;
    }
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
    <Card className="pt-2 gap-0 w-110 min-w-110 pb-2 shadow-[0_0_15px_rgba(0,0,0,0.1)]">
      <CardHeader className="font-bold text-lg py-2! px-4! ">
        <div className="flex justify-between items-center font-medium ">
          Fournisseurs exclus
          <Button
            variant="outline"
            className="cursor-pointer  bg-gray-100 shadow-lg"
            onClick={() => setIsAdding(true)}
          >
            <PlusIcon className="h-3.5 w-3.5" />
            Ajouter
          </Button>
        </div>
      </CardHeader>
      <div className="grid grid-cols-[1fr_2fr_auto] text-xs font-semibold text-muted-foreground tracking-widest px-4 py-2.5 bg-muted  ">
        <span>N° COMPTE</span>
        <span>FOURNISSEUR</span>
        <span />
      </div>
      <CardContent className="p-0! overflow-y-auto h-30 max-h-30">
        {config?.fournisseurs_exclus.length === 0 && !isAdding && (
          <p className=" h-full px-4 py-4 text-sm text-muted-foreground flex justify-center items-center">
            Aucun fournisseur exclu
          </p>
        )}
        {config?.fournisseurs_exclus.map((supplier) => (
          <div
            key={supplier.num}
            className={`grid grid-cols-[1fr_2fr_auto] font-medium border-b border-secondary`}
          >
            <div className="flex items-center ml-1 px-4 py-2 border-r border-muted text-sm">
              {supplier.num}
            </div>
            <div className="flex items-center ml-2 px-4 py-2  text-sm">
              {supplier.name}
            </div>
            <div className="flex items-center px-4 py-2">
              <button
                className="text-muted-foreground hover:text-destructive cursor-pointer"
                onClick={() => deleteSupplier(supplier.num)}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        ))}
        {isAdding && (
          <div className="grid grid-cols-[1fr_2fr_auto] items-center px-4 py-2 border-t border-secondary gap-2">
            <input
              autoFocus
              placeholder="N° compte"
              className={`h-7 px-2 text-sm border border-border bg-muted w-full ${isNumError ? "border-red-500" : "border-border"}`}
              maxLength={12}
              value={numInput}
              onChange={(event) => {
                setNumInput(event.target.value);
                setIsNumError(false);
              }}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  addSupplier(numInput, nameInput);
                }
              }}
            />
            <input
              placeholder="Nom fournisseur (optionnel)"
              className="h-7 px-2 text-sm border border-border bg-muted w-full"
              value={nameInput}
              maxLength={25}
              onChange={(event) => setNameInput(event.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  addSupplier(numInput, nameInput);
                }
              }}
            />
            <div className="flex items-center gap-1">
              <button
                className="h-7 w-7 flex items-center justify-center text-green-600 hover:text-green-700 hover:bg-green-50 cursor-pointer"
                onClick={() => {
                  addSupplier(numInput, nameInput);
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
