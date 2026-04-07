import datetime
import pandas as pd

JOURNAL_CODES = ['HA', 'CA', 'BC', 'AN']


def run_query(current_year_file, past_year_files, excluded_suppliers, start_date, end_date, output_path='full_report.xlsx'):
    start_year = datetime.date(start_date.year, 1, 1)

    df_clean, df_clean_past = clean_excel(current_year_file, past_year_files, excluded_suppliers)

    q1 = query_1(df_clean, start_date, end_date)
    q2 = query_2(df_clean, start_date, end_date, start_year)
    q3 = query_3(df_clean, start_date, end_date, start_year)
    q4 = query_4(df_clean, df_clean_past, start_date, end_date, start_year)
    q5 = query_5(df_clean, df_clean_past, end_date, start_year)

    result = pd.concat([q1, q2, q3, q4, q5])
    result.to_excel(output_path, index=False)
    return output_path


def clean_excel(current_year_file, past_year_files, excluded_suppliers):
    cleaned_rows_current_year = []
    cleaned_rows_past_year = []
    current_fournisseur_number = None
    current_fournisseur_name = None

    df_raw_current_year = pd.read_excel(current_year_file, header=None)
    for i, row in df_raw_current_year.iterrows():
        first_cell = str(row[0]).strip()

        if first_cell.startswith('4411'):
            current_fournisseur_number = first_cell.split()[0]
            current_fournisseur_name = ' '.join(first_cell.split()[1:])

        elif str(row[1]).strip() in JOURNAL_CODES:
            cleaned_rows_current_year.append({
                'Num fournisseur': current_fournisseur_number,
                'Nom fournisseur': current_fournisseur_name,
                'journal': row[1],
                'date': row[2].date() if pd.notna(row[2]) else None,
                'N° de pièce': row[3],
                'libelle': row[4],
                'montant_debit': row[8],
                'montant_credit': row[10],
                'lettrage': row[9]
            })

    for past_year_file in past_year_files:
        df_raw_past_year = pd.read_excel(past_year_file, header=None)
        for _, row in df_raw_past_year.iterrows():
            first_cell = str(row[0]).strip()

            if first_cell.startswith('4411'):
                current_fournisseur_number = first_cell.split()[0]
                current_fournisseur_name = ' '.join(first_cell.split()[1:])

            elif str(row[1]).strip() in JOURNAL_CODES:
                cleaned_rows_past_year.append({
                    'Num fournisseur': current_fournisseur_number,
                    'Nom fournisseur': current_fournisseur_name,
                    'journal': row[1],
                    'date': row[2].date() if pd.notna(row[2]) else None,
                    'N° de pièce': row[3],
                    'libelle': row[4],
                    'montant_debit': row[8],
                    'montant_credit': row[10],
                    'lettrage': row[9]
                })

    df_results_current_year = pd.DataFrame(cleaned_rows_current_year)
    df_clean = df_results_current_year[~df_results_current_year['Num fournisseur'].isin(excluded_suppliers)]

    df_results_past_year = pd.DataFrame(cleaned_rows_past_year)
    df_clean_past = df_results_past_year[~df_results_past_year['Num fournisseur'].isin(excluded_suppliers)]
    df_clean_past = df_clean_past[df_clean_past['journal'] == 'HA']

    return df_clean, df_clean_past


def query_1(df_clean, start_date, end_date):
    """Factures trimestre payées / non payées"""
    factures = df_clean[
        (df_clean['journal'].isin(['HA'])) &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'].between(start_date, end_date))
    ]
    paiements = df_clean[
        (
            ((df_clean['journal'].isin(['BC', 'CA', 'AN'])) & (df_clean['montant_debit'].notna()))
            |
            ((df_clean['journal'] == 'HA') & (df_clean['montant_credit'] < 0))
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


def query_2(df_clean, start_date, end_date, start_year):
    """Factures antérieures payées dans le trimestre"""
    start_date_1 = start_date - datetime.timedelta(days=1)

    factures = df_clean[
        (df_clean['journal'].isin(['HA'])) &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'].between(start_year, start_date_1))
    ]
    paiements = df_clean[
        (
            ((df_clean['journal'].isin(['BC', 'CA', 'AN'])) & (df_clean['montant_debit'].notna()))
            |
            ((df_clean['journal'] == 'HA') & (df_clean['montant_credit'] < 0))
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


def query_3(df_clean, start_date, end_date, start_year):
    """Factures antérieures non payées"""
    start_date_1 = start_date - datetime.timedelta(days=1)

    factures = df_clean[
        (df_clean['journal'].isin(['HA'])) &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'].between(start_year, start_date_1))
    ]
    paiements = df_clean[
        (
            ((df_clean['journal'].isin(['BC', 'CA', 'AN'])) & (df_clean['montant_debit'].notna()))
            |
            ((df_clean['journal'] == 'HA') & (df_clean['montant_credit'] < 0))
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
    return join[join['date_facture'].notna()]


def query_4(df_clean, df_clean_past, start_date, end_date, start_year):
    """RN payés dans le trimestre"""
    factures_AN = df_clean[
        (df_clean['journal'] == 'AN') &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'] == start_year)
    ]
    factures_HA = df_clean_past[
        (df_clean_past['journal'] == 'HA') &
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
    paiements = df_clean[
        (
            ((df_clean['journal'].isin(['BC', 'CA', 'AN'])) & (df_clean['montant_debit'].notna())) |
            ((df_clean['journal'] == 'HA') & (df_clean['montant_credit'] < 0))
        ) &
        (df_clean['date'].between(start_date, end_date))
    ].copy()
    paiements['montant_paiement'] = paiements['montant_debit'].fillna(paiements['montant_credit'].abs())

    join = pd.merge(
        matched_AN,
        paiements[['Num fournisseur', 'N° de pièce', 'date', 'montant_paiement', 'lettrage']],
        on=['Num fournisseur', 'lettrage'],
        how='left',
        suffixes=('_an', '_paiement')
    )
    return join[join['date'].notna()]


def query_5(df_clean, df_clean_past, end_date, start_year):
    """RN non encore payés"""
    factures_AN = df_clean[
        (df_clean['journal'] == 'AN') &
        (df_clean['montant_credit'].notna()) &
        (df_clean['montant_credit'] > 0) &
        (df_clean['date'] == start_year)
    ]
    factures_HA = df_clean_past[
        (df_clean_past['journal'] == 'HA') &
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
    paiements = df_clean[
        (
            ((df_clean['journal'].isin(['BC', 'CA', 'AN'])) & (df_clean['montant_debit'].notna())) |
            ((df_clean['journal'] == 'HA') & (df_clean['montant_credit'] < 0))
        ) &
        (df_clean['date'].between(start_year, end_date))
    ].copy()
    paiements['montant_paiement'] = paiements['montant_debit'].fillna(paiements['montant_credit'].abs())

    join = pd.merge(
        matched_AN,
        paiements[['Num fournisseur', 'N° de pièce', 'date', 'montant_paiement', 'lettrage']],
        on=['Num fournisseur', 'lettrage'],
        how='left',
        suffixes=('_an', '_paiement')
    )
    return join[join['date'].isna()]


if __name__ == '__main__':
    import datetime
    output = run_query(
        current_year_file='GRAND LIVRE FOURNISSEURS 2025.xlsx',
        past_year_files=['Grand livre fournisseurs 2024 (SOMPAGRAF).xlsx'],
        excluded_suppliers=[],
        start_date=datetime.date(2025, 6, 1),
        end_date=datetime.date(2025, 9, 30),
    )
    print(f'Done: {output}')
