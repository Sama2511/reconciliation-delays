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

SELECT * FROM (

--Invoices payed in trimester

SELECT  CT_Intitule as Fournisseurs,Factures.EC_Intitule,
    EC_RefPiece as [N°Facture],
    Factures.EC_Montant as [Montant de Facture],
    Paiements.EC_Montant as montant_paiement,
    Factures.Date_de_facture as [Date de facture],

    CASE 
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN 'Non réglé' 
        WHEN Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <>''  THEN 'Totalement réglé' 
        WHEN Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '' AND (Paiements.EC_Pointage IS NOT NULL OR Paiements.EC_Pointage <>'' )  THEN 'Partiellement réglé'
    END AS [Statut de paiement]
    ,
    CASE
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN NULL
        WHEN Paiements.EC_Lettrage IS NOT NULL 
         AND Paiements.EC_Lettrage <> '' THEN NULL
        WHEN (Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '')
         AND Paiements.EC_Pointage IS NOT NULL 
         AND Paiements.EC_Pointage <> '' THEN Factures.EC_Montant - Paiements.EC_Montant
    END AS [Reliquat]
    ,
    Paiements.Date_de_facture as [Date de paiement],
    Factures.EC_Pointage as [facture pointage],Paiements.EC_Pointage as [paiement pointage],
    Factures.Mois_de_livraison as [Mois de livraison],
    Commentaire as [Condition de paiement en jrs],
    CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as [Délai de paiement en jrs],
    FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as [Date d'échéance], 
    CASE 
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
        EC_Sens, EC_RefPiece, EC_Lettrage, EC_Montant,EC_Intitule,
        DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_facture,
        CONVERT(INT, CT_Commentaire) as Commentaire,EC_Pointage
FROM dbo.F_ECRITUREC as e 
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE (JO_Num IN ('AC') AND EC_Sens = 1 )
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL' 
AND CONVERT(date, JM_Date) BETWEEN '{start_date}' AND '{end_date}' ) as Factures
LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison,
        EC_Lettrage, DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement, EC_Montant, EC_Pointage
FROM dbo.F_ECRITUREC as e
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE (JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
WHERE CG_Num like '5%')  
OR (JO_num IN ('AC') AND EC_Sens = 0))
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL'   
AND CONVERT(date, JM_Date) BETWEEN '{start_date}' AND '{end_date}' ) as Paiements
ON Factures.N_Fournisseur = Paiements.N_Fournisseur
AND ((Factures.EC_Lettrage IS NOT NULL AND Factures.EC_Lettrage <> '')  OR Factures.EC_Pointage IS NOT NULL AND Factures.EC_Pointage <> '') 
AND ((Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <> '')  OR Paiements.EC_Pointage IS NOT NULL AND Paiements.EC_Pointage <> '') 
AND (
    (LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
    )
    OR
    (Factures.EC_Lettrage IS NULL
    AND LTRIM(RTRIM(Factures.EC_Pointage)) = LTRIM(RTRIM(Paiements.EC_Pointage))
    AND Factures.EC_Pointage IS NOT NULL
    AND Paiements.EC_Pointage IS NOT NULL
    )
)

UNION

