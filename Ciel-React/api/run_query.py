import datetime
import pandas as pd
import os 
from api.queries import query_1, query_2, query_3, query_4, query_5
from api.data_clean import clean_excel




def month_delay(due_date, payment_date, end_date):

    if pd.notna(payment_date):
        return ((payment_date.year - due_date.year)*12 + (payment_date.month - due_date.month) + 1)
    else:
        return ((end_date.year - due_date.year)*12 + (end_date.month - due_date.month) +1 )
    


def run_query(current_year_file, past_year_files, excluded_suppliers, start, end_date, output_path):
    start_date = datetime.datetime.strptime(start, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    start_year = datetime.date(start_date.year, 1, 1)
    df_clean, df_clean_past = clean_excel(current_year_file, past_year_files, excluded_suppliers)

    q1 = query_1(df_clean, start_date, end_date)
    q2 = query_2(df_clean, start_date, end_date, start_year)
    q3 = query_3(df_clean, start_date, end_date, start_year)
    q4 = query_4(df_clean, df_clean_past, start_date, end_date, start_year)
    q5 = query_5(df_clean, df_clean_past, end_date, start_year)

    result = pd.concat([q1, q2, q3, q4, q5])
    result['Statut Paiement'] = result['date_paiement'].apply(lambda x: 'Réglée' if pd.notna(x) else 'Non Réglée')

    result.drop(columns=['Num fournisseur', 'montant_debit','lettrage'],inplace=True)
    result.rename(columns={'N° de pièce':'N° Facture'},inplace=True)
    result.rename(columns={'montant_credit':'Montant Facture'},inplace=True)

    result['mois_livraison'] = result['date_facture'].apply(
        lambda x: x.strftime('%B-%Y').capitalize() if pd.notna(x) else None
    )

    result['date_paiement'] = pd.to_datetime(result['date_paiement'])
    result['date_facture'] = pd.to_datetime(result['date_facture'])

    result["date d'echeance"] = result['date_facture'] + pd.to_timedelta(result['Condition de paiement'], unit='D')


    result['Delai paiement (jrs)'] = (result['date_paiement'] - result['date_facture']).dt.days.clip(lower=0)

    result['Retard Jours'] = (result['Delai paiement (jrs)'] - result['Condition de paiement']).where(result['Delai paiement (jrs)'] > result['Condition de paiement'])
    
    result['Retard mois'] = result.apply(
    lambda row: month_delay(row["date d'echeance"], row['date_paiement'], end_date) 
    if (row['Retard Jours'] > 0) or (pd.isna(row['date_paiement']) and row["date d'echeance"] < pd.Timestamp(end_date)) 
    else None, axis=1
)
    
    result['date_paiement'] = result['date_paiement'].dt.date
    result['date_facture'] = result['date_facture'].dt.date
    result["date d'echeance"] = result["date d'echeance"].dt.date


    result.to_excel(output_path, index=False)

    os.startfile(output_path)