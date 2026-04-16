import pandas as pd


def filter_supplier_condition(num_supplier, condition_default, custom_condition):
    return custom_condition.get(num_supplier, condition_default)


def clean_excel(current_year_file, past_year_file, excluded_suppliers, condition_default, custom_condition, journal_codes,journal_achat):
    cleaned_rows_current_year = []
    cleaned_rows_past_year = []
    current_supplier_number = None
    current_supplier_name = None
    current_payement_condition = None

    df_raw_current_year = pd.read_excel(current_year_file, header=None)
    for _, row in df_raw_current_year.iterrows():
        first_cell = str(row[0]).strip()

        if first_cell.startswith('4411'):
            current_supplier_number = first_cell.split()[0]
            current_supplier_name = ' '.join(first_cell.split()[1:])
            current_payement_condition = filter_supplier_condition(current_supplier_number, condition_default, custom_condition)

        elif str(row[1]).strip() in journal_codes:
            cleaned_rows_current_year.append({
                'Num fournisseur': current_supplier_number,
                'Nom fournisseur': current_supplier_name,
                'journal': row[1],
                'date': row[2].date() if pd.notna(row[2]) else None,
                'N° de pièce': row[3],
                'libelle': row[4],
                'montant_debit': row[8],
                'montant_credit': row[10],
                'lettrage': row[9],
                'Condition de paiement': current_payement_condition,
            })

    current_supplier_number = None
    current_supplier_name = None
    current_payement_condition = None

    df_raw_past_year = pd.read_excel(past_year_file, header=None)
    for _, row in df_raw_past_year.iterrows():
        first_cell = str(row[0]).strip()

        if first_cell.startswith('4411'):
            current_supplier_number = first_cell.split()[0]
            current_supplier_name = ' '.join(first_cell.split()[1:])
            current_payement_condition = filter_supplier_condition(current_supplier_number, condition_default, custom_condition)

        elif str(row[1]).strip() in journal_codes:
            cleaned_rows_past_year.append({
                'Num fournisseur': current_supplier_number,
                'Nom fournisseur': current_supplier_name,
                'journal': row[1],
                'date': row[2].date() if pd.notna(row[2]) else None,
                'N° de pièce': row[3],
                'libelle': row[4],
                'montant_debit': row[8],
                'montant_credit': row[10],
                'lettrage': row[9],
                'Condition de paiement': current_payement_condition,
            })

    df_results_current_year = pd.DataFrame(cleaned_rows_current_year)
    df_clean = df_results_current_year[~df_results_current_year['Num fournisseur'].isin(excluded_suppliers)]

    df_results_past_year = pd.DataFrame(cleaned_rows_past_year)
    df_clean_past = df_results_past_year[~df_results_past_year['Num fournisseur'].isin(excluded_suppliers)]
    df_clean_past = df_clean_past[df_clean_past['journal'].isin(journal_achat)]

    return df_clean, df_clean_past