-- Past invoices paid choosen trismester 
SELECT  CT_Intitule as Fournisseurs,Factures.EC_Intitule,
    EC_RefPiece as [N°Facture],
    Factures.EC_Montant as [Montant de Facture],
    Paiements.EC_Montant as montant_paiement,
    Factures.Date_de_facture as [Date de facture],

    CASE 
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN 'Non réglé' 
        WHEN Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <>''  THEN 'Totalement réglé' 
        WHEN Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '' AND (Paiements.EC_Pointage IS NOT NULL OR Paiements.EC_Pointage <>'' )  THEN 'Partiellement réglé'
    END AS [Statut de paiement]
    ,
    CASE
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN NULL
        WHEN Paiements.EC_Lettrage IS NOT NULL 
         AND Paiements.EC_Lettrage <> '' THEN NULL
        WHEN (Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '')
         AND Paiements.EC_Pointage IS NOT NULL 
         AND Paiements.EC_Pointage <> '' THEN Factures.EC_Montant - Paiements.EC_Montant
    END AS [Reliquat]
    ,
    Paiements.Date_de_facture as [Date de paiement],
    Factures.EC_Pointage as [facture pointage],Paiements.EC_Pointage as [paiement pointage],
    Factures.Mois_de_livraison as [Mois de livraison],
    Commentaire as [Condition de paiement en jrs],
    CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as [Délai de paiement en jrs],
    FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as [Date d'échéance], 
    CASE 
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
           EC_Sens, EC_RefPiece, EC_Lettrage, EC_Montant,EC_Intitule,
           DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_facture,
           CONVERT(INT, CT_Commentaire) as Commentaire, EC_Pointage
    FROM dbo.F_ECRITUREC as e 
    JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
    WHERE (JO_Num IN ('AC') AND EC_Sens = 1 )
    AND e.CT_Num NOT LIKE '3%'
    AND e.CT_Num <> 'NULL'
    AND CONVERT(date, JM_Date) BETWEEN '{year_start}' AND '{start_date_minus1}'
) as Factures
LEFT JOIN (
    SELECT e.CT_Num as N_Fournisseur,
           FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') as Date_de_facture,
           DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison,
           EC_Lettrage, EC_Montant, 
           DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement,EC_Pointage
    FROM dbo.F_ECRITUREC as e
    JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
    WHERE (JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
    WHERE CG_Num like '5%')  
    OR (JO_num IN ('AC') AND EC_Sens = 0))
    AND e.CT_Num NOT LIKE '3%'
    AND e.CT_Num <> 'NULL'
    AND CONVERT(date, JM_Date) BETWEEN '{start_date}' AND '{end_date}'
) as Paiements
ON Factures.N_Fournisseur = Paiements.N_Fournisseur
AND ((Factures.EC_Lettrage IS NOT NULL AND Factures.EC_Lettrage <> '')  OR Factures.EC_Pointage IS NOT NULL AND Factures.EC_Pointage <> '') 
AND ((Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <> '')  OR Paiements.EC_Pointage IS NOT NULL AND Paiements.EC_Pointage <> '') 
AND (
    (LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
    )
    OR
    (Factures.EC_Lettrage IS NULL
    AND LTRIM(RTRIM(Factures.EC_Pointage)) = LTRIM(RTRIM(Paiements.EC_Pointage))
    AND Factures.EC_Pointage IS NOT NULL
    AND Paiements.EC_Pointage IS NOT NULL
    )
)
WHERE Paiements.Date_de_facture IS NOT NULL

UNION

-- Past invoices still unpaid
SELECT  CT_Intitule as Fournisseurs,Factures.EC_Intitule,
    EC_RefPiece as [N°Facture],
    Factures.EC_Montant as [Montant de Facture],
    Paiements.EC_Montant as montant_paiement,
    Factures.Date_de_facture as [Date de facture],

    CASE 
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN 'Non réglé' 
        WHEN Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <>''  THEN 'Totalement réglé' 
        WHEN Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '' AND (Paiements.EC_Pointage IS NOT NULL OR Paiements.EC_Pointage <>'' )  THEN 'Partiellement réglé'
    END AS [Statut de paiement]
    ,
    CASE
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN NULL
        WHEN Paiements.EC_Lettrage IS NOT NULL 
         AND Paiements.EC_Lettrage <> '' THEN NULL
        WHEN (Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '')
         AND Paiements.EC_Pointage IS NOT NULL 
         AND Paiements.EC_Pointage <> '' THEN Factures.EC_Montant - Paiements.EC_Montant
    END AS [Reliquat]
    ,
    Paiements.Date_de_facture as [Date de paiement],
    Factures.EC_Pointage as [facture pointage],Paiements.EC_Pointage as [paiement pointage],
    Factures.Mois_de_livraison as [Mois de livraison],
    Commentaire as [Condition de paiement en jrs],
    CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as [Délai de paiement en jrs],
    FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as [Date d'échéance],
    CASE 
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
        EC_Sens, EC_RefPiece, EC_Lettrage, EC_Montant,EC_Intitule,
        DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_facture,
        CONVERT(INT, CT_Commentaire) as Commentaire, EC_Pointage
FROM dbo.F_ECRITUREC as e 
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE (JO_Num IN ('AC') AND EC_Sens = 1 )
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL'  
AND CONVERT(date, JM_Date) BETWEEN '{year_start}' AND '{start_date_minus1}'
) as Factures
LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison, EC_Montant,
        EC_Lettrage, DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement, EC_Pointage
