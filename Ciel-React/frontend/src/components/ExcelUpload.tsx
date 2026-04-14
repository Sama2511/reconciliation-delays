import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { useState, type ChangeEvent } from "react";
import { Button } from "./ui/button";
import { X } from "lucide-react";

export function ExcelUpload() {
  const [currentYearFile, setCurrentYearFile] = useState<File | null>(null);
  const [pastYearFile, setPastYearFile] = useState<File | null>(null);

  function handleUploadCurrentYear(e: ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files.length > 0) {
      setCurrentYearFile(e.target.files[0]);
    }
  }
  function handleUploadPastYear(e: ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files.length > 0) {
      setPastYearFile(e.target.files[0]);
    }
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
                  {currentYearFile.name}
                </span>
                <span className="text-[12px] text-green-600">
                  {(currentYearFile.size / 1024).toFixed(0)} KB · Excel
                </span>
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
            <div className="flex items-center justify-center border border-dashed h-27 text-muted-foreground text-sm flex-col gap-1">
              <label
                htmlFor="filePicker"
                className="w-full bg-secondary flex flex-col justify-center items-center h-full cursor-pointer "
              >
                <span className="text-3xl">📂</span>
                <h1 className="font-semibold text-[16px]">
                  Clicker pour importer
                </h1>
                <p>Grand livre N (.xlsx)</p>
              </label>
              <input
                id="filePicker"
                className="hidden"
                type={"file"}
                onChange={handleUploadCurrentYear}
              />
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
                  {pastYearFile.name}
                </span>
                <span className="text-[12px] text-green-600">
                  {(pastYearFile.size / 1024).toFixed(0)} KB · Excel
                </span>
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
            <div className="flex items-center justify-center border border-dashed h-27 text-muted-foreground text-sm flex-col gap-1">
              <label
                htmlFor="filePicker2"
                className="w-full bg-secondary flex flex-col justify-center items-center h-full cursor-pointer "
              >
                <span className="text-3xl">📂</span>
                <h1 className="font-semibold text-[16px]">
                  Clicker pour importer
                </h1>
                <p>Grand livre N-1 (.xlsx)</p>
              </label>
              <input
                id="filePicker2"
                className="hidden"
                type={"file"}
                onChange={handleUploadPastYear}
              />
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
