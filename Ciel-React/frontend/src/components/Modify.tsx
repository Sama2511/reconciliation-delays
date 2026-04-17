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
import { Check, PlusIcon, X, XIcon } from "lucide-react";
import type React from "react";
import { useState } from "react";
import { Input } from "./ui/input";
import { toast } from "sonner";

interface DialogModifyProps {
  config: Config | undefined;
  setRefreshConfig: React.Dispatch<React.SetStateAction<number>>;
}

export function DialogModify({ config, setRefreshConfig }: DialogModifyProps) {
  const [localConfig, setLocalConfig] = useState(config);
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState("");
  const [open, setOpen] = useState(false);
  function handleOpenChange(isOpen: boolean) {
    if (!isOpen) {
      setInputValue("");
      setActiveSection(null);
      setLocalConfig(config);
    }
    setOpen(isOpen);
  }
  async function save() {
    if (inputValue) {
      toast.error("Veuillez valider ou annuler le code en cours d'ajout", {
        position: "top-center",
      });
      return;
    }
    await window.pywebview.api.save_config(localConfig);
    setRefreshConfig((prev) => prev + 1);
    setOpen(false);
    console.log("reach set open");
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
    if (code.length <= 0) return;
    const clean_config = Object.entries(localConfig).map(([key, values]) => {
      if (key == configKey && Array.isArray(values)) {
        if (values.includes(code.toUpperCase())) return [key, values];
        const new_values = [...values, code.toUpperCase()];
        return [key, new_values];
      } else {
        return [key, values];
      }
    });
    setLocalConfig(Object.fromEntries(clean_config));
    setInputValue("");
    setActiveSection(null);
  }
  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button
          variant="outline"
          className="cursor-pointer  bg-gray-100 shadow-lg"
        >
          Modifier
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-sm">
        <DialogHeader>
          <DialogTitle className="font-semibold text-[16px]">
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
                    className="flex items-center gap-1 rounded border px-2 py-0.5 text-sm hover:bg-destructive bg-accent cursor-pointer"
                    onClick={() => deleteCode(code)}
                  >
                    {code}
                    <XIcon className="h-3 w-3 cursor-pointer text-muted-foreground" />
                  </Button>
                ))}
                {activeSection == section.configKey ? (
                  <div className="flex items-center gap-1">
                    <Input
                      autoFocus
                      placeholder="Code"
                      className="h-7 w-16 px-2 text-sm uppercase border border-border bg-muted"
                      value={inputValue}
                      onChange={(event) => setInputValue(event?.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") {
                          addCode(section.configKey, inputValue);
                        }
                      }}
                    />
                    {inputValue && (
                      <>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7 text-green-600 hover:text-green-700 hover:bg-green-50 cursor-pointer"
                          onClick={() => addCode(section.configKey, inputValue)}
                        >
                          <Check className="h-3.5 w-3.5" />
                        </Button>
                        <Button
                          size="icon"
                          variant="ghost"
                          className="h-7 w-7 text-muted-foreground hover:text-destructive hover:bg-destructive/10 cursor-pointer"
                          onClick={() => {
                            setInputValue("");
                            setActiveSection(null);
                          }}
                        >
                          <X className="h-3.5 w-3.5" />
                        </Button>
                      </>
                    )}
                  </div>
                ) : (
                  <Button
                    variant="ghost"
                    className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground border border-foreground border-dashed cursor-pointer"
                    onClick={() => {
                      setInputValue("");
                      setActiveSection(section.configKey);
                    }}
                  >
                    <PlusIcon className="h-3.5 w-3.5" />
                    Ajouter
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>

        <DialogFooter>
          <DialogClose asChild>
            <Button
              variant="outline"
              className="cursor-pointer  bg-gray-100 shadow-lg"
              onClick={() => {
                setInputValue("");
                setActiveSection(null);
                setLocalConfig(config);
              }}
            >
              Annuler
            </Button>
          </DialogClose>
          <Button
            onClick={() => {
              save();
            }}
          >
            Sauvegarder
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
