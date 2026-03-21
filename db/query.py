import pandas as pd
import warnings
from datetime import datetime, timedelta
from db.connection import get_connection

warnings.filterwarnings('ignore', category=UserWarning)

def run_query(database, year, start_date, end_date):
    conn = None
    year_end = (datetime.strptime(start_date, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        conn = get_connection(database)

        query = f"""SELECT * FROM (
        SELECT  CT_Intitule as Fournisseurs,
            EC_RefPiece as [N°Facture],
            Factures.EC_Montant as [Montant de Facture],
            Factures.Date_de_facture as [Date de facture],
            Factures.Mois_de_livraison as [Mois de livraison],
            Paiements.Date_de_facture as [Date de paiement],
            Paiements.EC_Montant as montant_paiement,
            Commentaire as [Condition de paiement en jrs],
            CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as [Délai de paiement en jrs],
            FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as [Date d'échéance], CASE 
            WHEN Paiements.Date_de_facture IS NULL THEN
                CASE
                    WHEN CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE) >= CAST('{end_date}' AS DATE) THEN NULL
                    ELSE CAST(DATEDIFF(day,
                        CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE),
                        CAST('{end_date}' AS DATE)
                    ) AS VARCHAR)
                END
            WHEN CAST(jour_paiement - jour_facture AS INT) - Commentaire <= 0 THEN NULL
            ELSE CAST(CAST(jour_paiement - jour_facture AS INT) - Commentaire AS VARCHAR)
        END as Retard_en_jours,
        CASE 
            WHEN Paiements.Date_de_facture IS NULL THEN
                CASE 
                    WHEN CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE) >= CAST('{end_date}' AS DATE) THEN NULL
                    ELSE CAST(DATEDIFF(month,
                        CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE),
                        CAST('{end_date}' AS DATE)
                    ) + 1 AS VARCHAR)
                END
            WHEN CAST(Paiements.Date_de_facture AS DATE) <= CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE) THEN NULL
            ELSE CAST(DATEDIFF(month,
                CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE),
                CAST(Paiements.Date_de_facture AS DATE)
            ) + 1 AS VARCHAR)
        END as Retard_en_mois
        FROM (
        SELECT c.CT_Intitule ,JO_Num, e.CT_Num as N_Fournisseur,
            FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
            DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison,
                EC_Sens, EC_RefPiece, EC_Lettrage, EC_Montant,
                CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_facture,
                CONVERT(INT, CT_Commentaire) as Commentaire
        FROM dbo.F_ECRITUREC as e 
        JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
        WHERE JO_Num IN ('AC')
        AND e.CT_Num NOT LIKE '3%'
        AND e.CT_Num <> 'NULL' 
        AND JM_Date BETWEEN '{start_date}' AND '{end_date}' ) as Factures
        LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
            FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
            DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison,
                EC_Lettrage, CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_paiement, EC_Montant
        FROM dbo.F_ECRITUREC as e
        JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
        WHERE JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
        WHERE CG_Num like '5%')  
        AND e.CT_Num NOT LIKE '3%'
        AND e.CT_Num <> 'NULL'   
        AND JM_Date BETWEEN '{start_date}' AND '{end_date}' ) as Paiements
        ON Factures.N_Fournisseur = Paiements.N_Fournisseur
        AND Factures.EC_Lettrage IS NOT NULL
        AND Paiements.EC_Lettrage IS NOT NULL
        AND LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
        AND LTRIM(RTRIM(Factures.EC_Lettrage)) <> ''
        AND LTRIM(RTRIM(Paiements.EC_Lettrage)) <> ''

        UNION

        -- Past invoices paid choosen trismester 
        SELECT  CT_Intitule as Fournisseurs,
            EC_RefPiece as [N°Facture],
            Factures.EC_Montant as [Montant de Facture],
            Factures.Date_de_facture as [Date de facture],
            Factures.Mois_de_livraison as [Mois de livraison],
            Paiements.Date_de_facture as [Date de paiement],
            Paiements.EC_Montant as montant_paiement,
            Commentaire as [Condition de paiement en jrs],
            CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as [Délai de paiement en jrs],
            FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as [Date d'échéance], CASE 
            WHEN Paiements.Date_de_facture IS NULL THEN
                CASE
                    WHEN CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE) >= CAST('{end_date}' AS DATE) THEN NULL
                    ELSE CAST(DATEDIFF(day,
                        CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE),
                        CAST('{end_date}' AS DATE)
                    ) AS VARCHAR)
                END
            WHEN CAST(jour_paiement - jour_facture AS INT) - Commentaire <= 0 THEN NULL
            ELSE CAST(CAST(jour_paiement - jour_facture AS INT) - Commentaire AS VARCHAR)
        END as Retard_en_jours,
        CASE 
            WHEN Paiements.Date_de_facture IS NULL THEN
                CASE 
                    WHEN CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE) >= CAST('{end_date}' AS DATE) THEN NULL
                    ELSE CAST(DATEDIFF(month,
                        CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE),
                        CAST('{end_date}' AS DATE)
                    ) + 1 AS VARCHAR)
                END
            WHEN CAST(Paiements.Date_de_facture AS DATE) <= CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE) THEN NULL
            ELSE CAST(DATEDIFF(month,
                CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE),
                CAST(Paiements.Date_de_facture AS DATE)
            ) + 1 AS VARCHAR)
        END as Retard_en_mois
        FROM (
            SELECT c.CT_Intitule, JO_Num, e.CT_Num as N_Fournisseur,
                FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') as Date_de_facture,
                FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy') as Mois_de_livraison,
                EC_Sens, EC_RefPiece, EC_Lettrage, EC_Montant,
                CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_facture,
                CONVERT(INT, CT_Commentaire) as Commentaire 
            FROM dbo.F_ECRITUREC as e 
            JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
            WHERE JO_Num IN ('AC')
            AND e.CT_Num NOT LIKE '3%'
            AND e.CT_Num <> 'NULL'
            AND JM_Date BETWEEN '{year}' AND '{year_end}'
        ) as Factures
        LEFT JOIN (
            SELECT e.CT_Num as N_Fournisseur,
                FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') as Date_de_facture,
            DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison,
                EC_Lettrage, EC_Montant, 
                CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_paiement
            FROM dbo.F_ECRITUREC as e
            JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
            WHERE JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
            WHERE CG_Num like '5%') 
            AND e.CT_Num NOT LIKE '3%'
            AND e.CT_Num <> 'NULL'
            AND JM_Date BETWEEN '{start_date}' AND '{end_date}'
        ) as Paiements
        ON Factures.N_Fournisseur = Paiements.N_Fournisseur
        AND Factures.EC_Lettrage IS NOT NULL
        AND Paiements.EC_Lettrage IS NOT NULL
        AND LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
        AND LTRIM(RTRIM(Factures.EC_Lettrage)) <> ''
        AND LTRIM(RTRIM(Paiements.EC_Lettrage)) <> ''
        WHERE Paiements.Date_de_facture IS NOT NULL

        UNION

        -- Past invoices still unpaid
        SELECT  CT_Intitule as Fournisseurs,
            EC_RefPiece as [N°Facture],
            Factures.EC_Montant as [Montant de Facture],
            Factures.Date_de_facture as [Date de facture],
            Factures.Mois_de_livraison as [Mois de livraison],
            Paiements.Date_de_facture as [Date de paiement],
            Paiements.EC_Montant as montant_paiement,
            Commentaire as [Condition de paiement en jrs],
            CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as [Délai de paiement en jrs],
            FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as [Date d'échéance], CASE 
            WHEN Paiements.Date_de_facture IS NULL THEN
                CASE
                    WHEN CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE) >= CAST('{end_date}' AS DATE) THEN NULL
                    ELSE CAST(DATEDIFF(day,
                        CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE),
                        CAST('{end_date}' AS DATE)
                    ) AS VARCHAR)
                END
            WHEN CAST(jour_paiement - jour_facture AS INT) - Commentaire <= 0 THEN NULL
            ELSE CAST(CAST(jour_paiement - jour_facture AS INT) - Commentaire AS VARCHAR)
        END as Retard_en_jours,
        CASE 
            WHEN Paiements.Date_de_facture IS NULL THEN
                CASE 
                    WHEN CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE) >= CAST('{end_date}' AS DATE) THEN NULL
                    ELSE CAST(DATEDIFF(month,
                        CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE),
                        CAST('{end_date}' AS DATE)
                    ) + 1 AS VARCHAR)
                END
            WHEN CAST(Paiements.Date_de_facture AS DATE) <= CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE) THEN NULL
            ELSE CAST(DATEDIFF(month,
                CAST(FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') AS DATE),
                CAST(Paiements.Date_de_facture AS DATE)
            ) + 1 AS VARCHAR)
        END as Retard_en_mois
        FROM (
        SELECT c.CT_Intitule ,JO_Num, e.CT_Num as N_Fournisseur,
            FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
            DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison,
                EC_Sens, EC_RefPiece, EC_Lettrage, EC_Montant,
                CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_facture,
                CONVERT(INT, CT_Commentaire) as Commentaire
        FROM dbo.F_ECRITUREC as e 
        JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
        WHERE JO_Num IN ('AC')
        AND e.CT_Num NOT LIKE '3%'
        AND e.CT_Num <> 'NULL'  
        AND JM_Date BETWEEN '{year}' AND '{year_end}' ) as Factures
        LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
            FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
            DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison, EC_Montant,
                EC_Lettrage, CAST(CAST(FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') AS DATETIME) AS INT) as jour_paiement
        FROM dbo.F_ECRITUREC as e
        JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
        WHERE JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
        WHERE CG_Num like '5%')  
        AND e.CT_Num NOT LIKE '3%'
        AND e.CT_Num <> 'NULL' 
        AND JM_Date BETWEEN '{year}' AND '{end_date}' ) as Paiements
        ON Factures.N_Fournisseur = Paiements.N_Fournisseur
        AND Factures.EC_Lettrage IS NOT NULL
        AND Paiements.EC_Lettrage IS NOT NULL
        AND LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
        AND LTRIM(RTRIM(Factures.EC_Lettrage)) <> ''
        AND LTRIM(RTRIM(Paiements.EC_Lettrage)) <> ''
        WHERE Paiements.Date_de_facture IS NULL

        ) as full_report
        ORDER BY Fournisseurs asc"""
        data = pd.read_sql(query, conn)
        return data
    except Exception as e:
        print(f"Query error: {e}")
        return None
    finally:
        if conn:
            conn.close()