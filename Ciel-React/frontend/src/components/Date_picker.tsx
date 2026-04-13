"use client";

import { format } from "date-fns";
import { fr } from "date-fns/locale";
import { ChevronDownIcon } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { useState } from "react";

interface DatePickerInputProps {
  date: Date | undefined;
  onDateChange: (date: Date | undefined) => void;
  label: string;
}

export function DatePickerInput({
  date,
  onDateChange,
  label,
}: DatePickerInputProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="flex flex-col gap-1">
      <label className="text-sm text-muted-foreground">{label}</label>
      <Popover open={open} onOpenChange={setOpen}>
        <PopoverTrigger asChild>
          <Button
            variant="outline"
            data-empty={!date}
            className="w-[212px] justify-between text-left font-normal data-[empty=true]:text-muted-foreground"
          >
            {date ? (
              format(date, "PPP", { locale: fr })
            ) : (
              <span>Choisir une date</span>
            )}
            <ChevronDownIcon />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-0" align="start">
          <Calendar
            mode="single"
            selected={date}
            onSelect={(date) => {
              setOpen(false);
              onDateChange(date);
            }}
            defaultMonth={date}
            locale={fr}
          />
        </PopoverContent>
      </Popover>
    </div>
  );
}