FROM dbo.F_ECRITUREC as e
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE (JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX WHERE CG_Num like '5%') OR (JO_num IN ('AC') AND EC_Sens = 0))  
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL' 
AND CONVERT(date, JM_Date) BETWEEN '{year_start}' AND '{end_date}'
) as Paiements
ON Factures.N_Fournisseur = Paiements.N_Fournisseur
AND ((Factures.EC_Lettrage IS NOT NULL AND Factures.EC_Lettrage <> '')  OR Factures.EC_Pointage IS NOT NULL AND Factures.EC_Pointage <> '') 
AND ((Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <> '')  OR Paiements.EC_Pointage IS NOT NULL AND Paiements.EC_Pointage <> '') 
AND (
    (LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
    )
    OR
    (Factures.EC_Lettrage IS NULL
    AND LTRIM(RTRIM(Factures.EC_Pointage)) = LTRIM(RTRIM(Paiements.EC_Pointage))
    AND Factures.EC_Pointage IS NOT NULL
    AND Paiements.EC_Pointage IS NOT NULL
    )
)
WHERE Paiements.Date_de_facture IS NULL

UNION

-- PAID RN in choosen trimester
SELECT  CT_Intitule as Fournisseurs,Factures.EC_Intitule,
    EC_RefPiece as [N°Facture],
    Factures.EC_Montant as [Montant de Facture],
    Paiements.EC_Montant as montant_paiement,
    Factures.Date_de_facture as [Date de facture],

    CASE 
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN 'Non réglé' 
        WHEN Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <>''  THEN 'Totalement réglé' 
        WHEN Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '' AND (Paiements.EC_Pointage IS NOT NULL OR Paiements.EC_Pointage <>'' )  THEN 'Partiellement réglé'
    END AS [Statut de paiement]
    ,
    CASE
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN NULL
        WHEN Paiements.EC_Lettrage IS NOT NULL 
         AND Paiements.EC_Lettrage <> '' THEN NULL
        WHEN (Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '')
         AND Paiements.EC_Pointage IS NOT NULL 
         AND Paiements.EC_Pointage <> '' THEN Factures.EC_Montant - Paiements.EC_Montant
    END AS [Reliquat]
    ,
    Paiements.Date_de_facture as [Date de paiement],
    Factures.EC_Pointage as [facture pointage],Paiements.EC_Pointage as [paiement pointage],
    Factures.Mois_de_livraison as [Mois de livraison],
    Commentaire as [Condition de paiement en jrs],
    CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as [Délai de paiement en jrs],
    FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as [Date d'échéance],
    CASE 
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
       EC_Sens, AC.EC_RefPiece, RN.EC_Lettrage, EC_Montant,EC_Intitule,
       DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, AC.JM_Date)) as jour_facture,
       CONVERT(INT, CT_Commentaire) as Commentaire, EC_Pointage
