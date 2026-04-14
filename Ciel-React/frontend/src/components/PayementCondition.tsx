import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import type Config from "@/lib/types";
import { CheckIcon, PlusIcon, XIcon } from "lucide-react";
import { useState } from "react";

interface PayementConditionProps {
  config: Config | undefined;
  setRefreshConfig: React.Dispatch<React.SetStateAction<number>>;
}

export function PayementCondition({
  config,
  setRefreshConfig,
}: PayementConditionProps) {
  const [isAdding, setIsAdding] = useState(false);
  const [numInput, setNumInput] = useState("");
  const [nameInput, setNameInput] = useState("");
  const [daysInput, setDaysInput] = useState("");
  const [isNumError, setIsNumError] = useState(false);
  const [isDaysError, setIsDaysError] = useState(false);

  async function addCondition(
    supplierNumber: string,
    supplierName: string,
    days: number,
  ) {
    if (!config) return;
    const updated_config = {
      ...config,
      conditions_fournisseur: [
        ...config.conditions_fournisseur,
        { num: supplierNumber, name: supplierName, days },
      ],
    };
    await window.pywebview.api.save_config(updated_config);
    setRefreshConfig((prev) => prev + 1);
    setNumInput("");
    setNameInput("");
    setDaysInput("");
    setIsAdding(false);
  }

  async function deleteCondition(supplierNumber: string) {
    if (!config) return;
    const updated_config = {
      ...config,
      conditions_fournisseur: config.conditions_fournisseur.filter(
        (s) => s.num !== supplierNumber,
      ),
    };
    await window.pywebview.api.save_config(updated_config);
    setRefreshConfig((prev) => prev + 1);
  }

  function handleConfirm() {
    let hasError = false;
    if (!numInput) {
      setIsNumError(true);
      hasError = true;
    }
    const parsedDays = parseInt(daysInput, 10);
    if (!daysInput || isNaN(parsedDays) || parsedDays <= 0) {
      setIsDaysError(true);
      hasError = true;
    }
    if (hasError) return;
    addCondition(numInput, nameInput, parsedDays);
  }

  return (
    <Card className="pt-2 gap-0 w-130 pb-2">
      <CardHeader className="border-b font-bold text-lg py-2! px-4!">
        <div className="flex justify-between items-center">
          Conditions de paiement
          <div className="flex items-center gap-2">
            <span className="text-sm font-normal text-muted-foreground">
              Défaut
            </span>
            <span className="border rounded px-2 py-0.5 text-sm font-semibold">
              {config?.condition_default} jours
            </span>
            <Button
              variant="outline"
              className="cursor-pointer"
              onClick={() => setIsAdding(true)}
            >
              <PlusIcon className="h-3.5 w-3.5" />
              Ajouter
            </Button>
          </div>
        </div>
      </CardHeader>
      <div className="grid grid-cols-[1fr_2fr_1fr_auto] text-xs font-semibold text-muted-foreground tracking-widest px-4 py-2.5 bg-muted border-b">
        <span>N° COMPTE</span>
        <span>FOURNISSEUR</span>
        <span>CONDITION</span>
        <span />
      </div>
      <CardContent className="p-0! overflow-y-auto h-34">
        {config?.conditions_fournisseur.length === 0 && !isAdding && (
          <p className=" h-full px-4 py-4 text-sm text-muted-foreground flex justify-center items-center">
            Aucune condition spécifique
          </p>
        )}
        {config?.conditions_fournisseur.map((condition, i) => (
          <div
            key={condition.num}
            className={`grid grid-cols-[1fr_2fr_1fr_auto] items-center px-4 py-3 ${i < config.conditions_fournisseur.length - 1 ? "border-b border-muted" : ""}`}
          >
            <span className="text-sm text-muted-foreground">
              {condition.num}
            </span>
            <span className="text-sm font-semibold">{condition.name}</span>
            <span className="text-sm font-semibold">
              {condition.days} jours
            </span>
            <button
              className="text-muted-foreground hover:text-destructive cursor-pointer"
              onClick={() => deleteCondition(condition.num)}
            >
              <XIcon className="h-3.5 w-3.5" />
            </button>
          </div>
        ))}
        {isAdding && (
          <div className="grid grid-cols-[1fr_2fr_1fr_auto] items-center px-4 py-2 border-t gap-2">
            <input
              autoFocus
              placeholder="N° compte"
              className={`h-7 px-2 text-sm border bg-muted w-full ${isNumError ? "border-red-500" : "border-border"}`}
              maxLength={12}
              value={numInput}
              onChange={(e) => {
                setNumInput(e.target.value);
                setIsNumError(false);
              }}
            />
            <input
              placeholder="Nom fournisseur"
              className="h-7 px-2 text-sm border border-border bg-muted w-full"
              maxLength={25}
              value={nameInput}
              onChange={(e) => setNameInput(e.target.value)}
            />
            <input
              placeholder="Jours"
              className={`h-7 px-2 text-sm border bg-muted w-20 ${isDaysError ? "border-red-500" : "border-border"}`}
              maxLength={4}
              value={daysInput}
              onChange={(e) => {
                setDaysInput(e.target.value);
                setIsDaysError(false);
              }}
            />
            <div className="flex items-center gap-1">
              <button
                className="h-7 w-7 flex items-center justify-center text-green-600 hover:text-green-700 hover:bg-green-50 cursor-pointer"
                onClick={handleConfirm}
              >
                <CheckIcon className="h-3.5 w-3.5" />
              </button>
              <button
                className="h-7 w-7 flex items-center justify-center text-muted-foreground hover:text-destructive hover:bg-destructive/10 cursor-pointer"
                onClick={() => {
                  setIsAdding(false);
                  setNumInput("");
                  setNameInput("");
                  setDaysInput("");
                  setIsNumError(false);
                  setIsDaysError(false);
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
