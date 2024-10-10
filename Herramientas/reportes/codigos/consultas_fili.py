import pandas as pd

def ejecutar_consulta_fili(conexion, esquema_seleccionado):
    queries = {
        'HOJA_MTJ': f"""
        SELECT 
            cp.qr_operacion AS "QR_MATRIZ (CODIGO_NIVEL)", 
            cp.qr_operacion_definitivo AS "QR_DERIVADO(ID_OPERACION)",
            CASE 
                WHEN mt.ilicode = 'Directo' THEN 'Metodo_Directo'
                WHEN mt.ilicode = 'Indirecto' THEN 'Metodo_Indirecto'
                WHEN mt.ilicode = 'Colaborativo_Declarativo' THEN 'Metodo_Declarativo_y_Colaborativo'
                WHEN mt.ilicode = 'Mixto' THEN 'Mixto' ELSE ''
            END "MÉTODO DE LEVANTAMIENTO",
            ROUND((ST_Area(ST_Transform(ct.geometria, 9377))::numeric), 2) AS "ÁREA_LEVANTAMIENTO",
            REPLACE(TO_CHAR(ROUND((ST_Area(ST_Transform(ct.geometria, 9377))::numeric),2), '9999999999D99'), '.', ',') AS "ÁREA_LEVANTAMIENTO_COMA",
            UPPER(ce.nombre_predio) AS "NOMBRE PREDIO",
            cdet.ilicode AS "DESTINO ECONÓMICO",
            CASE 
                WHEN cp.t_id > 0 THEN 
                CASE 
                    WHEN (SELECT COUNT(*) FROM {esquema_seleccionado}.cca_caracteristicasunidadconstruccion cc WHERE cc.predio = cp.t_id) > 0 THEN 'SI' ELSE 'NO'
                END
            END "¿TIENE CONSTRUCCIONES?",
            CASE 
                WHEN cp.t_id > 0 THEN 
                CASE 
                    WHEN (SELECT COUNT(*) FROM {esquema_seleccionado}.cca_caracteristicasunidadconstruccion cc WHERE cc.predio = cp.t_id) = 0 THEN NULL ELSE 
                    (SELECT COUNT(*) FROM {esquema_seleccionado}.cca_caracteristicasunidadconstruccion cc WHERE cc.predio = cp.t_id)
                END    
            END "¿CANTIDAD CONSTRUCCIONES?",
            CASE 
                WHEN cp.t_id > 0 THEN 
                CASE 
                    WHEN (SELECT COUNT(*) FROM {esquema_seleccionado}.cca_caracteristicasunidadconstruccion cc WHERE cc.predio = cp.t_id) > 0 THEN 
                    (SELECT SUM(cu.area_construida) FROM {esquema_seleccionado}.cca_unidadconstruccion cu JOIN {esquema_seleccionado}.cca_caracteristicasunidadconstruccion cca ON cca.t_id  = cu.caracteristicasunidadconstruccion WHERE cca.predio = cp.t_id) ELSE NULL  
                END
            END "¿ÁREA TOTAL CONSTRUIDA (m2)",
            CASE 
                WHEN cp.t_id > 0 THEN 
                CASE 
                    WHEN (SELECT COUNT(*) FROM {esquema_seleccionado}.cca_caracteristicasunidadconstruccion cc WHERE cc.predio = cp.t_id) > 0 THEN 
                    (SELECT REPLACE(REPLACE(TO_CHAR(ROUND(SUM(ST_Area(ST_Transform(cu.geometria, 9377))::numeric), 2), '9999999999D99'), '.', ','), ' ', '') FROM {esquema_seleccionado}.cca_unidadconstruccion cu JOIN {esquema_seleccionado}.cca_caracteristicasunidadconstruccion cca ON cca.t_id  = cu.caracteristicasunidadconstruccion WHERE cca.predio = cp.t_id) ELSE NULL  
                END
            END "¿ÁREA TOTAL CONST (Recalculo area PG CONST(m2)", 
            cp.departamento AS "DEPARTAMENTO",
            cp.municipio AS "MUNICIPIO",
            cp.vereda AS "VEREDA",
            cp.numero_predial AS "NUMERO PREDIAL VIGENTE",
            CASE 
                WHEN cdt.ilicode = 'Dominio' THEN 'Formal' ELSE 'Informal'
            END "PREDIO (FORMAL INFORMAL)",
            CASE 
                WHEN cdt.ilicode = 'Posesion' THEN 'PRIVADO'
                WHEN cdt.ilicode = 'Ocupacion' THEN 'PUBLICO'
                WHEN cdt.ilicode = 'Dominio' THEN NULL  
            END "NATURALEZA PREDIO", 
            cdt.ilicode  AS "TIPO DERECHO",
            ccp.ilicode AS "CONDICIÓN PREDIO",
            CASE 
                WHEN cp.matricula_inmobiliaria IS NOT NULL AND cp.matricula_inmobiliaria <> '' THEN 'SI' ELSE 'NO'
            END "¿RELACIONA FMI?", 
            cp.codigo_orip AS "CIRCULO REGISTRAL", 
            cp.matricula_inmobiliaria AS "NÚMERO FMI",
            cfat.ilicode AS "TIPO FUENTE ADMINISTRATIVA (tipo de documento o acto jurídico de relación de tenencia)", 
            cfa.ente_emisor AS "ENTE EMISOR FUENTE ADMINISTRATIVA",
            cfa.numero_fuente AS "NUMERO FUENTE ADMINISTRATIVA",
            cfa.fecha_documento_fuente  AS "FECHA FUENTE ADMINISTRATIVA"
        FROM {esquema_seleccionado}.cca_predio cp 
        JOIN {esquema_seleccionado}.cca_metodointervenciontipo mt ON cp.metodointervencion = mt.t_id
        JOIN {esquema_seleccionado}.cca_terreno ct ON cp.terreno = ct.t_id 
        JOIN {esquema_seleccionado}.cca_extdireccion ce ON cp.t_id = ce.cca_predio_direccion
        JOIN {esquema_seleccionado}.cca_derecho cd ON cp.t_id = cd.predio 
        JOIN {esquema_seleccionado}.cca_derechotipo cdt ON cd.tipo  = cdt.t_id 
        JOIN {esquema_seleccionado}.cca_condicionprediotipo ccp ON cp.condicion_predio = ccp.t_id 
        JOIN {esquema_seleccionado}.cca_fuenteadministrativa cfa ON cd.t_id = cfa.derecho 
        JOIN {esquema_seleccionado}.cca_fuenteadministrativatipo cfat ON cfa.tipo = cfat.t_id 
        JOIN {esquema_seleccionado}.cca_destinacioneconomicatipo cdet ON cp.destinacion_economica = cdet.t_id
        """,
        
        'HOJA_2_INTERESADOS': f"""
        SELECT 
            cp.qr_operacion_definitivo AS "QR_DERIVADO(ID_OPERACION)",
            cit.ilicode AS "INTERESADO_TIPO",
            cid.ilicode AS "DOCUMENTO_TIPO",
            CASE
                WHEN cid.ilicode = 'NIT' THEN upper(ci.razon_social)
                ELSE upper(ci.primer_nombre)
            END AS "PRIMER_NOMBRE",
            upper(ci.segundo_nombre) AS "SEGUNDO_NOMBRE", 
            upper(ci.primer_apellido) AS "PRIMER_APELLIDO", 
            upper(ci.segundo_apellido) AS "SEGUNDO_APELLIDO", 
            ci.documento_identidad AS "DOCUMENTO",
            CASE 
                WHEN ci.interesado_jefe_hogar = true THEN 'SI'
                WHEN ci.interesado_jefe_hogar = false THEN 'NO'
                WHEN ci.interesado_jefe_hogar IS NULL THEN ''
            END AS "¿EL INTERESADO ES JEFE DE HOGAR?", 
            CASE 
                WHEN ci.interesado_victima_conflicto = true THEN 'SI'
                WHEN ci.interesado_victima_conflicto = false THEN 'NO'
                WHEN ci.interesado_victima_conflicto IS NULL THEN ''
            END AS "¿ES VICTIMA CONFLICTO ARMADO?", 
            cect.ilicode AS "ESTADO CIVIL", 
            TO_CHAR(cd.fecha_inicio_tenencia,'DD/MM/YYYY') AS "FECHA INICIO DE TENENCIA DEL PREDIO",
            CASE 
                WHEN ci.reside_predio = true THEN 'SI'
                WHEN ci.reside_predio = false THEN 'NO'
                WHEN ci.reside_predio IS NULL THEN ''
            END AS "¿EL INTERESADO RESIDE EN EL PREDIO?", 
            CASE 
                WHEN ci.reside_predio = true THEN 'NO'
                WHEN ci.reside_predio = false THEN 'SI'
                WHEN ci.reside_predio IS NULL THEN ''
            END AS "¿RESIDE PERSONA DISTINTA AL SOLICITANTE?", 
            ci.quien_reside AS "¿QUIEN?",
            CASE 
                WHEN cp.solicitante_explota = true THEN 'SI'
                WHEN cp.solicitante_explota = false THEN 'NO'
                WHEN cp.solicitante_explota IS NULL THEN ''
            END AS "¿EL INTERESADO EXPLOTA EL PREDIO DIRECTAMENTE?"
        FROM {esquema_seleccionado}.cca_predio cp 
        JOIN {esquema_seleccionado}.cca_derecho cd ON cp.t_id = cd.predio 
        JOIN {esquema_seleccionado}.cca_interesado ci ON cd.t_id = ci.derecho 
        JOIN {esquema_seleccionado}.cca_interesadotipo cit ON ci.tipo = cit.t_id 
        JOIN {esquema_seleccionado}.cca_interesadodocumentotipo cid ON ci.tipo_documento = cid.t_id 
        LEFT JOIN {esquema_seleccionado}.cca_estadociviltipo cect ON ci.estado_civil = cect.t_id
        """
    }
    
    dataframes = {}
    for sheet_name, query in queries.items():
        dataframes[sheet_name] = pd.read_sql_query(query, conexion)
    
    return dataframes

