import pandas as pd
import warnings
from datetime import datetime, timedelta
from db.connection import get_connection

warnings.filterwarnings('ignore', category=UserWarning)

def run_query(database, start_date, end_date):
    year = datetime.strptime(start_date, '%Y-%m-%d').year
    year_start = f'{year}-01-01'

    start_date_minus1 = (datetime.strptime(start_date, '%Y-%m-%d')-timedelta(days=1)).strftime('%Y-%m-%d')
   
    conn = None
    try:
        conn = get_connection(database)

        query = f"""

--Invoices payed in trimester
SELECT * FROM (
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
        DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_facture,
        CONVERT(INT, CT_Commentaire) as Commentaire
FROM dbo.F_ECRITUREC as e 
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE JO_Num IN ('AC')
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL' 
AND CONVERT(date, JM_Date) BETWEEN '{start_date}' AND '{end_date}' ) as Factures -- debut period / fin  period
LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison,
        EC_Lettrage, DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement, EC_Montant
FROM dbo.F_ECRITUREC as e
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
WHERE CG_Num like '5%')  
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL'   
AND CONVERT(date, JM_Date) BETWEEN '{start_date}' AND '{end_date}' ) as Paiements
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
           DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison,
           EC_Sens, EC_RefPiece, EC_Lettrage, EC_Montant,
           DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_facture,
           CONVERT(INT, CT_Commentaire) as Commentaire 
    FROM dbo.F_ECRITUREC as e 
    JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
    WHERE JO_Num IN ('AC')
    AND e.CT_Num NOT LIKE '3%'
    AND e.CT_Num <> 'NULL'
    AND CONVERT(date, JM_Date) BETWEEN '{year_start}' AND '{start_date_minus1}' -- 01-01 debut period / debut period - 1 
) as Factures
LEFT JOIN (
    SELECT e.CT_Num as N_Fournisseur,
           FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') as Date_de_facture,
           DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison,
           EC_Lettrage, EC_Montant, 
           DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement
    FROM dbo.F_ECRITUREC as e
    JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
    WHERE JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
    WHERE CG_Num like '5%') 
    AND e.CT_Num NOT LIKE '3%'
    AND e.CT_Num <> 'NULL'
    AND CONVERT(date, JM_Date) BETWEEN '{start_date}' AND '{end_date}'  -- debut period - fin period  
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
        DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_facture,
        CONVERT(INT, CT_Commentaire) as Commentaire
FROM dbo.F_ECRITUREC as e 
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE JO_Num IN ('AC')
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL'  
 AND CONVERT(date, JM_Date) BETWEEN '{year_start}' AND '{start_date_minus1}' -- 01-01 debut period / fin period - 1 
 ) as Factures
LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison, EC_Montant,
        EC_Lettrage, DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement
FROM dbo.F_ECRITUREC as e
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
WHERE CG_Num like '5%')  
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL' 
AND CONVERT(date, JM_Date) BETWEEN '{year_start}' AND '{end_date}'  -- 01-01 debut periode / debut periode -1 
) as Paiements
ON Factures.N_Fournisseur = Paiements.N_Fournisseur
AND Factures.EC_Lettrage IS NOT NULL
AND Paiements.EC_Lettrage IS NOT NULL
AND LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
AND LTRIM(RTRIM(Factures.EC_Lettrage)) <> ''
AND LTRIM(RTRIM(Paiements.EC_Lettrage)) <> ''
WHERE Paiements.Date_de_facture IS NULL

UNION

-- PAID RN in choosen trimester
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
    SELECT c.CT_Intitule, AC.JO_Num, AC.CT_Num as N_Fournisseur,
       FORMAT(DATEADD(day, EC_Jour - 1, AC.JM_Date), 'yyyy/MM/dd') as Date_de_facture,
       DATENAME(month, DATEADD(day, EC_Jour - 1, AC.JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, AC.JM_Date)) AS VARCHAR) as Mois_de_livraison,
       EC_Sens, AC.EC_RefPiece, RN.EC_Lettrage, EC_Montant,
       DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, AC.JM_Date)) as jour_facture,
       CONVERT(INT, CT_Commentaire) as Commentaire
FROM dbo.F_ECRITUREC as AC
JOIN dbo.F_COMPTET as c on c.CT_Num = AC.CT_Num
JOIN (
    SELECT CT_Num, EC_RefPiece, EC_Lettrage
    FROM dbo.F_ECRITUREC
    WHERE JO_Num = 'RN'
    AND CONVERT(date, JM_Date) = '{year_start}' -- 01/01 debut period
    AND CT_Num <> 'NULL'
    AND CT_Num NOT LIKE '3%'
    AND EC_RefPiece <> ''
) as RN ON AC.CT_Num = RN.CT_Num AND AC.EC_RefPiece = RN.EC_RefPiece
WHERE AC.JO_Num = 'AC'
AND AC.CT_Num NOT LIKE '3%'
AND AC.CT_Num <> 'NULL'
AND CONVERT(date, AC.JM_Date) > CONVERT(date , (select TOP 1 D_commentaire FROm dbo.P_DOSSIER)) -- date de reference
) as Factures
LEFT JOIN (
    SELECT e.CT_Num as N_Fournisseur,
           FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') as Date_de_facture,
           DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison,
           EC_Lettrage, EC_Montant, 
           DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement
    FROM dbo.F_ECRITUREC as e
    JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
    WHERE JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
    WHERE CG_Num like '5%') 
    AND e.CT_Num NOT LIKE '3%'
    AND e.CT_Num <> 'NULL'
    AND CONVERT(date, JM_Date) BETWEEN '{start_date}' AND '{end_date}' -- debut period / fin period 
) as Paiements
ON Factures.N_Fournisseur = Paiements.N_Fournisseur
AND Factures.EC_Lettrage IS NOT NULL
AND Paiements.EC_Lettrage IS NOT NULL
AND LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
AND LTRIM(RTRIM(Factures.EC_Lettrage)) <> ''
AND LTRIM(RTRIM(Paiements.EC_Lettrage)) <> ''
WHERE Paiements.Date_de_facture IS NOT NULL

UNION

-- RN still unpaid
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
SELECT c.CT_Intitule, AC.JO_Num, AC.CT_Num as N_Fournisseur,
       FORMAT(DATEADD(day, EC_Jour - 1, AC.JM_Date), 'yyyy/MM/dd') as Date_de_facture,
       DATENAME(month, DATEADD(day, EC_Jour - 1, AC.JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, AC.JM_Date)) AS VARCHAR) as Mois_de_livraison,
       EC_Sens, AC.EC_RefPiece, RN.EC_Lettrage, EC_Montant,
       DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, AC.JM_Date)) as jour_facture,
       CONVERT(INT, CT_Commentaire) as Commentaire
FROM dbo.F_ECRITUREC as AC
JOIN dbo.F_COMPTET as c on c.CT_Num = AC.CT_Num
JOIN (
    SELECT CT_Num, EC_RefPiece, EC_Lettrage
    FROM dbo.F_ECRITUREC
    WHERE JO_Num = 'RN'
    AND CONVERT(date, JM_Date) = '{year_start}' -- 01-01 debut period
    AND CT_Num <> 'NULL'
    AND CT_Num NOT LIKE '3%'
    AND EC_RefPiece <> ''
) as RN ON AC.CT_Num = RN.CT_Num AND AC.EC_RefPiece = RN.EC_RefPiece
WHERE AC.JO_Num = 'AC'
AND AC.CT_Num NOT LIKE '3%'
AND AC.CT_Num <> 'NULL'
AND CONVERT(date, AC.JM_Date) > CONVERT(date, (select TOP 1 D_commentaire FROm dbo.P_DOSSIER)) -- date de reference
) as Factures 
LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison, EC_Montant,
        EC_Lettrage, DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement
FROM dbo.F_ECRITUREC as e
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
WHERE CG_Num like '5%')  
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL' 
AND CONVERT(date, JM_Date) BETWEEN '{year_start}' AND '{end_date}' ) as Paiements  -- 01/01 debut period / fin period
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