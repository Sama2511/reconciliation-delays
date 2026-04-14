import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader } from "./components/ui/card";
import { DatePickerInput } from "./components/Date_picker";
import { DialogModify } from "./components/Modify";
import { ExcelUpload } from "./components/ExcelUpload";
import type Config from "./lib/types";
import { SupplierExcluded } from "./components/SupplierExcluded";

function App() {
  const [startDate, setStartDate] = useState<Date | undefined>(undefined);
  const [endDate, setEndDate] = useState<Date | undefined>(undefined);
  const [factures, setFactures] = useState<string[]>([]);
  const [paiements, setPaiements] = useState<string[]>([]);
  const [reports, setReports] = useState<string[]>([]);
  const [configuration, setConfiguration] = useState<Config | undefined>(
    undefined,
  );
  const [currentYearFile, setCurrentYearFile] = useState<File | null>(null);
  const [pastYearFile, setPastYearFile] = useState<File | null>(null);

  const [refreshConfig, setRefreshConfig] = useState(0);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const config = await window.pywebview.api.load_config();
        setFactures(config.journal_factures);
        setPaiements(config.journal_paiements);
        setReports(config.journal_report);
        setConfiguration(config);
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

  return (
    <div className="bg-background h-screen p-5 flex justify-center ">
      <div className="flex flex-col gap-5">
        <div className="flex gap-4.75 max-h-50">
          <Card className="min-w-112.5 pt-2 gap-5 h-54">
            <CardHeader className="border-b font-bold text-lg py-3! px-4!">
              Période du rapport
            </CardHeader>
            <CardContent className="flex gap-8 pt-3  items-center mb-5">
              <DatePickerInput
                date={startDate}
                onDateChange={setStartDate}
                label="Date de début"
              />
              <DatePickerInput
                date={endDate}
                onDateChange={setEndDate}
                label="Date de fin"
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
                  {factures.map((facture) => (
                    <p className="border py-0.5 px-1 bg-accent text-sm">
                      {facture}
                    </p>
                  ))}
                </div>
              </div>
              <div className="text-[15px] border-b flex items-center justify-between py-2">
                <h3 className="text-muted-foreground">Paiements</h3>
                <div className="flex gap-2">
                  {paiements.map((paiement) => (
                    <p className="border py-0.5 px-1 bg-accent text-sm">
                      {paiement}
                    </p>
                  ))}
                </div>
              </div>
              <div className="text-[15px] flex items-center justify-between py-2">
                <h3 className="text-muted-foreground">Report à nouveau</h3>
                <div className="flex gap-2">
                  {reports.map((report) => (
                    <p className="border py-0.5 px-1 bg-accent text-sm">
                      {report}
                    </p>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <ExcelUpload
          currentYearFile={currentYearFile}
          pastYearFile={pastYearFile}
          setCurrentYearFile={setCurrentYearFile}
          setPastYearFile={setPastYearFile}
        />
        <SupplierExcluded
          config={configuration}
          setRefreshConfig={setRefreshConfig}
        />
      </div>
    </div>
  );
}

export default App;
