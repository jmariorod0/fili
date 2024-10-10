# consultas_reporte_observaciones.py

consultas_reporte_2_mtj = [


  
  """

    ----------------- 18.1 Area de Levantamiento en Base de datos coincide con area MTJ

    SELECT 
        COALESCE(pd.qr_operacion, mtj.id_operacion) AS qr_operacion,
        pd.qr_operacion as "QR_MATRIZ (CODIGO_NIVEL) BD",
        ccp.ilicode as "CONDICION_PREDIO BD",
        pd.qr_operacion_definitivo AS "QR_DERIVADO (ID_OPERACION) BD" ,

        ROUND((ST_Area(ST_Transform(te.geometria, 9377))::numeric), 2) as "ÁREA LEVANTAMIENTO (m2) BD",
        mtj.local_id as "QR_MATRIZ (CODIGO_NIVEL) MTJ",
        mtj.id_operacion AS "QR_DERIVADO (ID_OPERACION) MTJ",
        mtj.condicion_predio as "CONDICION PREDIO MTJ",
        
            ((REPLACE(mtj.area_terreno_levantamiento, ',', '.'))::numeric) as "ÁREA LEVANTAMIENTO (m2) MTJ",
        CASE 
            WHEN  ((REPLACE(mtj.area_terreno_levantamiento, ',', '.'))::numeric)=  ROUND((ST_Area(ST_Transform(te.geometria, 9377))::numeric), 2) then 'SI' ELSE 'NO' END AS "COINCIDE(SI/NO) AREA_LEV"
            
        ,ABS(ROUND((ST_Area(ST_Transform(te.geometria, 9377))::numeric), 2) - ((REPLACE(mtj.area_terreno_levantamiento, ',', '.'))::numeric)) as "DIFERENCIA_AREAS",
        CASE
            WHEN (ABS(((REPLACE(mtj.area_terreno_levantamiento, ',', '.'))::numeric) - ROUND((ST_Area(ST_Transform(te.geometria, 9377))::numeric), 2)) > 0.005) 
            OR  (ABS(((REPLACE(mtj.area_terreno_levantamiento, ',', '.'))::numeric) - ROUND((ST_Area(ST_Transform(te.geometria, 9377))::numeric), 2)) > 0.005) IS NULL THEN 'AJUSTAR' ELSE 'OK' END AS "VALIDACION"
        ,CASE
            WHEN pd.qr_operacion_definitivo IS NULL THEN 'Falta en cca_predio'
            WHEN mtj.id_operacion IS NULL THEN 'Falta en matriz_mtj'
            ELSE NULL
        END AS "OBS"
    FROM 
        {esquema}.cca_predio pd
    JOIN {esquema}.cca_condicionprediotipo ccp ON pd.condicion_predio = ccp.t_id  
    FULL OUTER JOIN 
        {esquema}.cca_terreno te ON pd.terreno = te.t_id
    FULL OUTER JOIN 
        mtj.matriz_mtj mtj ON pd.qr_operacion_definitivo = mtj.id_operacion
        
    WHERE 
        (ABS(((REPLACE(mtj.area_terreno_levantamiento, ',', '.'))::numeric) - ROUND((ST_Area(ST_Transform(te.geometria, 9377))::numeric), 2)) > 0.05)
        OR  (ABS(((REPLACE(mtj.area_terreno_levantamiento, ',', '.'))::numeric) - ROUND((ST_Area(ST_Transform(te.geometria, 9377))::numeric), 2)) > 0.05) IS NULL



    """,
    
    
    """
    
    ----18.2	Area  y numero de construcciones coincide Base de Datos  MTJ

	WITH bd_data AS (
			SELECT 
				cp.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD", 
				cp.qr_operacion_definitivo AS "QR_DERIVADO (ID_OPERACION) BD", 
				ccp.ilicode AS "CONDICION_PREDIO_BD",
				CASE 
					WHEN EXISTS (SELECT 1 FROM {esquema}.cca_caracteristicasunidadconstruccion cc WHERE cc.predio = cp.t_id) THEN 'SI' 
					ELSE 'NO'
				END AS "¿TIENE CONSTRUCCIONES? BD", 
				(SELECT count(*) FROM {esquema}.cca_caracteristicasunidadconstruccion cc WHERE cc.predio = cp.t_id) AS "¿CANTIDAD CONSTRUCCIONES? BD",
				(SELECT ROUND(SUM(ST_Area(ST_Transform(cu.geometria, 9377))::numeric), 2)
				FROM {esquema}.cca_unidadconstruccion cu 
				JOIN {esquema}.cca_caracteristicasunidadconstruccion cca ON cca.t_id = cu.caracteristicasunidadconstruccion 
				WHERE cca.predio = cp.t_id
				) AS "ÁREA TOTAL CONSTRUIDA (m2) BD"	
			FROM {esquema}.cca_predio cp 
			JOIN {esquema}.cca_terreno ct ON cp.terreno = ct.t_id 
			JOIN {esquema}.cca_derecho cd ON cp.t_id = cd.predio 
			JOIN {esquema}.cca_derechotipo cdt ON cd.tipo = cdt.t_id 
			JOIN {esquema}.cca_condicionprediotipo ccp ON cp.condicion_predio = ccp.t_id 
			JOIN {esquema}.cca_fuenteadministrativa cfa ON cd.t_id = cfa.derecho 
			JOIN {esquema}.cca_fuenteadministrativatipo cfat ON cfa.tipo = cfat.t_id 
			JOIN {esquema}.cca_destinacioneconomicatipo cdet ON cp.destinacion_economica = cdet.t_id 
			GROUP BY 
				cp.qr_operacion, cp.qr_operacion_definitivo, ccp.ilicode, cp.t_id, ct.geometria
	),
	mtj_data AS (
			SELECT 
				local_id AS "QR_MATRIZ (CODIGO_NIVEL) MTJ", 
				id_operacion AS "QR_DERIVADO (ID_OPERACION) MTJ", 
				condicion_predio AS "CONDICION_PREDIO_MTJ", 
				tiene_construcciones AS "¿TIENE CONSTRUCCIONES? MTJ", 
				cons_cantidad AS "¿CANTIDAD CONSTRUCCIONES? MTJ",
				CASE 
					WHEN TRIM(cons_area) = '' THEN '0'
					ELSE REPLACE(cons_area, ',', '.') 
				END AS "ÁREA TOTAL CONSTRUIDA (m2) MTJ"
			FROM mtj.matriz_mtj
	)
	SELECT *
	FROM (
		SELECT 
			bd."QR_MATRIZ (CODIGO_NIVEL) BD",
			bd."QR_DERIVADO (ID_OPERACION) BD",
			bd."CONDICION_PREDIO_BD",
			bd."¿TIENE CONSTRUCCIONES? BD",
			bd."¿CANTIDAD CONSTRUCCIONES? BD",
			bd."ÁREA TOTAL CONSTRUIDA (m2) BD",
			mtj."QR_MATRIZ (CODIGO_NIVEL) MTJ",
			mtj."QR_DERIVADO (ID_OPERACION) MTJ",
			mtj."CONDICION_PREDIO_MTJ",  
			mtj."¿TIENE CONSTRUCCIONES? MTJ",
			mtj."¿CANTIDAD CONSTRUCCIONES? MTJ",
			mtj."ÁREA TOTAL CONSTRUIDA (m2) MTJ",
			CASE 
				WHEN bd."¿TIENE CONSTRUCCIONES? BD" = mtj."¿TIENE CONSTRUCCIONES? MTJ" THEN 'SI' 
				WHEN bd."¿TIENE CONSTRUCCIONES? BD" IS NULL OR mtj."¿TIENE CONSTRUCCIONES? MTJ" IS NULL THEN 'FALTAN DATOS'
				ELSE 'NO' 
			END AS "COINCIDE(SI/NO) TIENE_CONS",
			CASE 
				WHEN (bd."¿CANTIDAD CONSTRUCCIONES? BD"::TEXT = mtj."¿CANTIDAD CONSTRUCCIONES? MTJ"::TEXT) OR  (bd."¿CANTIDAD CONSTRUCCIONES? BD"=0 AND mtj."¿CANTIDAD CONSTRUCCIONES? MTJ" IS NULL)  THEN 'SI'
				WHEN bd."¿CANTIDAD CONSTRUCCIONES? BD" IS NULL OR mtj."¿CANTIDAD CONSTRUCCIONES? MTJ" IS NULL THEN 'FALTAN DATOS'
				ELSE 'NO' 
			END AS "COINCIDE(SI/NO) CANTIDAD_CONS",     
			CASE 
				WHEN (bd."ÁREA TOTAL CONSTRUIDA (m2) BD"::numeric = COALESCE(NULLIF(REGEXP_REPLACE(REPLACE(mtj."ÁREA TOTAL CONSTRUIDA (m2) MTJ", ',', '.'), '[^0-9.]', '', 'g'), '')::numeric, 0))
				OR (bd."ÁREA TOTAL CONSTRUIDA (m2) BD" IS NULL AND mtj."ÁREA TOTAL CONSTRUIDA (m2) MTJ" IS NULL)
				OR (bd."ÁREA TOTAL CONSTRUIDA (m2) BD" IS NULL AND (CAST(mtj."ÁREA TOTAL CONSTRUIDA (m2) MTJ" AS numeric) IN (0, 0.0, 0.000, 0.00))) 
				THEN 'SI' 
				ELSE 'NO' 
			END AS "COINCIDE(SI/NO) AREA_CONSTRUIDA (m2)",
			ABS(bd."ÁREA TOTAL CONSTRUIDA (m2) BD"::numeric - COALESCE(NULLIF(REGEXP_REPLACE(REPLACE(mtj."ÁREA TOTAL CONSTRUIDA (m2) MTJ", ',', '.'), '[^0-9.]', '', 'g'), '')::numeric, 0)) AS "DIFERENCIA AREAS"


		FROM bd_data bd
		FULL OUTER JOIN mtj_data mtj 
		ON bd."QR_DERIVADO (ID_OPERACION) BD" = mtj."QR_DERIVADO (ID_OPERACION) MTJ"
	) AS subquery
	WHERE 
		"COINCIDE(SI/NO) TIENE_CONS" <> 'SI' 
		OR "COINCIDE(SI/NO) CANTIDAD_CONS" <> 'SI' 
		OR "COINCIDE(SI/NO) AREA_CONSTRUIDA (m2)" <> 'SI'
 






	
    """,
    """
    ---- 19.1 - Coindicencia Tipo Fuente administrativa  Base de Datos - MTJ


	WITH bd_data AS (
		SELECT 
			cp.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD", 
			cp.qr_operacion_definitivo AS "QR_DERIVADO (ID_OPERACION) BD",
			cfa.t_id as "T_ID CCA_FUENTEADM BD",
			ccp.ilicode AS "CONDICION_PREDIO_BD", 
			cfat.ilicode as "TIPO FUENTE ADMINISTRATIVA BD",
			cfat.t_id as "T_ID_TIPO_FUENTE BD",
			cfa.ente_emisor as "ENTE EMISOR FUENTE ADMINISTRATIVA BD", 
			cfa.numero_fuente as "NÚMERO FUENTE ADMINISTRATIVA BD", 
			TO_CHAR(cfa.fecha_documento_fuente, 'DD/MM/YYYY') AS "FECHA FUENTE ADMINISTRATIVA BD"
		FROM {esquema}.cca_predio cp 
		JOIN {esquema}.cca_terreno ct ON cp.terreno = ct.t_id 
		JOIN {esquema}.cca_derecho cd ON cp.t_id = cd.predio 
		JOIN {esquema}.cca_derechotipo cdt ON cd.tipo = cdt.t_id 
		JOIN {esquema}.cca_condicionprediotipo ccp ON cp.condicion_predio = ccp.t_id 
		JOIN {esquema}.cca_fuenteadministrativa cfa ON cd.t_id = cfa.derecho 
		JOIN {esquema}.cca_fuenteadministrativatipo cfat ON cfa.tipo = cfat.t_id 
		JOIN {esquema}.cca_destinacioneconomicatipo cdet ON cp.destinacion_economica = cdet.t_id 
		GROUP BY 
			cp.qr_operacion, cp.qr_operacion_definitivo, ccp.ilicode, cp.t_id, ccp.ilicode, cfat.ilicode, 
			cfa.ente_emisor, cfa.numero_fuente, cfa.fecha_documento_fuente, cfa.t_id, cfat.t_id
	),
	mtj_data AS (
		SELECT 
			local_id AS "QR_MATRIZ (CODIGO_NIVEL) MTJ", 
			id_operacion AS "QR_DERIVADO (ID_OPERACION) MTJ", 
			condicion_predio AS "CONDICION_PREDIO_MTJ", 
			tipo_fuente_adm AS "TIPO FUENTE ADMINISTRATIVA MTJ",
			fmi_ente_emisor AS "ENTE EMISOR FUENTE ADMINISTRATIVA MTJ",
			numero_fuente_adm AS "NÚMERO FUENTE ADMINISTRATIVA MTJ",
			fmi_fecha_documento_fuente AS "FECHA FUENTE ADMINISTRATIVA MTJ",
			CASE
				WHEN tipo_fuente_adm = 'Sin_Documento' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Sin_Documento')
				WHEN tipo_fuente_adm = 'Documento_Publico.Escritura_Publica' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Escritura_Publica')
				WHEN tipo_fuente_adm = 'Documento_Privado' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Privado')
				WHEN tipo_fuente_adm = 'Documento_Publico.Sentencia_Judicial' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Sentencia_Judicial')
				WHEN tipo_fuente_adm = 'Documento_Publico.Acto_Administrativo' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Acto_Administrativo')
				ELSE NULL
			END AS "HOMOLOGACION_TIPO_FUENTE_MTJ"
		FROM mtj.matriz_mtj
	)
	SELECT *
	FROM (
		SELECT 
			bd."QR_MATRIZ (CODIGO_NIVEL) BD", 
			bd."QR_DERIVADO (ID_OPERACION) BD",
			bd."CONDICION_PREDIO_BD",
			bd."TIPO FUENTE ADMINISTRATIVA BD",
			mtj."QR_MATRIZ (CODIGO_NIVEL) MTJ",
			mtj."QR_DERIVADO (ID_OPERACION) MTJ", 	
			mtj."TIPO FUENTE ADMINISTRATIVA MTJ",
			CASE 
				WHEN bd."TIPO FUENTE ADMINISTRATIVA BD" = mtj."TIPO FUENTE ADMINISTRATIVA MTJ" THEN 'SI' 
				WHEN bd."TIPO FUENTE ADMINISTRATIVA BD" IS NULL OR mtj."TIPO FUENTE ADMINISTRATIVA MTJ" IS NULL THEN 'FALTAN DATOS Ó QR NO ENCONTRADO'
				ELSE 'NO' 
			END AS "COINCIDE(SI/NO) TIPO_FUENTE_ADM",
			bd."T_ID CCA_FUENTEADM BD",
			bd."T_ID_TIPO_FUENTE BD" as "T_ID DOMINIO TIPO FUENTE BD",
			CASE 
				WHEN mtj."HOMOLOGACION_TIPO_FUENTE_MTJ" IS NOT NULL AND bd."T_ID CCA_FUENTEADM BD" IS NOT NULL
				THEN 'UPDATE cambiar_esquema.cca_fuenteadministrativa SET tipo =' || mtj."HOMOLOGACION_TIPO_FUENTE_MTJ" || ' WHERE t_id =' || bd."T_ID CCA_FUENTEADM BD"
				ELSE NULL
			END AS "consulta_cambio_tipo_fuente"
		FROM bd_data bd
		FULL OUTER JOIN mtj_data mtj 
		ON bd."QR_DERIVADO (ID_OPERACION) BD" = mtj."QR_DERIVADO (ID_OPERACION) MTJ"
	) AS subquery
	WHERE 
		"COINCIDE(SI/NO) TIPO_FUENTE_ADM" <> 'SI' 



    """,
	
	"""
	--- 19.2 coincide	ente emisor coincide Base de Datos - MTJ


	WITH bd_data AS (
		SELECT 
			cp.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD", 
			cp.qr_operacion_definitivo AS "QR_DERIVADO (ID_OPERACION) BD",
			cfa.t_id as "T_ID CCA_FUENTEADM BD",
			ccp.ilicode AS "CONDICION_PREDIO_BD", 
			cfat.ilicode as "TIPO FUENTE ADMINISTRATIVA BD",
			cfat.t_id as "T_ID_TIPO_FUENTE BD",
			cfa.ente_emisor as "ENTE EMISOR FUENTE ADMINISTRATIVA BD", 
			cfa.numero_fuente as "NÚMERO FUENTE ADMINISTRATIVA BD", 
			TO_CHAR(cfa.fecha_documento_fuente, 'DD/MM/YYYY') AS "FECHA FUENTE ADMINISTRATIVA BD"
		FROM {esquema}.cca_predio cp 
		JOIN {esquema}.cca_terreno ct ON cp.terreno = ct.t_id 
		JOIN {esquema}.cca_derecho cd ON cp.t_id = cd.predio 
		JOIN {esquema}.cca_derechotipo cdt ON cd.tipo = cdt.t_id 
		JOIN {esquema}.cca_condicionprediotipo ccp ON cp.condicion_predio = ccp.t_id 
		JOIN {esquema}.cca_fuenteadministrativa cfa ON cd.t_id = cfa.derecho 
		JOIN {esquema}.cca_fuenteadministrativatipo cfat ON cfa.tipo = cfat.t_id 
		JOIN {esquema}.cca_destinacioneconomicatipo cdet ON cp.destinacion_economica = cdet.t_id 
		GROUP BY 
			cp.qr_operacion, cp.qr_operacion_definitivo, ccp.ilicode, cp.t_id, ccp.ilicode, cfat.ilicode, 
			cfa.ente_emisor, cfa.numero_fuente, cfa.fecha_documento_fuente, cfa.t_id, cfat.t_id
	),
	mtj_data AS (
		SELECT 
			local_id AS "QR_MATRIZ (CODIGO_NIVEL) MTJ", 
			id_operacion AS "QR_DERIVADO (ID_OPERACION) MTJ", 
			condicion_predio AS "CONDICION_PREDIO_MTJ", 
			tipo_fuente_adm AS "TIPO FUENTE ADMINISTRATIVA MTJ",
			fmi_ente_emisor AS "ENTE EMISOR FUENTE ADMINISTRATIVA MTJ",
			numero_fuente_adm AS "NÚMERO FUENTE ADMINISTRATIVA MTJ",
			fmi_fecha_documento_fuente AS "FECHA FUENTE ADMINISTRATIVA MTJ",
			CASE
				WHEN tipo_fuente_adm = 'Sin_Documento' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Sin_Documento')
				WHEN tipo_fuente_adm = 'Documento_Publico.Escritura_Publica' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Escritura_Publica')
				WHEN tipo_fuente_adm = 'Documento_Privado' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Privado')
				WHEN tipo_fuente_adm = 'Documento_Publico.Sentencia_Judicial' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Sentencia_Judicial')
				WHEN tipo_fuente_adm = 'Documento_Publico.Acto_Administrativo' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Acto_Administrativo')
				ELSE NULL
			END AS "HOMOLOGACION_TIPO_FUENTE_MTJ"
		FROM mtj.matriz_mtj
	)
	SELECT *
	FROM (
		SELECT 
			bd."QR_MATRIZ (CODIGO_NIVEL) BD", 
			bd."QR_DERIVADO (ID_OPERACION) BD",
			bd."CONDICION_PREDIO_BD",
			bd."TIPO FUENTE ADMINISTRATIVA BD",
			bd."ENTE EMISOR FUENTE ADMINISTRATIVA BD",
			mtj."QR_MATRIZ (CODIGO_NIVEL) MTJ",
			mtj."QR_DERIVADO (ID_OPERACION) MTJ",
			mtj."TIPO FUENTE ADMINISTRATIVA MTJ",
			mtj."ENTE EMISOR FUENTE ADMINISTRATIVA MTJ",
		
			CASE 
				WHEN LOWER(TRANSLATE(bd."ENTE EMISOR FUENTE ADMINISTRATIVA BD", 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou')) = 
					 LOWER(TRANSLATE(mtj."ENTE EMISOR FUENTE ADMINISTRATIVA MTJ", 'ÁÉÍÓÚáéíóú', 'AEIOUaeiou'))
				OR (bd."ENTE EMISOR FUENTE ADMINISTRATIVA BD" IS NULL AND mtj."ENTE EMISOR FUENTE ADMINISTRATIVA MTJ" IN ('NA','N/A','na','n/a','N/R',''))
				OR (bd."ENTE EMISOR FUENTE ADMINISTRATIVA BD" IN ('NA','N/A','na','n/a','N/R','') AND mtj."ENTE EMISOR FUENTE ADMINISTRATIVA MTJ" IS NULL)
				OR (bd."ENTE EMISOR FUENTE ADMINISTRATIVA BD" IN ('NA','N/A','na','n/a','N/R','') AND mtj."ENTE EMISOR FUENTE ADMINISTRATIVA MTJ" IN ('NA','N/A','na','n/a','N/R',''))
				OR (bd."ENTE EMISOR FUENTE ADMINISTRATIVA BD" IS NULL AND mtj."ENTE EMISOR FUENTE ADMINISTRATIVA MTJ" IS NULL) THEN 'SI' 
				ELSE 'NO' 
			END AS "COINCIDE(SI/NO) ENTE_EMISOR_FUENTE_ADM"

		
		FROM bd_data bd
		FULL OUTER JOIN mtj_data mtj 
		ON bd."QR_DERIVADO (ID_OPERACION) BD" = mtj."QR_DERIVADO (ID_OPERACION) MTJ"
	) AS subquery
	WHERE  "COINCIDE(SI/NO) ENTE_EMISOR_FUENTE_ADM" <> 'SI' ;




	
	""",
	
	"""
	-- 14.3 - Coindicencia del Número de Fuente de documento de la Fuente administrativa entre Base de Datos - MTJ


	WITH bd_data AS (
		SELECT 
			cp.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD", 
			cp.qr_operacion_definitivo AS "QR_DERIVADO (ID_OPERACION) BD",
			cfa.t_id as "T_ID CCA_FUENTEADM BD",
			ccp.ilicode AS "CONDICION_PREDIO_BD", 
			cfat.ilicode as "TIPO FUENTE ADMINISTRATIVA BD",
			cfat.t_id as "T_ID_TIPO_FUENTE BD",
			cfa.ente_emisor as "ENTE EMISOR FUENTE ADMINISTRATIVA BD", 
			cfa.numero_fuente as "NÚMERO FUENTE ADMINISTRATIVA BD", 
			TO_CHAR(cfa.fecha_documento_fuente, 'DD/MM/YYYY') AS "FECHA FUENTE ADMINISTRATIVA BD"
		FROM {esquema}.cca_predio cp 
		JOIN {esquema}.cca_terreno ct ON cp.terreno = ct.t_id 
		JOIN {esquema}.cca_derecho cd ON cp.t_id = cd.predio 
		JOIN {esquema}.cca_derechotipo cdt ON cd.tipo = cdt.t_id 
		JOIN {esquema}.cca_condicionprediotipo ccp ON cp.condicion_predio = ccp.t_id 
		JOIN {esquema}.cca_fuenteadministrativa cfa ON cd.t_id = cfa.derecho 
		JOIN {esquema}.cca_fuenteadministrativatipo cfat ON cfa.tipo = cfat.t_id 
		JOIN {esquema}.cca_destinacioneconomicatipo cdet ON cp.destinacion_economica = cdet.t_id 
		GROUP BY 
			cp.qr_operacion, cp.qr_operacion_definitivo, ccp.ilicode, cp.t_id, ccp.ilicode, cfat.ilicode, 
			cfa.ente_emisor, cfa.numero_fuente, cfa.fecha_documento_fuente, cfa.t_id, cfat.t_id
	),
	mtj_data AS (
		SELECT 
			local_id AS "QR_MATRIZ (CODIGO_NIVEL) MTJ", 
			id_operacion AS "QR_DERIVADO (ID_OPERACION) MTJ", 
			condicion_predio AS "CONDICION_PREDIO_MTJ", 
			tipo_fuente_adm AS "TIPO FUENTE ADMINISTRATIVA MTJ",
			fmi_ente_emisor AS "ENTE EMISOR FUENTE ADMINISTRATIVA MTJ",
			numero_fuente_adm AS "NÚMERO FUENTE ADMINISTRATIVA MTJ",
			fmi_fecha_documento_fuente AS "FECHA FUENTE ADMINISTRATIVA MTJ",
			CASE
				WHEN tipo_fuente_adm = 'Sin_Documento' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Sin_Documento')
				WHEN tipo_fuente_adm = 'Documento_Publico.Escritura_Publica' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Escritura_Publica')
				WHEN tipo_fuente_adm = 'Documento_Privado' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Privado')
				WHEN tipo_fuente_adm = 'Documento_Publico.Sentencia_Judicial' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Sentencia_Judicial')
				WHEN tipo_fuente_adm = 'Documento_Publico.Acto_Administrativo' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Acto_Administrativo')
				ELSE NULL
			END AS "HOMOLOGACION_TIPO_FUENTE_MTJ"
		FROM mtj.matriz_mtj
	)
	SELECT *
	FROM (
		SELECT 
			bd."QR_MATRIZ (CODIGO_NIVEL) BD", 
			bd."QR_DERIVADO (ID_OPERACION) BD",
			bd."CONDICION_PREDIO_BD",
			bd."TIPO FUENTE ADMINISTRATIVA BD",
			bd."NÚMERO FUENTE ADMINISTRATIVA BD",
			mtj."QR_MATRIZ (CODIGO_NIVEL) MTJ",
			mtj."QR_DERIVADO (ID_OPERACION) MTJ",
			mtj."TIPO FUENTE ADMINISTRATIVA MTJ",
			mtj."NÚMERO FUENTE ADMINISTRATIVA MTJ",		

	
			CASE 
				WHEN bd."NÚMERO FUENTE ADMINISTRATIVA BD"= mtj."NÚMERO FUENTE ADMINISTRATIVA MTJ" 
				OR (bd."NÚMERO FUENTE ADMINISTRATIVA BD" IS NULL AND mtj."NÚMERO FUENTE ADMINISTRATIVA MTJ" IN ('NA','N/A','N/R','na','n/a',''))
				OR (bd."NÚMERO FUENTE ADMINISTRATIVA BD" IN ('NA','N/A','N/R','na','n/a','') AND mtj."NÚMERO FUENTE ADMINISTRATIVA MTJ" IS NULL)
				OR (bd."NÚMERO FUENTE ADMINISTRATIVA BD" IS NULL AND mtj."NÚMERO FUENTE ADMINISTRATIVA MTJ" IS NULL)
				THEN 'SI' 
				ELSE 'NO' 
			END AS "COINCIDE(SI/NO) NUMERO_FUENTE_ADM"
		
		
		FROM bd_data bd
		FULL OUTER JOIN mtj_data mtj 
		ON bd."QR_DERIVADO (ID_OPERACION) BD" = mtj."QR_DERIVADO (ID_OPERACION) MTJ"
	) AS subquery
	WHERE  "COINCIDE(SI/NO) NUMERO_FUENTE_ADM" <> 'SI';



	
	""",
	
	"""
	
	---14.4 - Coindicencia de la Fecha del documento de la Fuente administrativa entre Base de Datos - MTJ


	WITH bd_data AS (
		SELECT 
			cp.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD", 
			cp.qr_operacion_definitivo AS "QR_DERIVADO (ID_OPERACION) BD",
			cfa.t_id as "T_ID CCA_FUENTEADM BD",
			ccp.ilicode AS "CONDICION_PREDIO_BD", 
			cfat.ilicode as "TIPO FUENTE ADMINISTRATIVA BD",
			cfat.t_id as "T_ID_TIPO_FUENTE BD",
			cfa.ente_emisor as "ENTE EMISOR FUENTE ADMINISTRATIVA BD", 
			cfa.numero_fuente as "NÚMERO FUENTE ADMINISTRATIVA BD", 
			TO_CHAR(cfa.fecha_documento_fuente, 'DD/MM/YYYY') AS "FECHA FUENTE ADMINISTRATIVA BD"
		FROM {esquema}.cca_predio cp 
		JOIN {esquema}.cca_terreno ct ON cp.terreno = ct.t_id 
		JOIN {esquema}.cca_derecho cd ON cp.t_id = cd.predio 
		JOIN {esquema}.cca_derechotipo cdt ON cd.tipo = cdt.t_id 
		JOIN {esquema}.cca_condicionprediotipo ccp ON cp.condicion_predio = ccp.t_id 
		JOIN {esquema}.cca_fuenteadministrativa cfa ON cd.t_id = cfa.derecho 
		JOIN {esquema}.cca_fuenteadministrativatipo cfat ON cfa.tipo = cfat.t_id 
		JOIN {esquema}.cca_destinacioneconomicatipo cdet ON cp.destinacion_economica = cdet.t_id 
		GROUP BY 
			cp.qr_operacion, cp.qr_operacion_definitivo, ccp.ilicode, cp.t_id, ccp.ilicode, cfat.ilicode, 
			cfa.ente_emisor, cfa.numero_fuente, cfa.fecha_documento_fuente, cfa.t_id, cfat.t_id
	),
	mtj_data AS (
		SELECT 
			local_id AS "QR_MATRIZ (CODIGO_NIVEL) MTJ", 
			id_operacion AS "QR_DERIVADO (ID_OPERACION) MTJ", 
			condicion_predio AS "CONDICION_PREDIO_MTJ", 
			tipo_fuente_adm AS "TIPO FUENTE ADMINISTRATIVA MTJ",
			fmi_ente_emisor AS "ENTE EMISOR FUENTE ADMINISTRATIVA MTJ",
			numero_fuente_adm AS "NÚMERO FUENTE ADMINISTRATIVA MTJ",
			fmi_fecha_documento_fuente AS "FECHA FUENTE ADMINISTRATIVA MTJ",
			CASE
				WHEN tipo_fuente_adm = 'Sin_Documento' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Sin_Documento')
				WHEN tipo_fuente_adm = 'Documento_Publico.Escritura_Publica' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Escritura_Publica')
				WHEN tipo_fuente_adm = 'Documento_Privado' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Privado')
				WHEN tipo_fuente_adm = 'Documento_Publico.Sentencia_Judicial' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Sentencia_Judicial')
				WHEN tipo_fuente_adm = 'Documento_Publico.Acto_Administrativo' THEN (SELECT t_id FROM {esquema}.cca_fuenteadministrativatipo WHERE ilicode = 'Documento_Publico.Acto_Administrativo')
				ELSE NULL
			END AS "HOMOLOGACION_TIPO_FUENTE_MTJ"
		FROM mtj.matriz_mtj
	)
	SELECT *
	FROM (
		SELECT 
			bd."QR_MATRIZ (CODIGO_NIVEL) BD", 
			bd."QR_DERIVADO (ID_OPERACION) BD",
			bd."CONDICION_PREDIO_BD",
			bd."TIPO FUENTE ADMINISTRATIVA BD",
			bd."FECHA FUENTE ADMINISTRATIVA BD",
			mtj."QR_MATRIZ (CODIGO_NIVEL) MTJ",
			mtj."QR_DERIVADO (ID_OPERACION) MTJ", 	
			mtj."TIPO FUENTE ADMINISTRATIVA MTJ",
			mtj."FECHA FUENTE ADMINISTRATIVA MTJ",
			CASE
				WHEN (mtj."FECHA FUENTE ADMINISTRATIVA MTJ" IS NULL AND bd."FECHA FUENTE ADMINISTRATIVA BD" IS NULL)
					 OR (mtj."FECHA FUENTE ADMINISTRATIVA MTJ" = '' AND bd."FECHA FUENTE ADMINISTRATIVA BD" = '') THEN 'SI'
				WHEN LENGTH(mtj."FECHA FUENTE ADMINISTRATIVA MTJ") = 10 AND LENGTH(bd."FECHA FUENTE ADMINISTRATIVA BD") = 10 THEN 
					CASE 
						WHEN TO_CHAR(TO_DATE(mtj."FECHA FUENTE ADMINISTRATIVA MTJ", 'DD/MM/YYYY'), 'DD/MM/YYYY') = TO_CHAR(TO_DATE(bd."FECHA FUENTE ADMINISTRATIVA BD", 'DD/MM/YYYY'), 'DD/MM/YYYY') THEN 'SI'
						ELSE 'NO'
					END
				WHEN LENGTH(mtj."FECHA FUENTE ADMINISTRATIVA MTJ") = 10 THEN 
					CASE 
						WHEN TO_CHAR(TO_DATE(mtj."FECHA FUENTE ADMINISTRATIVA MTJ", 'DD/MM/YYYY'), 'DD/MM/YYYY') = bd."FECHA FUENTE ADMINISTRATIVA BD" THEN 'SI'
						ELSE 'NO'
					END
				WHEN LENGTH(bd."FECHA FUENTE ADMINISTRATIVA BD") = 10 THEN 
					CASE 
						WHEN TO_CHAR(TO_DATE(bd."FECHA FUENTE ADMINISTRATIVA BD", 'DD/MM/YYYY'), 'DD/MM/YYYY') = mtj."FECHA FUENTE ADMINISTRATIVA MTJ" THEN 'SI'
						ELSE 'NO'
					END
				ELSE 
					CASE 
						WHEN mtj."FECHA FUENTE ADMINISTRATIVA MTJ" = bd."FECHA FUENTE ADMINISTRATIVA BD" THEN 'SI'
						ELSE 'NO'
					END
			END AS "COINCIDE(SI/NO) FECHA_FUENTE_ADM"

		FROM bd_data bd
		FULL OUTER JOIN mtj_data mtj 
		ON bd."QR_DERIVADO (ID_OPERACION) BD" = mtj."QR_DERIVADO (ID_OPERACION) MTJ"
	) AS subquery
	WHERE "COINCIDE(SI/NO) FECHA_FUENTE_ADM" <> 'SI';

	""",
	
    """
    ---  15.1 - Cantidad de formales según columna BP(formal_informal) coincide MTJ - Base de Datos (Dominios)

	WITH condicion_predio_count AS (
		SELECT 
			drtp.ilicode AS derecho_predio, 
			COUNT(*) AS total_count
		FROM 
			{esquema}.cca_predio pd
		JOIN 
			{esquema}.cca_condicionprediotipo cpt 
			ON pd.condicion_predio = cpt.t_id
		JOIN 
			{esquema}.cca_derecho der 
			ON pd.t_id = der.predio
		JOIN 
			{esquema}.cca_derechotipo drtp 
			ON der.tipo = drtp.t_id
		WHERE 
			drtp.ilicode = 'Dominio'
		GROUP BY  
			drtp.ilicode
	),
	formal_informal_count AS (
		SELECT 
			'Total Formal' AS formal_informal, 
			SUM(total) AS total_count
		FROM (
			SELECT 
				formal_informal, 
				COUNT(*) AS total
			FROM 
				mtj.matriz_mtj
			WHERE 
				formal_informal IN ('Formal', 'Formal-sin remanente', 'Formal-con remanente')
			GROUP BY 
				formal_informal
		) sub
	),
	default_condicion_predio AS (
		SELECT 0 AS total_count
	)
	SELECT 
		COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) AS formales_BD,
		formal_informal_count.total_count AS formales_MTJ,
		CASE 
			WHEN COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) = formal_informal_count.total_count THEN 'COINCIDE'
			ELSE 'INCONSISTENCIA'
		END AS comparacion
	FROM 
		formal_informal_count
	LEFT JOIN 
		condicion_predio_count ON TRUE
	LEFT JOIN
		default_condicion_predio ON condicion_predio_count.total_count IS NULL
	WHERE 
		CASE 
			WHEN COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) = formal_informal_count.total_count THEN 'COINCIDE'
			ELSE 'INCONSISTENCIA'
		END = 'INCONSISTENCIA';

    """,
    """

    ---  15.2 REPORTE DE LOS CASOS QUE DIFIEREN FORMALES DE MTJ Y BASE DE DATOS 
    
    WITH cca_predio_data AS (
        SELECT 
            pd.qr_operacion_definitivo,
            CASE
                WHEN drtp.ilicode = 'Dominio' THEN 'Formal' ELSE 'Informal' 
            END AS formal_informal_bd
        FROM 
            {esquema}.cca_predio pd
        JOIN 
            {esquema}.cca_condicionprediotipo cpt 
            ON pd.condicion_predio = cpt.t_id
				JOIN 
			{esquema}.cca_derecho der 
			ON pd.t_id = der.predio
		JOIN 
			{esquema}.cca_derechotipo drtp 
			ON der.tipo = drtp.t_id
        WHERE 
            drtp.ilicode = 'Dominio'
    ),
    matriz_mtj_data AS (
        SELECT 
            id_operacion AS qr_operacion_definitivo,
            CASE 
                WHEN formal_informal IN ('Formal', 'Formal-sin remanente', 'Formal-con remanente') THEN 'Formal' ELSE 'Informal' 
            END AS formal_informal_mtj
        FROM  
            mtj.matriz_mtj
        WHERE 
            formal_informal IN ('Formal', 'Formal-sin remanente', 'Formal-con remanente')
    )
    SELECT 
        COALESCE(cca_predio_data.qr_operacion_definitivo, matriz_mtj_data.qr_operacion_definitivo) AS "QR_DERIVADO (ID_OPERACION)",
        cca_predio_data.formal_informal_bd AS "PREDIO  (FORMAL INFORMAL) BD",
        matriz_mtj_data.formal_informal_mtj AS "PREDIO  (FORMAL INFORMAL) MTJ",
        CASE 
            WHEN cca_predio_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en cca_predio o mal catalogado'
            WHEN matriz_mtj_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en matriz_mtj o mal catalogado'
            WHEN cca_predio_data.formal_informal_bd = matriz_mtj_data.formal_informal_mtj THEN 'SI'
            ELSE 'INCONSISTENCIA'
        END AS "COINCIDE(SI/NO)"
    FROM 
        cca_predio_data
    FULL OUTER JOIN 
        matriz_mtj_data 
        ON cca_predio_data.qr_operacion_definitivo = matriz_mtj_data.qr_operacion_definitivo

		WHERE 
			CASE 
				WHEN cca_predio_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en cca_predio o mal catalogado'
				WHEN matriz_mtj_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en matriz_mtj o mal catalogado'
				WHEN cca_predio_data.formal_informal_bd = matriz_mtj_data.formal_informal_mtj THEN 'SI'
				ELSE 'INCONSISTENCIA'
			END <> 'SI';


    """,
    """
    ---15.3  cantidad de informales en la base de datos y MTJ

    WITH condicion_predio_count AS (
        SELECT 
            cpt.ilicode AS condicion_predio, 
            COUNT(*) AS total_count
        FROM 
            {esquema}.cca_predio pd
        JOIN 
            {esquema}.cca_condicionprediotipo cpt 
            ON pd.condicion_predio = cpt.t_id
        WHERE 
            cpt.ilicode = 'Informal'
        GROUP BY  
            cpt.ilicode
    ),
    formal_informal_count AS (
        SELECT 
            'Total Formal' AS formal_informal, 
            SUM(total) AS total_count
        FROM (
            SELECT 
                formal_informal, 
                COUNT(*) AS total
            FROM 
                mtj.matriz_mtj
            WHERE 
                formal_informal IN ('Informal')
            GROUP BY 
                formal_informal
        ) sub
    ),
    default_condicion_predio AS (
        SELECT 0 AS total_count
    )
    SELECT 
        COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) AS informales_BD,
        formal_informal_count.total_count AS informales_MTJ,
        CASE 
            WHEN COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) = formal_informal_count.total_count THEN 'COINCIDE'
            ELSE 'INCONSISTENCIA'
        END AS comparacion
    FROM 
        formal_informal_count
    LEFT JOIN 
        condicion_predio_count ON TRUE
    LEFT JOIN
        default_condicion_predio ON condicion_predio_count.total_count IS NULL
     WHERE
	 CASE 
            WHEN COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) = formal_informal_count.total_count THEN 'COINCIDE'
            ELSE 'INCONSISTENCIA'
	END ='INCONSISTENCIA';



    """,
    """

    ---15.4 REPORTE DE LOS CASOS QUE DIFIEREN INFORMALES DE MTJ Y BASE DE DATOS

    WITH cca_predio_data AS (
        SELECT 
            pd.qr_operacion_definitivo,
            CASE
                WHEN cpt.ilicode = 'Informal' THEN 'Informal' ELSE 'Formal' 
            END AS formal_informal_bd
        FROM 
            {esquema}.cca_predio pd
        JOIN 
            {esquema}.cca_condicionprediotipo cpt 
            ON pd.condicion_predio = cpt.t_id
        WHERE 
            cpt.ilicode = 'Informal'
    ),
    matriz_mtj_data AS (
        SELECT 
            id_operacion AS qr_operacion_definitivo,
            CASE 
                WHEN formal_informal IN ('Informal') THEN 'Informal' ELSE 'Formal' 
            END AS formal_informal_mtj
        FROM  
            mtj.matriz_mtj
        WHERE 
            formal_informal IN ('Informal')
    )
    SELECT 
        COALESCE(cca_predio_data.qr_operacion_definitivo, matriz_mtj_data.qr_operacion_definitivo) AS "QR_DERIVADO (ID_OPERACION)",
        cca_predio_data.formal_informal_bd as "PREDIO  (FORMAL INFORMAL) BD",
        matriz_mtj_data.formal_informal_mtj as "PREDIO  (FORMAL INFORMAL) MTJ",
        CASE 
            WHEN cca_predio_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en cca_predio o mal catalogado'
            WHEN matriz_mtj_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en matriz_mtj o mal catalogado'
            WHEN cca_predio_data.formal_informal_bd = matriz_mtj_data.formal_informal_mtj THEN 'SI'
            ELSE 'INCONSISTENCIA'
        END AS "COINCIDE(SI/NO)"
    FROM 
        cca_predio_data
    FULL OUTER JOIN 
        matriz_mtj_data 
        ON cca_predio_data.qr_operacion_definitivo = matriz_mtj_data.qr_operacion_definitivo
	WHERE 
        CASE 
            WHEN cca_predio_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en cca_predio o mal catalogado'
            WHEN matriz_mtj_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en matriz_mtj o mal catalogado'
            WHEN cca_predio_data.formal_informal_bd = matriz_mtj_data.formal_informal_mtj THEN 'SI'
            ELSE 'INCONSISTENCIA'
        END <> 'SI';

    
    """,
    """
    --- 15.5	cantidad de formales coincide  Base de Datos - MTJ (según columna BT de condicion del predio catalogados como NPH)
    
    WITH condicion_predio_count AS (
        SELECT 
            cpt.ilicode AS condicion_predio, 
            COUNT(*) AS total_count
        FROM 
            {esquema}.cca_predio pd
        JOIN 
            {esquema}.cca_condicionprediotipo cpt 
            ON pd.condicion_predio = cpt.t_id
        WHERE 
            cpt.ilicode = 'NPH'
        GROUP BY  
            cpt.ilicode
    ),
    formal_informal_count AS (
        SELECT 
            'Total Formal' AS formal_informal, 
            SUM(total) AS total_count
        FROM (
            SELECT 
                condicion_predio, 
                COUNT(*) AS total
            FROM 
                mtj.matriz_mtj
            WHERE 
                condicion_predio IN ('NPH')
            GROUP BY 
                condicion_predio
        ) sub
    ),
    default_condicion_predio AS (
        SELECT 0 AS total_count
    )
    SELECT 
        COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) AS NPH_BD,
        formal_informal_count.total_count AS NPH_MTJ,
        CASE 
            WHEN COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) = formal_informal_count.total_count THEN 'COINCIDE'
            ELSE 'INCONSISTENCIA'
        END AS comparacion
    FROM 
        formal_informal_count
    LEFT JOIN 
        condicion_predio_count ON TRUE
    LEFT JOIN
        default_condicion_predio ON condicion_predio_count.total_count IS NULL
	WHERE
        CASE 
            WHEN COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) = formal_informal_count.total_count THEN 'COINCIDE'
            ELSE 'INCONSISTENCIA'
        END = 'INCONSISTENCIA';
    
    
    """,
    """

    ---15.6 REPORTE formales Base de Datos - MTJ (según columna BT de condicion del predio catalogados como NPH)

    WITH cca_predio_data AS (
        SELECT 
            pd.qr_operacion_definitivo,
            CASE
                WHEN cpt.ilicode = 'NPH' THEN 'NPH' ELSE 'Informal' 
            END AS condicion_predio_bd
        FROM 
            {esquema}.cca_predio pd
        JOIN 
            {esquema}.cca_condicionprediotipo cpt 
            ON pd.condicion_predio = cpt.t_id
        WHERE 
            cpt.ilicode = 'NPH'
    ),
    matriz_mtj_data AS (
        SELECT 
            id_operacion AS qr_operacion_definitivo,
            CASE 
                WHEN condicion_predio IN ('NPH') THEN 'NPH' ELSE 'Informal' 
            END AS condicion_predio_mtj
        FROM  
            mtj.matriz_mtj
        WHERE 
            condicion_predio IN ('NPH')
    )
    SELECT 
        COALESCE(cca_predio_data.qr_operacion_definitivo, matriz_mtj_data.qr_operacion_definitivo) AS "QR_DERIVADO (ID_OPERACION)",
        cca_predio_data.condicion_predio_bd as "CONDICIÓN PREDIO BD",
        matriz_mtj_data.condicion_predio_mtj as "CONDICIÓN PREDIO MTJ",
        CASE 
            WHEN cca_predio_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en cca_predio o mal catalogado'
            WHEN matriz_mtj_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en matriz_mtj mal catalogado'
            WHEN cca_predio_data.condicion_predio_bd = matriz_mtj_data.condicion_predio_mtj THEN 'SI'
            ELSE 'INCONSISTENCIA'
        END AS "COINCIDE(SI/NO)"
    FROM 
        cca_predio_data
    FULL OUTER JOIN 
        matriz_mtj_data 
        ON cca_predio_data.qr_operacion_definitivo = matriz_mtj_data.qr_operacion_definitivo 
   
   WHERE
           CASE 
            WHEN cca_predio_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en cca_predio o mal catalogado'
            WHEN matriz_mtj_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en matriz_mtj mal catalogado'
            WHEN cca_predio_data.condicion_predio_bd = matriz_mtj_data.condicion_predio_mtj THEN 'SI'
            ELSE 'INCONSISTENCIA'
        END <>'SI';
   
    
    """,
    
    """
    
    ---- 20.4 - Cantidad de informales coincide  Base de Datos - MTJ (según columna BT de condicion del predio catalogados como Informales)"
    
    WITH condicion_predio_count AS (
        SELECT 
            cpt.ilicode AS condicion_predio, 
            COUNT(*) AS total_count
        FROM 
            {esquema}.cca_predio pd
        JOIN 
            {esquema}.cca_condicionprediotipo cpt 
            ON pd.condicion_predio = cpt.t_id
        WHERE 
            cpt.ilicode = 'Informal'
        GROUP BY  
            cpt.ilicode
    ),
    formal_informal_count AS (
        SELECT 
            'Total Formal' AS formal_informal, 
            SUM(total) AS total_count
        FROM (
            SELECT 
                condicion_predio, 
                COUNT(*) AS total
            FROM 
                mtj.matriz_mtj
            WHERE 
                condicion_predio IN ('Informal')
            GROUP BY 
                condicion_predio
        ) sub
    ),
    default_condicion_predio AS (
        SELECT 0 AS total_count
    )
    SELECT 
        COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) AS Informal_BD,
        formal_informal_count.total_count AS Informal_MTJ,
        CASE 
            WHEN COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) = formal_informal_count.total_count THEN 'COINCIDE'
            ELSE 'INCONSISTENCIA'
        END AS comparacion
    FROM 
        formal_informal_count
    LEFT JOIN 
        condicion_predio_count ON TRUE
    LEFT JOIN
        default_condicion_predio ON condicion_predio_count.total_count IS NULL
   
   where
           CASE 
            WHEN COALESCE(condicion_predio_count.total_count, default_condicion_predio.total_count) = formal_informal_count.total_count THEN 'COINCIDE'
            ELSE 'INCONSISTENCIA'
        END ='INCONSISTENCIA';
   
   
    """,
    
    """
    --15.8 REPORTE informales Base de Datos - MTJ (según columna BT de condicion del predio catalogados como informal)

    WITH cca_predio_data AS (
        SELECT 
            pd.qr_operacion_definitivo,
            CASE
                WHEN cpt.ilicode = 'Informal' THEN 'Informal' ELSE 'NPH' 
            END AS condicion_predio_bd
        FROM 
            {esquema}.cca_predio pd
        JOIN 
            {esquema}.cca_condicionprediotipo cpt 
            ON pd.condicion_predio = cpt.t_id
        WHERE 
            cpt.ilicode = 'Informal'
    ),
    matriz_mtj_data AS (
        SELECT 
            id_operacion AS qr_operacion_definitivo,
            CASE 
                WHEN condicion_predio IN ('Informal') THEN 'Informal' ELSE 'NPH' 
            END AS condicion_predio_mtj
        FROM  
            mtj.matriz_mtj
        WHERE 
            condicion_predio IN ('Informal')
    )
    SELECT 
        COALESCE(cca_predio_data.qr_operacion_definitivo, matriz_mtj_data.qr_operacion_definitivo) AS "QR_DERIVADO (ID_OPERACION)",
        cca_predio_data.condicion_predio_bd AS "CONDICIÓN PREDIO BD",
        matriz_mtj_data.condicion_predio_mtj AS "CONDICIÓN PREDIO MTJ",
        CASE 
            WHEN cca_predio_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en cca_predio o mal catalogado'
            WHEN matriz_mtj_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en matriz_mtj o mal catalogado'
            WHEN cca_predio_data.condicion_predio_bd = matriz_mtj_data.condicion_predio_mtj THEN 'SI'
            ELSE 'INCONSISTENCIA'
        END AS "COINCIDE(SI/NO)"
    FROM 
        cca_predio_data
    FULL OUTER JOIN 
        matriz_mtj_data 
        ON cca_predio_data.qr_operacion_definitivo = matriz_mtj_data.qr_operacion_definitivo
	where
	        CASE 
            WHEN cca_predio_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en cca_predio o mal catalogado'
            WHEN matriz_mtj_data.qr_operacion_definitivo IS NULL THEN 'NO, Falta en matriz_mtj o mal catalogado'
            WHEN cca_predio_data.condicion_predio_bd = matriz_mtj_data.condicion_predio_mtj THEN 'SI'
            ELSE 'INCONSISTENCIA'
        END <>'SI';
   
    """,
    """

    ---20.5	Informal tenga el mismo matriz tanto en Base de Datos como MTJ

    WITH cca_predio_data AS (
        SELECT 
            qr_operacion,
            qr_operacion_definitivo,
            qr_operacion || '-' || qr_operacion_definitivo AS concatenado_bd
        FROM 
            {esquema}.cca_predio
    ),
    matriz_mtj_data AS (
        SELECT 
            local_id,
            id_operacion,
            local_id || '-' || id_operacion AS concatenado_mtj
        FROM 
            mtj.matriz_mtj
    )
    SELECT 
        cca_predio_data.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD", 
        cca_predio_data.qr_operacion_definitivo AS "QR_DERIVADO (ID_OPERACION) BD",
        cca_predio_data.concatenado_bd AS "UNION_BD",
        matriz_mtj_data.local_id AS "QR_MATRIZ (CODIGO_NIVEL) MTJ",
        matriz_mtj_data.id_operacion AS "QR_DERIVADO (ID_OPERACION) MTJ",
        matriz_mtj_data.concatenado_mtj AS "UNION_MTJ",
        CASE 
            WHEN cca_predio_data.concatenado_bd = matriz_mtj_data.concatenado_mtj THEN 'SI'
            ELSE 'NO COINCIDE MATRIZ Ó SIN COINCIDENCIA QR BD-MTJ'
        END AS "COINCIDE(SI/NO)"
    FROM 
        cca_predio_data
    FULL OUTER JOIN 
        matriz_mtj_data 
        ON cca_predio_data.qr_operacion_definitivo = matriz_mtj_data.id_operacion
	WHERE
	        CASE 
            WHEN cca_predio_data.concatenado_bd = matriz_mtj_data.concatenado_mtj THEN 'SI'
            ELSE 'NO COINCIDE MATRIZ Ó SIN COINCIDENCIA QR BD-MTJ'
        END <>'SI';

   
    """,
    """
	-- 16.1 la cantidad de dominios debe ser igual en MTJ (COLUMNA BS) y BD

	WITH primera_consulta AS (
		SELECT 
			drt.ilicode AS derecho_tipo, 
			COUNT(*) AS cuenta_derecho_bd
		FROM 
			{esquema}.cca_predio pd
		JOIN 
			{esquema}.cca_derecho dr 
			ON pd.t_id = dr.predio
		JOIN 
			{esquema}.cca_derechotipo drt 
			ON dr.tipo = drt.t_id
		GROUP BY 
			drt.ilicode
	),
	segunda_consulta AS (
		SELECT 
			CASE
				WHEN tipo_derecho ILIKE 'ocupación' OR tipo_derecho ILIKE 'ocupacion' THEN 'Ocupacion'
				WHEN tipo_derecho ILIKE 'posesión' OR tipo_derecho ILIKE 'posesion' THEN 'Posesion'
				WHEN tipo_derecho ILIKE 'dominio' THEN 'Dominio'
				ELSE 'PEND'
			END AS tipo_der,
			COUNT(*) AS cuenta_derecho_mtj
		FROM 
			mtj.matriz_mtj
		GROUP BY 
			tipo_der
	)
	SELECT 
		COALESCE(pc.derecho_tipo, sc.tipo_der) AS "TIPO DERECHO",
		pc.cuenta_derecho_bd AS "CANTIDAD BD",
		sc.cuenta_derecho_mtj AS "CANTIDAD MTJ",
		CASE 
			WHEN pc.cuenta_derecho_bd = sc.cuenta_derecho_mtj THEN 'SI'
			ELSE 'NO, DIFIERE'
		END AS "COINCIDE (SI/NO)"
	FROM 
		primera_consulta pc
	FULL OUTER JOIN 
		segunda_consulta sc
		ON pc.derecho_tipo = sc.tipo_der
	WHERE 
		sc.tipo_der = 'Dominio'
		AND CASE 
			WHEN pc.cuenta_derecho_bd = sc.cuenta_derecho_mtj THEN 'SI'
			ELSE 'NO, DIFIERE'
		END <> 'SI'
	ORDER BY 
		pc.derecho_tipo, sc.tipo_der;


	
    """,
	
    """
    -----  16.1 REPORTE DOMINIOS QUE DIFIEREN

    WITH primera_consulta AS (
        SELECT qr_operacion, qr_operacion_definitivo, drt.ilicode as derecho_tipo
        FROM {esquema}.cca_predio pd
        JOIN {esquema}.cca_derecho dr ON pd.t_id = dr.predio
        JOIN {esquema}.cca_derechotipo drt ON dr.tipo = drt.t_id
        WHERE drt.ilicode = 'Dominio'
    ),

    segunda_consulta AS (
        SELECT local_id, id_operacion,
            CASE
                WHEN tipo_derecho IN ('Ocupación', 'Ocupacion', 'ocupacion', 'ocupación') THEN 'Ocupacion'
                WHEN tipo_derecho IN ('Posesión', 'Posesion', 'posesion', 'posesión') THEN 'Posesion'
                WHEN tipo_derecho IN ('Dominio', 'dominio','Dominio.PROPIEDAD_COLECTIVA_DE_PUEBLO_O_COMUNIDAD_ETNICA') THEN 'Dominio'
                ELSE 'SIN DEFINICION'
            END AS tipo_der
        FROM mtj.matriz_mtj
        WHERE tipo_derecho IN ('Dominio', 'dominio')
    )
    SELECT 
        pc.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD",
        pc.qr_operacion_definitivo AS "QR_DERIVADO (ID_OPERACION) BD",
        pc.derecho_tipo AS "TIPO DERECHO BD",
        sc.local_id AS "QR_MATRIZ (CODIGO_NIVEL) MTJ",
        sc.id_operacion AS "QR_DERIVADO (ID_OPERACION) MTJ",
        sc.tipo_der  AS "TIPO DERECHO MTJ",
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.derecho_tipo = sc.tipo_der THEN 'SI'
            ELSE 'NO, AJUSTAR'
        END AS "COINCIDE(SI/NO)"
    FROM primera_consulta pc
    FULL OUTER JOIN segunda_consulta sc
    ON pc.qr_operacion_definitivo = sc.id_operacion

    where
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.derecho_tipo = sc.tipo_der THEN 'SI'
            ELSE 'NO, AJUSTAR'
        END <>'SI'
		ORDER BY pc.qr_operacion, sc.id_operacion;
    
    """,
	
	"""
	--- 16.3 La cantidad de posesiones debe coincidir BD MTJ	

	WITH primera_consulta AS (
		SELECT 
			drt.ilicode AS derecho_tipo, 
			COUNT(*) AS cuenta_derecho_bd
		FROM 
			{esquema}.cca_predio pd
		JOIN 
			{esquema}.cca_derecho dr 
			ON pd.t_id = dr.predio
		JOIN 
			{esquema}.cca_derechotipo drt 
			ON dr.tipo = drt.t_id
		GROUP BY 
			drt.ilicode
	),
	segunda_consulta AS (
		SELECT 
			CASE
				WHEN tipo_derecho ILIKE 'ocupación' OR tipo_derecho ILIKE 'ocupacion' THEN 'Ocupacion'
				WHEN tipo_derecho ILIKE 'posesión' OR tipo_derecho ILIKE 'posesion' THEN 'Posesion'
				WHEN tipo_derecho ILIKE 'dominio' THEN 'Dominio'
				ELSE 'PEND'
			END AS tipo_der,
			COUNT(*) AS cuenta_derecho_mtj
		FROM 
			mtj.matriz_mtj
		GROUP BY 
			tipo_der
	)
	SELECT 
		COALESCE(pc.derecho_tipo, sc.tipo_der) AS "TIPO DERECHO",
		pc.cuenta_derecho_bd AS "CANTIDAD BD",
		sc.cuenta_derecho_mtj AS "CANTIDAD MTJ",
		CASE 
			WHEN pc.cuenta_derecho_bd = sc.cuenta_derecho_mtj THEN 'SI'
			ELSE 'NO, DIFIERE'
		END AS "COINCIDE (SI/NO)"
	FROM 
		primera_consulta pc
	FULL OUTER JOIN 
		segunda_consulta sc
		ON pc.derecho_tipo = sc.tipo_der
	WHERE 
		sc.tipo_der = 'Posesion'
		AND CASE 
			WHEN pc.cuenta_derecho_bd = sc.cuenta_derecho_mtj THEN 'SI'
			ELSE 'NO, DIFIERE'
		END <> 'SI'
	ORDER BY 
		pc.derecho_tipo, sc.tipo_der;

	
	""",
	
	
    """

    --- 16.4   REPORTE POSESIONES QUE COINCIDEN O NO

    WITH primera_consulta AS (
        SELECT qr_operacion, qr_operacion_definitivo, drt.ilicode as derecho_tipo
        FROM {esquema}.cca_predio pd
        JOIN {esquema}.cca_derecho dr ON pd.t_id = dr.predio
        JOIN {esquema}.cca_derechotipo drt ON dr.tipo = drt.t_id
        WHERE drt.ilicode = 'Posesion'
    ),

    segunda_consulta AS (
        SELECT local_id, id_operacion,
            CASE
                WHEN tipo_derecho IN ('Ocupación', 'Ocupacion', 'ocupacion', 'ocupación') THEN 'Ocupacion'
                WHEN tipo_derecho IN ('Posesión', 'Posesion', 'posesion', 'posesión') THEN 'Posesion'
                WHEN tipo_derecho IN ('Dominio', 'dominio') THEN 'Dominio'
                ELSE 'PEND'
            END AS tipo_der
        FROM mtj.matriz_mtj
        WHERE tipo_derecho IN ('Posesión', 'Posesion', 'posesion', 'posesión')
    )
    SELECT 
        pc.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD",
        pc.qr_operacion_definitivo  AS "QR_DERIVADO (ID_OPERACION)BD",
        pc.derecho_tipo AS "TIPO DERECHO BD",
        sc.local_id "QR_MATRIZ (CODIGO_NIVEL) MTJ",
        sc.id_operacion  AS "QR_DERIVADO (ID_OPERACION) MTJ",
        sc.tipo_der AS "TIPO DERECHO MTJ",
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.derecho_tipo = sc.tipo_der THEN 'SI'
            ELSE 'NO, AJUSTAR'
        END AS "COINCIDE(SI/NO)"
    FROM primera_consulta pc
    FULL OUTER JOIN segunda_consulta sc
    ON pc.qr_operacion_definitivo = sc.id_operacion

	where
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.derecho_tipo = sc.tipo_der THEN 'SI'
            ELSE 'NO, AJUSTAR'
        END <> 'SI'
		ORDER BY pc.qr_operacion, sc.id_operacion;



    """,
	"""
	-- 16.3 - la cantidad de Ocupaciones debe ser igual en MTJ (COLUMNA BS) y BD
	

	WITH primera_consulta AS (
		SELECT 
			drt.ilicode AS derecho_tipo, 
			COUNT(*) AS cuenta_derecho_bd
		FROM 
			{esquema}.cca_predio pd
		JOIN 
			{esquema}.cca_derecho dr 
			ON pd.t_id = dr.predio
		JOIN 
			{esquema}.cca_derechotipo drt 
			ON dr.tipo = drt.t_id
		GROUP BY 
			drt.ilicode
	),
	segunda_consulta AS (
		SELECT 
			CASE
				WHEN tipo_derecho ILIKE 'ocupación' OR tipo_derecho ILIKE 'ocupacion' THEN 'Ocupacion'
				WHEN tipo_derecho ILIKE 'posesión' OR tipo_derecho ILIKE 'posesion' THEN 'Posesion'
				WHEN tipo_derecho ILIKE 'dominio' THEN 'Dominio'
				ELSE 'PEND'
			END AS tipo_der,
			COUNT(*) AS cuenta_derecho_mtj
		FROM 
			mtj.matriz_mtj
		GROUP BY 
			tipo_der
	)
	SELECT 
		COALESCE(pc.derecho_tipo, sc.tipo_der) AS "TIPO DERECHO",
		pc.cuenta_derecho_bd AS "CANTIDAD BD",
		sc.cuenta_derecho_mtj AS "CANTIDAD MTJ",
		CASE 
			WHEN pc.cuenta_derecho_bd = sc.cuenta_derecho_mtj THEN 'SI'
			ELSE 'NO, DIFIERE'
		END AS "COINCIDE (SI/NO)"
	FROM 
		primera_consulta pc
	FULL OUTER JOIN 
		segunda_consulta sc
		ON pc.derecho_tipo = sc.tipo_der
	WHERE 
		sc.tipo_der = 'Ocupacion'
		AND CASE 
			WHEN pc.cuenta_derecho_bd = sc.cuenta_derecho_mtj THEN 'SI'
			ELSE 'NO, DIFIERE'
		END <> 'SI'
	ORDER BY 
		pc.derecho_tipo, sc.tipo_der;	
	
	
	""",
	
	
    """

    --- 21.3   REPORTE OCUPACIONES QUE COINCIDEN O NO

    WITH primera_consulta AS (
        SELECT qr_operacion, qr_operacion_definitivo, drt.ilicode as derecho_tipo
        FROM {esquema}.cca_predio pd
        JOIN {esquema}.cca_derecho dr ON pd.t_id = dr.predio
        JOIN {esquema}.cca_derechotipo drt ON dr.tipo = drt.t_id
        WHERE drt.ilicode = 'Ocupacion'
    ),

    segunda_consulta AS (
        SELECT local_id, id_operacion,
            CASE
                WHEN tipo_derecho IN ('Ocupación', 'Ocupacion', 'ocupacion', 'ocupación') THEN 'Ocupacion'
                WHEN tipo_derecho IN ('Posesión', 'Posesion', 'posesion', 'posesión') THEN 'Posesion'
                WHEN tipo_derecho IN ('Dominio', 'dominio') THEN 'Dominio'
                ELSE 'PEND'
            END AS tipo_der
        FROM mtj.matriz_mtj
        WHERE tipo_derecho IN ('Ocupación', 'Ocupacion', 'ocupacion', 'ocupación')
    )
    SELECT 
        pc.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD",
        pc.qr_operacion_definitivo  AS "QR_DERIVADO (ID_OPERACION) BD",
        pc.derecho_tipo AS "TIPO DERECHO BD",
        sc.local_id "QR_MATRIZ (CODIGO_NIVEL) MTJ",
        sc.id_operacion  AS "QR_DERIVADO (ID_OPERACION) MTJ",
        sc.tipo_der AS "TIPO DERECHO MTJ",
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.derecho_tipo = sc.tipo_der THEN 'SI'
            ELSE 'NO, AJUSTAR'
        END AS "COINCIDE(SI/NO)"
    FROM primera_consulta pc
    FULL OUTER JOIN segunda_consulta sc
    ON pc.qr_operacion_definitivo = sc.id_operacion

	where
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.derecho_tipo = sc.tipo_der THEN 'SI'
            ELSE 'NO, AJUSTAR'
        END <> 'SI'
		    ORDER BY pc.qr_operacion, sc.id_operacion;
	
	

    """,
    """

    --- 17.1- Coincidencia de los QR tanto en MTJ como en BD

    WITH primera_consulta AS (
        SELECT qr_operacion, qr_operacion_definitivo
        FROM {esquema}.cca_predio pd
    ),
    segunda_consulta AS (
        SELECT local_id, id_operacion
        FROM mtj.matriz_mtj
    )
    SELECT 
        pc.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD",
        pc.qr_operacion_definitivo  AS "QR_DERIVADO (ID_OPERACION) BD",
        sc.local_id "QR_MATRIZ (CODIGO_NIVEL) MTJ",
        sc.id_operacion  AS "QR_DERIVADO (ID_OPERACION) MTJ",
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.qr_operacion_definitivo = sc.id_operacion THEN 'SI'
            ELSE 'NO, AJUSTAR'
        END AS "COINCIDE(SI/NO)"
    FROM primera_consulta pc
    FULL OUTER JOIN segunda_consulta sc
    ON pc.qr_operacion_definitivo = sc.id_operacion
	WHERE
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.qr_operacion_definitivo = sc.id_operacion THEN 'SI'
            ELSE 'NO, AJUSTAR'
        END <> 'SI'
    ORDER BY pc.qr_operacion, sc.id_operacion;

    """,
    """
    ---- 17.2	Coincidencia de los numeros prediales tanto en MTJ como en BD
    
    WITH primera_consulta AS (
        SELECT t_id, qr_operacion, qr_operacion_definitivo, numero_predial
        FROM {esquema}.cca_predio
    ),

    segunda_consulta AS (
        SELECT 
            id, local_id, 
            id_operacion, 
            numero_predial, 
            numero_predial_provisional,tipo_novedad,
            CASE 
                WHEN numero_predial_provisional IS NULL THEN numero_predial
                WHEN LENGTH(numero_predial_provisional) >= 18 AND SUBSTRING(numero_predial_provisional FROM 18 FOR 1) SIMILAR TO '[A-Za-z]' THEN numero_predial_provisional
                WHEN numero_predial_provisional SIMILAR TO '%[^[:alnum:][:space:]]%'  THEN numero_predial
                ELSE numero_predial_provisional
            END AS PREDIAL_DEF
        FROM 
            mtj.matriz_mtj	
    )
    SELECT
        pc.t_id as "T_ID BD",
        pc.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL) BD",
        pc.qr_operacion_definitivo  AS "QR_DERIVADO (ID_OPERACION) BD",
        pc.numero_predial AS "NUMERO_PREDIAL_BD",
        sc.id as "ID MTJ",
        sc.local_id "QR_MATRIZ (CODIGO_NIVEL) MTJ",
        sc.id_operacion  AS "QR_DERIVADO (ID_OPERACION)MTJ",
        sc.numero_predial as "NUMERO PREDIAL VIGENTE",
        sc.numero_predial_provisional as "NUMERO PREDIAL (PROVISIONAL)",
        sc.tipo_novedad as "TIPO DE NOVEDAD NÚMERO PREDIAL (MODELO LADM)",
        sc.PREDIAL_DEF AS "TOTALES PREDIALES_MTJ",
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.numero_predial = sc.PREDIAL_DEF THEN 'SI'
            ELSE 'NO, AJUSTAR Ó ACTUALIZAR A NPN PROVISIONAL'
        END AS "COINCIDE(SI/NO)",

        CASE 
            WHEN pc.numero_predial IS NOT NULL AND sc.PREDIAL_DEF IS NOT NULL
            THEN 'UPDATE cambiar_esquema.cca_predio SET numero_predial =' || sc.PREDIAL_DEF || ' WHERE t_id =' || pc.t_id
            ELSE NULL
        END AS "CONSULTA_EJEMPLO_NPN"        
        
    FROM primera_consulta pc
    FULL OUTER JOIN segunda_consulta sc
    ON pc.qr_operacion_definitivo = sc.id_operacion
	WHERE
        CASE 
            WHEN pc.qr_operacion_definitivo IS NULL THEN 'NO, FALTA EN CCA_PREDIO O MAL DILIGENCIADO'
            WHEN sc.id_operacion IS NULL THEN 'NO, FALTA EN MTJ O MAL DILIGENCIADO'
            WHEN pc.numero_predial = sc.PREDIAL_DEF THEN 'SI'
            ELSE 'NO, AJUSTAR Ó ACTUALIZAR A NPN PROVISIONAL'
        END <> 'SI'

    ORDER BY pc.qr_operacion, sc.id_operacion;


    """,
    """

    --- 17.3	Si tipo de novedad numero predial es Predio_Nuevo, entonces debe tener numero provisional asignado en la MTJ

    SELECT
        id as "ID",
        local_id as "QR_MATRIZ (CODIGO_NIVEL)", 
        id_operacion as "QR_DERIVADO(ID_OPERACION)", 
        numero_predial as "NUMERO PREDIAL VIGENTE", 
        numero_predial_provisional as "NUMERO PREDIAL (PROVISIONAL)",tipo_novedad as "TIPO DE NOVEDAD NÚMERO PREDIAL (MODELO LADM)",  'VERIFICAR,FALTA PREDIAL PROVISIONAL' as "VALIDACION"
    FROM mtj.matriz_mtj		
    WHERE tipo_novedad ='Predio_Nuevo' and numero_predial_provisional is null
	or tipo_novedad ='Predio_Nuevo' and numero_predial_provisional =''
	or tipo_novedad ='Predio_Nuevo' and numero_predial_provisional ='0'
    or  tipo_novedad ='Predio_Nuevo' and numero_predial_provisional SIMILAR TO '%[^[:alnum:][:space:]]%'

    """,
    """

    -----17.4  REPETICIONES FORMALES SOBRE LA BASE  DE DATOS    
    SELECT 
        numero_predial,
        CONDICION_PREDIO,
        STRING_AGG(qr_operacion_definitivo, ', ') AS qr_operacion_definitivo_afectados,
        repeticiones, 'VERIFIFCAR, UN NUMERO PREDIAL SOLO DEBE ESTAR ASOCIADO A 1 QR FORMAL' as validacion
    FROM 
        (SELECT 
            pd.numero_predial,
            pd.qr_operacion_definitivo,
            cpt.ilicode as CONDICION_PREDIO,
            COUNT(*) OVER (PARTITION BY pd.numero_predial) AS repeticiones
        FROM 
            {esquema}.cca_predio pd
        JOIN 
            {esquema}.cca_condicionprediotipo cpt ON pd.condicion_predio = cpt.t_id
        WHERE 
            cpt.ilicode = 'NPH'
        ) AS subquery
    WHERE 
        repeticiones > 1
    GROUP BY 
        numero_predial, CONDICION_PREDIO, repeticiones;


    """,
	"""
	--- 17.5 - El  Folio de Matrícula Inmobiliaria debe coincidir tanto en la MTJ como en la Base de Datos	

	SELECT pd.qr_operacion as "QR_MATRIZ_BD (CODIGO_NIVEL)", pd.qr_operacion_definitivo as "QR_DERIVADO_BD(ID_OPERACION)" , CONCAT(pd.codigo_orip,'-',pd.matricula_inmobiliaria) as "FMI_BD", 
	mtj.local_id as "QR_MATRIZ_MTJ (CODIGO_NIVEL)", mtj.id_operacion as "QR_DERIVADO_MTJ(ID_OPERACION)",
	CONCAT(mtj."Codigo_Orip",'-',mtj."Matricula_Inmobiliaria") as "FMI_MTJ",
	CASE
		when CONCAT(mtj."Codigo_Orip",'-',mtj."Matricula_Inmobiliaria")= CONCAT(pd.codigo_orip,'-',pd.matricula_inmobiliaria) then 'SI'
		when pd.qr_operacion_definitivo IS NULL AND mtj.id_operacion IS NOT NULL THEN 'QR NO Relacionado en BD'
		when pd.qr_operacion_definitivo IS NOT NULL AND mtj.id_operacion IS NULL THEN 'QR NO Relacionado en MTJ'
		else 'No, Falta relacionar FMI ó estructura errónea en BD'
	end as "COINCIDE (SI/NO)"

	FROM {esquema}.cca_predio pd
	full outer join mtj.matriz_mtj as mtj ON  pd.qr_operacion_definitivo=mtj.id_operacion
	where 
	CASE
		when CONCAT(mtj."Codigo_Orip",'-',mtj."Matricula_Inmobiliaria")= CONCAT(pd.codigo_orip,'-',pd.matricula_inmobiliaria) then 'SI'
		when pd.qr_operacion_definitivo IS NULL AND mtj.id_operacion IS NOT NULL THEN 'QR NO Relacionado en BD'
		when pd.qr_operacion_definitivo IS NOT NULL AND mtj.id_operacion IS NULL THEN 'QR NO Relacionado en MTJ'
		else 'No, Verificar valor de FMI o estructura en BD'
	end <> 'SI';
	
	""",

    """

    ---- 17.6 - No puede existir QR definitivos repetidos en la MTJ
    
    select id,id_operacion, count(id_operacion) as repetidos 
    from mtj.matriz_mtj
    group by id, id_operacion
    HAVING count(id_operacion) > 1


    """,
    """
    ---- reporte 1 intereados 
    
    WITH interesados_bd AS (

            SELECT 
                pd.qr_operacion_definitivo,
                STRING_AGG(int.ilicode, ',') AS interesados_tipo_bd,
                STRING_AGG(indt.ilicode, ',') AS interesados_documentotipo_bd,
                STRING_AGG(i.documento_identidad, ',') AS interesados_documento_bd,
                STRING_AGG(
                    CASE 
                        WHEN indt.ilicode = 'NIT' THEN i.razon_social
                        ELSE CONCAT(i.primer_nombre, ' ', i.segundo_nombre, ' ', i.primer_apellido, ' ', i.segundo_apellido)
                    END, 
                    ','
                ) AS interesados_bd
            FROM 
                {esquema}.cca_predio pd
            JOIN 
                {esquema}.cca_derecho dr ON pd.t_id = dr.predio
            JOIN 
                {esquema}.cca_interesado i ON dr.t_id = i.derecho
            JOIN 
                {esquema}.cca_interesadotipo int ON i.tipo = int.t_id
            JOIN
                {esquema}.cca_interesadodocumentotipo indt ON i.tipo_documento = indt.t_id
            GROUP BY 
                pd.qr_operacion_definitivo
        ),
        comparisons AS (
            SELECT 
                mtj.id_operacion,
                mtj.condicion_predio,
                mtj."CR_InteresadoTipo" AS "Interesa_Tipo_MTJ",
                ibd.interesados_tipo_bd AS "Interesa_Tipo_BD",    
                CASE 
                    WHEN ARRAY(SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(mtj."CR_InteresadoTipo", '\s+', '', 'g')), ',')) ORDER BY 1) = ARRAY(SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(ibd.interesados_tipo_bd, '\s+', '', 'g')), ',')) ORDER BY 1) THEN 'SI' 
                    ELSE 'NO' 
                END AS "COINCIDEN(SI/NO) TIPO_INT",
                
                mtj."CR_DocumentoTipo" AS "Documento_Tipo_MTJ",
                ibd.interesados_documentotipo_bd AS "Documento_Tipo_BD",
                CASE 
                    WHEN ARRAY(SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(mtj."CR_DocumentoTipo", '\s+', '', 'g')), ',')) ORDER BY 1) = ARRAY(SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(ibd.interesados_documentotipo_bd, '\s+', '', 'g')), ',')) ORDER BY 1) THEN 'SI' 
                    ELSE 'NO' 
                END AS "COINCIDEN(SI/NO) DOC_TIPO",    
                
                mtj."Documento_Identidad" AS "Num_Documento_MTJ",
                ibd.interesados_documento_bd AS "Num_Documento_BD",    
                CASE 
                    WHEN ARRAY(SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(mtj."Documento_Identidad", '\s+', '', 'g')), ',')) ORDER BY 1) = ARRAY(SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(ibd.interesados_documento_bd, '\s+', '', 'g')), ',')) ORDER BY 1) THEN 'SI' 
                    ELSE 'NO' 
                END AS "COINCIDEN(SI/NO) NUMERO_DOC_ID",        
                
                mtj."CR_Interesado_all" AS "Interesados_MTJ",
                ibd.interesados_bd AS "Interesados_BD",
                CASE 
                    WHEN ARRAY(
                            SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(unaccent(UPPER(mtj."CR_Interesado_all")), '\s+', '', 'g')), ',')) 
                            ORDER BY 1
                        ) = ARRAY(
                            SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(unaccent(UPPER(ibd.interesados_bd)), '\s+', '', 'g')), ',')) 
                            ORDER BY 1
                        ) THEN 'SI' 
                    ELSE 'NO' 
                END AS "COINCIDEN(SI/NO) NOMBRE_INTERESADOS",
                ARRAY(
                    SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(unaccent(UPPER(mtj."CR_Interesado_all")), '\s+', '', 'g')), ',')) 
                    EXCEPT 
                    SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(unaccent(UPPER(ibd.interesados_bd)), '\s+', '', 'g')), ',')) 
                ) AS "DIFERENCIAS_INTERESADOS_MTJ",
                ARRAY(
                    SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(unaccent(UPPER(ibd.interesados_bd)), '\s+', '', 'g')), ',')) 
                    EXCEPT 
                    SELECT UNNEST(STRING_TO_ARRAY(TRIM(regexp_replace(unaccent(UPPER(mtj."CR_Interesado_all")), '\s+', '', 'g')), ',')) 
                ) AS "DIFERENCIAS_INTERESADOS_BD"


            FROM 
                mtj.matriz_mtj mtj
            LEFT JOIN 
                interesados_bd ibd ON mtj.id_operacion = ibd.qr_operacion_definitivo

        )
		SELECT 
			*
		FROM comparisons
		WHERE 
			"COINCIDEN(SI/NO) TIPO_INT" <> 'SI'
			OR "COINCIDEN(SI/NO) DOC_TIPO" <> 'SI'
			OR "COINCIDEN(SI/NO) NUMERO_DOC_ID" <> 'SI'
			OR "COINCIDEN(SI/NO) NOMBRE_INTERESADOS" <> 'SI';


    """,
    """
    ---19.1 - El campo tiene_construcciones debe estar diligenciado

    SELECT id, local_id as "QR_MATRIZ (CODIGO_NIVEL)", id_operacion as "QR_DERIVADO(ID_OPERACION)", 'FALTA DILIGENCIAR EN MTJ' as tiene_construcciones
    FROM mtj.matriz_mtj
    WHERE tiene_construcciones IS NULL 
    OR tiene_construcciones = '' 
    OR tiene_construcciones = '0';

    """,
    """
    -- 19.2	El campo "tipo novedad numero predial" debe estar diligenciado

    SELECT id, local_id as "QR_MATRIZ (CODIGO_NIVEL)", id_operacion as "QR_DERIVADO(ID_OPERACION)", 'FALTA DILIGENCIAR EN MTJ' as tipo_novedad
    FROM mtj.matriz_mtj
    WHERE tipo_novedad IS NULL 
    OR tipo_novedad = '' 
    OR tipo_novedad = '0';
        

    """,

    """
    ---19.3	El campo "Predio formal informal" debe estar diligenciado

    
    SELECT id, local_id as "QR_MATRIZ (CODIGO_NIVEL)", id_operacion as "QR_DERIVADO(ID_OPERACION)", 'FALTA DILIGENCIAR EN MTJ' as formal_informal
    FROM mtj.matriz_mtj
    WHERE formal_informal IS NULL 
    OR formal_informal = '' 
    OR formal_informal = '0';    

    """,

    """
    ----19.4	El campo "Naturaleza predio" debe estar dilifenciado


    SELECT id, local_id as "QR_MATRIZ (CODIGO_NIVEL)", id_operacion as "QR_DERIVADO(ID_OPERACION)", 'FALTA DILIGENCIAR EN MTJ' as naturaleza_predio
    FROM mtj.matriz_mtj
    WHERE naturaleza_predio IS NULL 
    OR naturaleza_predio = '' 
    OR naturaleza_predio = '0';


    """,
    """
    --- 19.5	El campo "Tipo predio" debe estar diligenciado

    SELECT id, local_id as "QR_MATRIZ (CODIGO_NIVEL)", id_operacion as "QR_DERIVADO(ID_OPERACION)", 'FALTA DILIGENCIAR EN MTJ' as tipo_predio
    FROM mtj.matriz_mtj
    WHERE tipo_predio IS NULL 
    OR tipo_predio = '' 
    OR tipo_predio = '0'; 



    """,
    """
    ---19.6	El campo "Tipo derecho" debe estar diligenciado

    SELECT id, local_id as "QR_MATRIZ (CODIGO_NIVEL)", id_operacion as "QR_DERIVADO(ID_OPERACION)", 'FALTA DILIGENCIAR EN MTJ' as tipo_derecho
    FROM mtj.matriz_mtj
    WHERE tipo_derecho IS NULL 
    OR tipo_derecho = '' 
    OR tipo_derecho = '0';


    """,
    """
    -- 19.7	El capo "Condicion predio" debe estar diligenciado

        
    SELECT id, local_id as "QR_MATRIZ (CODIGO_NIVEL)", id_operacion as "QR_DERIVADO(ID_OPERACION)", 'FALTA DILIGENCIAR EN MTJ' as condicion_predio
    FROM mtj.matriz_mtj
    WHERE condicion_predio IS NULL 
    OR condicion_predio = '' 
    OR condicion_predio = '0';
    
    
    """


    
        
    


]

