import { useState, useEffect } from "react";
import { toast } from "sonner";
import { Card, CardContent, CardHeader } from "./components/ui/card";
import { DatePickerInput } from "./components/Date_picker";
import { DialogModify } from "./components/Modify";
import { ExcelUpload } from "./components/ExcelUpload";
import type Config from "./lib/types";
import { SupplierExcluded } from "./components/SupplierExcluded";
import { PayementCondition } from "./components/PayementCondition";
import { Button } from "./components/ui/button";
import { format } from "date-fns";

function App() {
  const [startDate, setStartDate] = useState<Date | undefined>(undefined);
  const [endDate, setEndDate] = useState<Date | undefined>(undefined);
  const [factures, setFactures] = useState<string[]>([]);
  const [paiements, setPaiements] = useState<string[]>([]);
  const [reports, setReports] = useState<string[]>([]);
  const [configuration, setConfiguration] = useState<Config | undefined>(
    undefined,
  );
  const [currentYearFile, setCurrentYearFile] = useState<string | null>(null);
  const [pastYearFile, setPastYearFile] = useState<string | null>(null);

  const [refreshConfig, setRefreshConfig] = useState(0);
  const [hasCurrentFileError, setHasCurrentFileError] = useState(false);
  const [hasPastFileError, setHasPastFileError] = useState(false);
  const [hasStartDateError, setHasStartDateError] = useState(false);
  const [hasEndDateError, setHasEndDateError] = useState(false);
  const [hasFacturesError, setHasFacturesError] = useState(false);
  const [hasPaiementsError, setHasPaiementsError] = useState(false);
  const [hasReportsError, setHasReportsError] = useState(false);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const config = await window.pywebview.api.load_config();
        setFactures(config.journal_factures);
        setPaiements(config.journal_paiements);
        setReports(config.journal_report);
        setConfiguration(config);
        if (config.journal_factures.length > 0) setHasFacturesError(false);
        if (config.journal_paiements.length > 0) setHasPaiementsError(false);
        if (config.journal_report.length > 0) setHasReportsError(false);
      } catch (err) {
        console.error("PyWebView call failed:", err);
      }
    };
    const handleReady = () => {
      fetchConfig();
    };
    if (window.pywebview) {
      fetchConfig();
    } else {
      window.addEventListener("pywebviewready", handleReady);
    }
    return () => {
      window.removeEventListener("pywebviewready", handleReady);
    };
  }, [refreshConfig]);
  function validate() {
    setHasCurrentFileError(!currentYearFile);
    setHasPastFileError(!pastYearFile);
    setHasStartDateError(!startDate);
    setHasEndDateError(!endDate);
    setHasFacturesError(factures.length === 0);
    setHasPaiementsError(paiements.length === 0);
    setHasReportsError(reports.length === 0);

    if (
      !currentYearFile ||
      !pastYearFile ||
      !startDate ||
      !endDate ||
      factures.length === 0 ||
      paiements.length === 0 ||
      reports.length === 0
    ) {
      return false;
    }
    return true;
  }
  async function generateReport() {
    if (!validate()) {
      toast.error(
        "Veuillez remplir tous les champs obligatoires avant de générer le rapport.",
        { position: "top-center" },
      );

      return;
    }
    await window.pywebview.api.generate_report(
      currentYearFile!,
      pastYearFile!,
      configuration?.fournisseurs_exclus.map((s) => s.num) ?? [],
      format(startDate!, "yyyy-MM-dd"),
      format(endDate!, "yyyy-MM-dd"),
    );
  }
  return (
    <div className="bg-background h-screen p-5 flex justify-center ">
      <div className="flex flex-col gap-5">
        <div className="flex gap-4.75 max-h-50">
          <Card className="min-w-112.5 pt-2 gap-5 h-54">
            <CardHeader className="border-b font-bold text-lg py-3! px-4!">
              Période de la declaration
            </CardHeader>
            <CardContent className="flex gap-8 pt-3  items-center mb-5">
              <DatePickerInput
                date={startDate}
                onDateChange={(date) => {
                  setStartDate(date);
                  setHasStartDateError(false);
                }}
                label="Date de début"
                hasError={hasStartDateError}
              />
              <DatePickerInput
                date={endDate}
                onDateChange={(date) => {
                  setEndDate(date);
                  setHasEndDateError(false);
                }}
                label="Date de fin"
                hasError={hasEndDateError}
              />
            </CardContent>
          </Card>
          <Card className="min-w-112.5 pt-2 gap-2 h-54">
            <CardHeader className="border-b font-bold text-lg py-2! px-4!">
              <div className="flex justify-between items-center">
                Codes journaux
                {configuration && (
                  <DialogModify
                    config={configuration}
                    setRefreshConfig={setRefreshConfig}
                  />
                )}
              </div>
            </CardHeader>
            <CardContent className="flex flex-col  gap-1 pt-0!">
              <div className="text-[15px] border-b  flex items-center justify-between py-2">
                <h3 className="text-muted-foreground">Factures</h3>
                <div className="flex gap-2">
                  {factures.length === 0 ? (
                    <p
                      className={`text-sm ${hasFacturesError ? "text-red-600" : "text-muted-foreground"}`}
                    >
                      Aucun code
                    </p>
                  ) : (
                    factures.map((facture) => (
                      <p className="border py-0.5 px-1 bg-accent text-sm">
                        {facture}
                      </p>
                    ))
                  )}
                </div>
              </div>
              <div className="text-[15px] border-b flex items-center justify-between py-2">
                <h3 className="text-muted-foreground">Paiements</h3>
                <div className="flex gap-2">
                  {paiements.length === 0 ? (
                    <p
                      className={`text-sm ${hasPaiementsError ? "text-red-600" : "text-muted-foreground"}`}
                    >
                      Aucun code
                    </p>
                  ) : (
                    paiements.map((paiement) => (
                      <p className="border py-0.5 px-1 bg-accent text-sm">
                        {paiement}
                      </p>
                    ))
                  )}
                </div>
              </div>
              <div className="text-[15px] flex items-center justify-between py-2">
                <h3 className="text-muted-foreground">Report à nouveau</h3>
                <div className="flex gap-2">
                  {reports.length === 0 ? (
                    <p
                      className={`text-sm ${hasReportsError ? "text-red-600" : "text-muted-foreground"}`}
                    >
                      Aucun code
                    </p>
                  ) : (
                    reports.map((report) => (
                      <p className="border py-0.5 px-1 bg-accent text-sm">
                        {report}
                      </p>
                    ))
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <ExcelUpload
          currentYearFile={currentYearFile}
          pastYearFile={pastYearFile}
          setCurrentYearFile={(file) => {
            setCurrentYearFile(file);
            setHasCurrentFileError(false);
          }}
          setPastYearFile={(file) => {
            setPastYearFile(file);
            setHasPastFileError(false);
          }}
          hasCurrentFileError={hasCurrentFileError}
          hasPastFileError={hasPastFileError}
        />
        <div className="flex gap-5">
          <SupplierExcluded
            config={configuration}
            setRefreshConfig={setRefreshConfig}
          />
          <PayementCondition
            config={configuration}
            setRefreshConfig={setRefreshConfig}
          />
        </div>
        <div className="flex justify-end">
          <Button onClick={() => generateReport()}>Générer le rapport</Button>
        </div>
      </div>
    </div>
  );
}

export default App;
