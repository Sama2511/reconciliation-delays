import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "./ui/button";
import { X } from "lucide-react";

interface excelUploadProps {
  currentYearFile: string | null;
  pastYearFile: string | null;
  setCurrentYearFile: (file: string | null) => void;
  setPastYearFile: (file: string | null) => void;
  hasCurrentFileError: boolean;
  hasPastFileError: boolean;
}

export function ExcelUpload({
  currentYearFile,
  pastYearFile,
  setCurrentYearFile,
  setPastYearFile,
  hasCurrentFileError,
  hasPastFileError,
}: excelUploadProps) {
  async function handlePickCurrentYear() {
    const path = await window.pywebview.api.pick_current_year_file();
    if (path) setCurrentYearFile(path);
  }

  async function handlePickPastYear() {
    const path = await window.pywebview.api.pick_past_year_file();
    if (path) setPastYearFile(path);
  }

  return (
    <Card className="pt-2 gap-2 mt-4">
      <CardHeader className="border-b font-bold text-lg py-2! px-4!">
        Fichiers Grand Livre
      </CardHeader>
      <CardContent className="flex gap-8 pt-3 pb-4!">
        <div className="flex flex-col gap-1.5 flex-1">
          <span className="text-sm text-muted-foreground">Année en cours</span>
          {currentYearFile ? (
            <div className="flex items-center gap-3 border border-green-200 bg-green-50 px-4 h-27">
              <div className="flex flex-col flex-1 min-w-0">
                <span className="font-semibold text-green-800 text-[16px] truncate">
                  {currentYearFile.split("\\").pop()}
                </span>
                <span className="text-[12px] text-green-600">Excel</span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="shrink-0 text-muted-foreground hover:text-destructive hover:bg-destructive/10 cursor-pointer"
                onClick={() => setCurrentYearFile(null)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div
              className={`flex items-center justify-center border border-dashed h-27 text-muted-foreground text-sm flex-col gap-1 ${hasCurrentFileError ? "border-red-600" : ""}`}
              onClick={handlePickCurrentYear}
            >
              <div className="w-full bg-secondary flex flex-col justify-center items-center h-full cursor-pointer">
                <span className="text-3xl">📂</span>
                <h1 className="font-semibold text-[16px]">
                  Clicker pour importer
                </h1>
                <p>Grand livre N (.xlsx)</p>
              </div>
            </div>
          )}
        </div>
        <div className="flex flex-col gap-1.5 flex-1">
          <span className="text-sm text-muted-foreground">
            Année précédente
          </span>
          {pastYearFile ? (
            <div className="flex items-center gap-3 border border-green-200 bg-green-50 px-4 h-27">
              <div className="flex flex-col flex-1 min-w-0">
                <span className="font-semibold text-green-800 text-[16px] truncate">
                  {pastYearFile.split("\\").pop()}
                </span>
                <span className="text-[12px] text-green-600">Excel</span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="shrink-0 text-muted-foreground hover:text-destructive hover:bg-destructive/10 cursor-pointer"
                onClick={() => setPastYearFile(null)}
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          ) : (
            <div
              className={`flex items-center justify-center border border-dashed h-27 text-muted-foreground text-sm flex-col gap-1 ${hasPastFileError ? "border-red-600" : ""}`}
              onClick={handlePickPastYear}
            >
              <div className="w-full bg-secondary flex flex-col justify-center items-center h-full cursor-pointer">
                <span className="text-3xl">📂</span>
                <h1 className="font-semibold text-[16px]">
                  Clicker pour importer
                </h1>
                <p>Grand livre N-1 (.xlsx)</p>
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