nombres_consultas_observaciones_mtj = [
    "13.1 - Area  de Levantamiento en Base de datos coincide con area MTJ",
    "13.2 - Area  y numero de construcciones coincide Base de Datos  MTJ",
    "14.1 - Coindicencia del Tipo de Fuente administrativa entre Base de Datos - MTJ",
    "14.2 - Coindicencia del Ente emisor del documento de la Fuente administrativa entre Base de Datos - MTJ",
    "14.3 - Coindicencia del Número de Fuente de documento de la Fuente administrativa entre Base de Datos - MTJ",
    "14.4 - Coindicencia de la Fecha del documento de la Fuente administrativa entre Base de Datos - MTJ",
    "15.1 - Coincidencia de la Cantidad de formales según columna BP(formal_informal) coincide MTJ - Base de Datos (Dominios)",
    "15.2 - En concordancia con la Regla 15.1 sino coincide algun registro, se presenta el Reporte de formales que NO coinciden según columna BP(formal_informal) MTJ - BD(Dominios)",
    "15.3 - Coincidencia de la Cantidad de informales según columna BP(formal_informal) coincide MTJ - BD",
    "15.4 - En concordancia con la Regla 15.3 sino coincide algun registro, se presenta el Reporte de informales que NO coinciden según columna BP(formal_informal) MTJ - BD",
    "15.5 - Cantidad de formales coincide  Base de Datos (NPH) - MTJ (según columna BT de condicion del predio catalogados como NPH)",
    "15.6 - En concordancia con la regla 15.5 sino coincide algún registro, se presenta el Reporte de formales que NO coinciden  Base de Datos((NPH) - MTJ (según columna BT de condicion del predio catalogados como NPH)",
    "15.7 - Cantidad de informales coincide  Base de Datos - MTJ (según columna BT de condicion del predio catalogados como Informales)",
    "15.8 - En concordancia con la regla 15.7 sino coincide algún registro, se presenta el Reporte de informales que NO coinciden Base de Datos - MTJ (según columna BT de condicion del predio catalogados como Informales)",
    "15.9 - Informal tenga el mismo matriz tanto en Base de Datos como MTJ",
    "16.1 - la cantidad de Dominios debe ser igual en MTJ (COLUMNA BS) y BD",
    "16.2 - En concordancia con la Regla 16.1 se presenta el Reporte de los predios con derecho Dominio que Diferen entre MTJ-BD",
    "16.3 - la cantidad de Posesiones debe ser igual en MTJ (COLUMNA BS) y BD",
    "16.4 - En concordancia con la Regla 16.3 se presenta el Reporte de los predios con derecho Posesión que Diferen entre MTJ-BD",
    "16.5 - la cantidad de Ocupaciones debe ser igual en MTJ (COLUMNA BS) y BD",
    "16.6 - En concordancia con la Regla 16.5 se presenta el Reporte de los predios con derecho Ocupación que Diferen entre MTJ-BD",
    "17.1 - Los QR definitivos deben ser iguales tanto en MTJ como en BD",
    "17.2 - Los numeros prediales deben coincidir tanto en MTJ como en BD",
    "17.3 - Si tipo de novedad numero predial es Predio_Nuevo, entonces debe tener numero provisional asignado en la MTJ",
    "17.4 - No pueden haber formalidades con un mismo número predial en la Base de Datos",
    "17.5 - El  Folio de Matrícula Inmobiliaria debe coincidir tanto en la MTJ como en la Base de Datos", 
    "17.6 - No puede existir QR definitivos repetidos en la MTJ",
    "18.1 - Los diferentes QR deben tener correspondencia de los interesados tanto en MTJ como en la base de datos en cuanto a : tipo de interesado, documento del interesado, documento de identificacion, nombres del interesado y con ello la cantidad de interesados",

    "19.1 - El campo tiene_construcciones debe estar diligenciado en la MTJ",
    "19.2 - El campo tipo_novedad numero predial debe estar diligenciado en la MTJ",
    "19.3 - El campo Predio_formal informal debe estar diligenciado en la MTJ",
    "19.4 - El campo Naturaleza_predio debe estar dilifenciado en la MTJ",
    "19.5 - El campo Tipo_predio debe estar diligenciado en la MTJ",
    "19.6 - El campo Tipo_derecho debe estar diligenciado en la MTJ",
    "19.7 - El campo Condicion_predio debe estar diligenciado en la MTJ"

    

    
    

]