FROM dbo.F_ECRITUREC as AC
JOIN dbo.F_COMPTET as c on c.CT_Num = AC.CT_Num
JOIN (
    SELECT CT_Num, EC_RefPiece, EC_Lettrage
    FROM dbo.F_ECRITUREC
    WHERE JO_Num = 'RN'
    AND CONVERT(date, JM_Date) = '{year_start}'
    AND CT_Num <> 'NULL'
    AND CT_Num NOT LIKE '3%'
    AND EC_RefPiece <> ''
) as RN ON AC.CT_Num = RN.CT_Num AND AC.EC_RefPiece = RN.EC_RefPiece
WHERE (JO_Num IN ('AC') AND EC_Sens = 1 )
AND AC.CT_Num NOT LIKE '3%'
AND AC.CT_Num <> 'NULL'
AND CONVERT(date, AC.JM_Date) > CONVERT(date , (select TOP 1 D_commentaire FROm dbo.P_DOSSIER))
) as Factures
LEFT JOIN (
    SELECT e.CT_Num as N_Fournisseur,
           FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd') as Date_de_facture,
           DATENAME(month, DATEADD(day, EC_Jour - 1, JM_Date)) + '-' + CAST(YEAR(DATEADD(day, EC_Jour - 1, JM_Date)) AS VARCHAR) as Mois_de_livraison,
           EC_Lettrage, EC_Montant, 
           DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement, EC_Pointage
    FROM dbo.F_ECRITUREC as e
    JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
    WHERE (JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX
    WHERE CG_Num like '5%')  
    OR (JO_num IN ('AC') AND EC_Sens = 0)) 
    AND e.CT_Num NOT LIKE '3%'
    AND e.CT_Num <> 'NULL'
    AND CONVERT(date, JM_Date) BETWEEN '{start_date}' AND '{end_date}'
) as Paiements
ON Factures.N_Fournisseur = Paiements.N_Fournisseur
AND ((Factures.EC_Lettrage IS NOT NULL AND Factures.EC_Lettrage <> '')  OR Factures.EC_Pointage IS NOT NULL AND Factures.EC_Pointage <> '') 
AND ((Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <> '')  OR Paiements.EC_Pointage IS NOT NULL AND Paiements.EC_Pointage <> '') 
AND (
    (LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
    )
    OR
    (Factures.EC_Lettrage IS NULL
    AND LTRIM(RTRIM(Factures.EC_Pointage)) = LTRIM(RTRIM(Paiements.EC_Pointage))
    AND Factures.EC_Pointage IS NOT NULL
    AND Paiements.EC_Pointage IS NOT NULL
    )
)
WHERE Paiements.Date_de_facture IS NOT NULL

UNION

-- RN still unpaid
SELECT  CT_Intitule as Fournisseurs,Factures.EC_Intitule,
    EC_RefPiece as [N°Facture],
    Factures.EC_Montant as [Montant de Facture],
    Paiements.EC_Montant as montant_paiement,
    Factures.Date_de_facture as [Date de facture],

    CASE 
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN 'Non réglé' 
        WHEN Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <>''  THEN 'Totalement réglé' 
        WHEN Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '' AND (Paiements.EC_Pointage IS NOT NULL OR Paiements.EC_Pointage <>'' )  THEN 'Partiellement réglé'
    END AS [Statut de paiement]
    ,
    CASE
        WHEN Paiements.EC_Lettrage IS NULL AND Paiements.EC_Pointage IS NULL THEN NULL
        WHEN Paiements.EC_Lettrage IS NOT NULL 
         AND Paiements.EC_Lettrage <> '' THEN NULL
        WHEN (Paiements.EC_Lettrage IS NULL OR Paiements.EC_Lettrage = '')
         AND Paiements.EC_Pointage IS NOT NULL 
         AND Paiements.EC_Pointage <> '' THEN Factures.EC_Montant - Paiements.EC_Montant
    END AS [Reliquat]
    ,
    Paiements.Date_de_facture as [Date de paiement],
    Factures.EC_Pointage as [facture pointage],Paiements.EC_Pointage as [paiement pointage],
    Factures.Mois_de_livraison as [Mois de livraison],
    Commentaire as [Condition de paiement en jrs],
    CASE WHEN jour_paiement - jour_facture < 0 then 'En Avance' Else CAST(jour_paiement - jour_facture as varchar) END as [Délai de paiement en jrs],
    FORMAT(DATEADD(day, Commentaire, CAST(Factures.Date_de_facture AS DATE)), 'yyyy/MM/dd') as [Date d'échéance],
    CASE 
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
       EC_Sens, AC.EC_RefPiece, RN.EC_Lettrage, EC_Montant,EC_Intitule,
       DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, AC.JM_Date)) as jour_facture,
       CONVERT(INT, CT_Commentaire) as Commentaire, EC_Pointage
