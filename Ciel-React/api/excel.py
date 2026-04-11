
import datetime
import pandas as pd
import locale
import os

locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')


exclude_supplier = ['12123123','12132189']
journal_achat = ['HA']
journal_report_nouveau = ['AN']
journal_tresorie = ['CA','BC']
journal_codes= journal_achat + journal_tresorie + journal_report_nouveau
custom_condition = [{'44111041':90},{'44111021':120}]


def filter_supplier_condition(num_supplier):
    for supplier in custom_condition:
        for key, value in supplier.items():
            if num_supplier == key:
                return value
    return 30

def month_delay(due_date, payment_date, end_date):
    if pd.notna(payment_date):
        return ((payment_date.year - due_date.year)*12 + (payment_date.month - due_date.month) + 1)
    else:
        return ((end_date.year - due_date.year)*12 + (end_date.month - due_date.month) +1 )
    

def clean_excel(current_year_file, past_year_file, excluded_suppliers):
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
            current_payement_condition = filter_supplier_condition(current_supplier_number)


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
            current_payement_condition = filter_supplier_condition(current_supplier_number)

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

"""Invoice from Trimester"""
def query_1(df_clean, start_date, end_date):
    factures = df_clean[
        (df_clean['journal'].isin(journal_achat)) &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'].between(start_date, end_date))
    ]
    paiements = df_clean[
        (
            ((df_clean['journal'].isin(journal_codes)) & (df_clean['montant_debit'].notna()))
            |
            ((df_clean['journal'].isin(journal_achat)) & (df_clean['montant_credit'] < 0))
        ) &
        (df_clean['date'].between(start_date, end_date))
    ].copy()
    paiements['montant_paiement'] = paiements['montant_debit'].fillna(paiements['montant_credit'].abs())

    result = pd.merge(
        factures,
        paiements[['Num fournisseur', 'lettrage', 'montant_paiement', 'date']],
        on=['Num fournisseur', 'lettrage'],
        how='left',
        suffixes=('_facture', '_paiement')
    )
    return result


"""Past Invoices paid in trimester"""
def query_2(df_clean, start_date, end_date, start_year):
    start_date_minus_1 = start_date - datetime.timedelta(days=1)

    factures = df_clean[
        (df_clean['journal'].isin(journal_achat)) &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'].between(start_year, start_date_minus_1))
    ]
    paiements = df_clean[
        (
            ((df_clean['journal'].isin(journal_codes)) & (df_clean['montant_debit'].notna()))
            |
            ((df_clean['journal'].isin(journal_achat)) & (df_clean['montant_credit'] < 0))
        ) &
        (df_clean['date'].between(start_date, end_date))
    ].copy()
    paiements['montant_paiement'] = paiements['montant_debit'].fillna(paiements['montant_credit'].abs())

    join = pd.merge(
        factures,
        paiements[['Num fournisseur', 'lettrage', 'montant_paiement', 'date']],
        on=['Num fournisseur', 'lettrage'],
        how='left',
        suffixes=('_facture', '_paiement')
    )
    return join[join['date_paiement'].notna()]


"""Past invoice not paid yet"""
def query_3(df_clean, start_date, end_date, start_year):
    start_date_minus_1 = start_date - datetime.timedelta(days=1)

    factures = df_clean[
        (df_clean['journal'].isin(journal_achat)) &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'].between(start_year, start_date_minus_1))
    ]
    paiements = df_clean[
        (
            ((df_clean['journal'].isin(journal_codes)) & (df_clean['montant_debit'].notna()))
            |
            ((df_clean['journal'].isin(journal_achat)) & (df_clean['montant_credit'] < 0))
        ) &
        (df_clean['date'].between(start_year, end_date))
    ].copy()
    paiements['montant_paiement'] = paiements['montant_debit'].fillna(paiements['montant_credit'].abs())

    join = pd.merge(
        factures,
        paiements[['Num fournisseur', 'lettrage', 'montant_paiement', 'date']],
        on=['Num fournisseur', 'lettrage'],
        how='left',
        suffixes=('_facture', '_paiement')
    )
    return join[join['date_paiement'].isna()]


"""RN paid in trimester"""
def query_4(df_clean, df_clean_past, start_date, end_date, start_year):
    factures_AN = df_clean[
        (df_clean['journal'].isin(journal_report_nouveau)) &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'] == start_year)
    ]
    factures_HA = df_clean_past[
        (df_clean_past['journal'].isin(journal_achat)) &
        (df_clean_past['montant_credit'].notna()) &
        (df_clean_past['montant_credit'] > 0)
    ]
    matched_AN = pd.merge(
        factures_AN,
        factures_HA[['Num fournisseur', 'N° de pièce', 'date', 'montant_credit']],
        on=['Num fournisseur', 'N° de pièce', 'montant_credit'],
        how='inner',
        suffixes=('_an', '_original')
    )
    matched_AN['date_an'] = matched_AN['date_original']
    matched_AN.rename(columns={'date_an':'date'}, inplace=True)
    matched_AN.drop(columns=['date_original'], inplace=True)

    paiements = df_clean[
        (
            ((df_clean['journal'].isin(journal_codes)) & (df_clean['montant_debit'].notna())) |
            ((df_clean['journal'].isin(journal_achat)) & (df_clean['montant_credit'] < 0))
        ) &
        (df_clean['date'].between(start_date, end_date))
    ].copy()
    paiements['montant_paiement'] = paiements['montant_debit'].fillna(paiements['montant_credit'].abs())

    join = pd.merge(
        matched_AN,
        paiements[['Num fournisseur', 'date', 'montant_paiement', 'lettrage']],
        on=['Num fournisseur', 'lettrage'],
        how='left',
        suffixes=('_facture', '_paiement')
    )
    join.rename(columns={'N° de pièce_facture': 'N° de pièce'}, inplace=True)

    return join[join['date_paiement'].notna()]


"""RN not paid yet"""
def query_5(df_clean, df_clean_past, end_date, start_year):
    factures_AN = df_clean[
        (df_clean['journal'].isin(journal_report_nouveau)) &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'] == start_year)
    ]
    factures_HA = df_clean_past[
        (df_clean_past['journal'].isin(journal_achat)) &
        (df_clean_past['montant_credit'].notna()) &
        (df_clean_past['montant_credit'] > 0)
    ]
    matched_AN = pd.merge(
        factures_AN,
        factures_HA[['Num fournisseur', 'N° de pièce', 'date', 'montant_credit']],
        on=['Num fournisseur', 'N° de pièce', 'montant_credit'],
        how='inner',
        suffixes=('_an', '_original')
    )
    
    matched_AN['date_an'] = matched_AN['date_original']
    matched_AN.rename(columns={'date_an':'date'}, inplace=True)
    matched_AN.drop(columns=['date_original'], inplace=True)

    paiements = df_clean[
        (
            ((df_clean['journal'].isin(journal_codes)) & (df_clean['montant_debit'].notna())) |
            ((df_clean['journal'].isin(journal_achat)) & (df_clean['montant_credit'] < 0))
        ) &
        (df_clean['date'].between(start_year, end_date))
    ].copy()
    paiements['montant_paiement'] = paiements['montant_debit'].fillna(paiements['montant_credit'].abs())

    join = pd.merge(
        matched_AN,
        paiements[['Num fournisseur', 'date', 'montant_paiement', 'lettrage']],
        on=['Num fournisseur', 'lettrage'],
        how='left',
        suffixes=('_facture', '_paiement')
    )

    join.rename(columns={'N° de pièce_facture': 'N° de pièce'}, inplace=True)

    return join[join['date_paiement'].isna()]
