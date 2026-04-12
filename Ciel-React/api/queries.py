
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