FROM dbo.F_ECRITUREC as AC
JOIN dbo.F_COMPTET as c on c.CT_Num = AC.CT_Num
JOIN (
    SELECT CT_Num, EC_RefPiece, EC_Lettrage
    FROM dbo.F_ECRITUREC
    WHERE JO_Num = 'RN'
    AND CONVERT(date, JM_Date) = '{year_start}'
    AND CT_Num <> 'NULL'
    AND CT_Num NOT LIKE '3%'
    AND EC_RefPiece <> ''
) as RN ON AC.CT_Num = RN.CT_Num AND AC.EC_RefPiece = RN.EC_RefPiece
WHERE (JO_Num IN ('AC') AND EC_Sens = 1 )
AND AC.CT_Num NOT LIKE '3%'
AND AC.CT_Num <> 'NULL'
AND CONVERT(date, AC.JM_Date) > CONVERT(date, (select TOP 1 D_commentaire FROm dbo.P_DOSSIER))
) as Factures 
LEFT JOIN (SELECT e.CT_Num as N_Fournisseur,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'yyyy/MM/dd')as Date_de_facture,
       FORMAT(DATEADD(day, EC_Jour - 1, JM_Date), 'MM-yyyy')as Mois_de_livraison, EC_Montant,
        EC_Lettrage, DATEDIFF(day, '1900-01-01', DATEADD(day, EC_Jour - 1, JM_Date)) as jour_paiement, EC_Pointage
FROM dbo.F_ECRITUREC as e
JOIN dbo.F_COMPTET as c on c.CT_Num = e.CT_Num
WHERE (JO_Num IN (SELECT JO_Num FROM dbo.F_JOURNAUX WHERE CG_Num like '5%') OR (JO_num IN ('AC') AND EC_Sens = 0))  
AND e.CT_Num NOT LIKE '3%'
AND e.CT_Num <> 'NULL' 
AND CONVERT(date, JM_Date) BETWEEN '{year_start}' AND '{end_date}' ) as Paiements
ON Factures.N_Fournisseur = Paiements.N_Fournisseur
AND ((Factures.EC_Lettrage IS NOT NULL AND Factures.EC_Lettrage <> '')  OR Factures.EC_Pointage IS NOT NULL AND Factures.EC_Pointage <> '') 
AND ((Paiements.EC_Lettrage IS NOT NULL AND Paiements.EC_Lettrage <> '')  OR Paiements.EC_Pointage IS NOT NULL AND Paiements.EC_Pointage <> '') 
AND (
    (LTRIM(RTRIM(Factures.EC_Lettrage)) = LTRIM(RTRIM(Paiements.EC_Lettrage))
    )
    OR
    (Factures.EC_Lettrage IS NULL
    AND LTRIM(RTRIM(Factures.EC_Pointage)) = LTRIM(RTRIM(Paiements.EC_Pointage))
    AND Factures.EC_Pointage IS NOT NULL
    AND Paiements.EC_Pointage IS NOT NULL
    )
)
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