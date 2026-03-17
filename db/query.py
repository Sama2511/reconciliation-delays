import pandas as pd
from db.connection import get_connection


def run_query(database,year, start_date, end_date):

    try:
            
        conn = get_connection(database)
        query = f"""-- trismester table
                SELECT * FROM (
                SELECT JO_Num, CT_Intitule, factures.N_Fournisseur, Factures.EC_Lettrage,EC_RefPiece, Factures.Date_de_facture, Paiements.Date_de_facture as Date_de_paiement, Factures.Mois_de_livraison, CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as Delai_de_paiement_en_jour, Factures.EC_Montant as montant_facture, Paiements.EC_Montant as montant_paiement, Commentaire as Condition_de_paiement, FORMAT(DATEADD(day,  Commentaire , CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as date_d_echeance, CASE 
                    WHEN CAST(jour_paiement - jour_facture AS INT) - Commentaire <= 0 THEN NULL
                    ELSE CAST(CAST(jour_paiement - jour_facture AS INT) - Commentaire AS VARCHAR)
                END as Retard_en_jours
                FROM (
                SELECT c.CT_Intitule ,JO_Num, e.CT_Num as N_Fournisseur,
                    FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
                    FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison,
                        EC_Sens, EC_RefPiece, EC_Lettrage, EC_Montant,
                        CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_facture,

                        CONVERT(INT, CT_Commentaire) as Commentaire
                FROM dbo.F_ECRITUREC as e 
                JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
                WHERE JO_Num IN ('AC')
                AND e.CT_Num  NOT LIKE '3%'
                AND e.CT_Num <> 'NULL' 
                AND JM_Date BETWEEN '{start_date}' AND '{end_date}' ) as Factures
                LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
                    FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
                    FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison,
                        EC_Lettrage, CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_paiement, EC_Montant
                FROM dbo.F_ECRITUREC as e
                JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
                WHERE JO_Num IN ('BP', 'SG', 'CA', 'OD') 
                AND e.CT_Num  NOT LIKE '3%'
                AND e.CT_Num <> 'NULL'   
                AND JM_Date BETWEEN '{start_date}' AND '{end_date}' ) as Paiements
                ON Factures.N_Fournisseur = Paiements.N_Fournisseur
                AND Factures.EC_Lettrage = Paiements.EC_Lettrage 

                UNION 

                -- Past invoices paid in the chosen trimester

                SELECT JO_Num, CT_Intitule, factures.N_Fournisseur, Factures.EC_Lettrage,EC_RefPiece, Factures.Date_de_facture, Paiements.Date_de_facture as Date_de_paiement, Factures.Mois_de_livraison, CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as Delai_de_paiement_en_jour, Factures.EC_Montant as montant_facture, Paiements.EC_Montant as montant_paiement, Commentaire as Condition_de_paiement, FORMAT(DATEADD(day,  Commentaire , CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as date_d_echeance, CASE 
                    WHEN CAST(jour_paiement - jour_facture AS INT) - Commentaire <= 0 THEN NULL
                    ELSE CAST(CAST(jour_paiement - jour_facture AS INT) - Commentaire AS VARCHAR)
                END as Retard_en_jours
                FROM (
                    SELECT c.CT_Intitule, JO_Num, e.CT_Num as N_Fournisseur,
                        FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') as Date_de_facture,
                        FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy') as Mois_de_livraison,
                        EC_Sens, EC_RefPiece, EC_Lettrage,EC_Montant,
                        CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_facture,
                        CONVERT(INT, CT_Commentaire) as Commentaire 
                    FROM dbo.F_ECRITUREC as e 
                    JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
                    WHERE JO_Num IN ('AC')
                    AND e.CT_Num NOT LIKE '3%'
                    AND e.CT_Num <> 'NULL'
                    AND JM_Date between '{year}'and '{start_date}'  
                ) as Factures
                LEFT JOIN (
                    SELECT e.CT_Num as N_Fournisseur,
                        FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') as Date_de_facture,
                        FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy') as Mois_de_livraison,
                        EC_Lettrage, EC_Montant, 
                        CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_paiement
                    FROM dbo.F_ECRITUREC as e
                    JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
                    WHERE JO_Num IN ('BP', 'SG', 'CA', 'OD') 
                    AND e.CT_Num NOT LIKE '3%'
                    AND e.CT_Num <> 'NULL'
                    AND JM_Date BETWEEN '{start_date}' AND '{end_date}'  
                ) as Paiements
                ON Factures.N_Fournisseur = Paiements.N_Fournisseur
                AND Factures.EC_Lettrage = Paiements.EC_Lettrage
                WHERE Paiements.Date_de_facture IS NOT NULL

                UNION  

                -- past invoice not payed table


                SELECT JO_Num, CT_Intitule, factures.N_Fournisseur, Factures.EC_Lettrage,EC_RefPiece, Factures.Date_de_facture, Paiements.Date_de_facture as Date_de_paiement, Factures.Mois_de_livraison, CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as Delai_de_paiement_en_jour, Factures.EC_Montant as montant_facture, Paiements.EC_Montant as montant_paiement, Commentaire as Condition_de_paiement, FORMAT(DATEADD(day,  Commentaire , CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as date_d_echeance, CASE 
                    WHEN CAST(jour_paiement - jour_facture AS INT) - Commentaire <= 0 THEN NULL
                    ELSE CAST(CAST(jour_paiement - jour_facture AS INT) - Commentaire AS VARCHAR)
                END as Retard_en_jours
                FROM (
                SELECT c.CT_Intitule ,JO_Num, e.CT_Num as N_Fournisseur,
                    FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
                    FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison,
                        EC_Sens, EC_RefPiece, EC_Lettrage,EC_Montant,
                        CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_facture,
                        CONVERT(INT, CT_Commentaire) as Commentaire
                FROM dbo.F_ECRITUREC as e 
                JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
                WHERE JO_Num IN ('AC')
                AND e.CT_Num  NOT LIKE '3%'
                AND e.CT_Num <> 'NULL'  
                AND JM_Date BETWEEN '{year}' AND '{start_date}' ) as Factures
                LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
                    FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
                    FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison, EC_Montant,
                        EC_Lettrage, CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_paiement
                FROM dbo.F_ECRITUREC as e
                JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
                WHERE JO_Num IN ('BP', 'SG', 'CA', 'OD') 
                AND e.CT_Num  NOT LIKE '3%'
                AND e.CT_Num <> 'NULL' 
                AND JM_Date BETWEEN '{year}' AND '{end_date}' ) as Paiements
                ON Factures.N_Fournisseur = Paiements.N_Fournisseur
                AND Factures.EC_Lettrage = Paiements.EC_Lettrage
                WHERE Paiements.Date_de_facture is  NULL

                ) as full_report
                ORDER BY CT_Intitule asc"""
        
        data = pd.read_sql(query, conn)
        return data
    except Exception:
        return None
    finally:
        if conn:
            conn.close()

