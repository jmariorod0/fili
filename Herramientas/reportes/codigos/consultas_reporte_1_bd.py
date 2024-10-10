# consultas_reporte_observaciones.py

consultas_reporte_1_bd = [
    """

    --- 2.1 - La cantidad de registros en terrreno, cca_predio y cca_derecho debe ser igual
    WITH 
        terreno_total_registros AS (SELECT COUNT(*) AS count FROM cca_terreno),
        predio_total_registros AS (SELECT COUNT(*) AS count FROM cca_predio),
        derecho_total_registros AS (SELECT COUNT(*) AS count FROM cca_derecho),
        union_total_registros AS (
        SELECT 
            (SELECT count FROM terreno_total_registros) AS terreno_total_registros,
            (SELECT count FROM predio_total_registros) AS predio_total_registros,
            (SELECT count FROM derecho_total_registros) AS derecho_total_registros)
        SELECT 
            terreno_total_registros, 
            predio_total_registros, 
            derecho_total_registros,
            CASE 
                WHEN terreno_total_registros = predio_total_registros AND predio_total_registros = derecho_total_registros THEN 'IGUALES'
                ELSE 'VARIA'
            END AS validacion
        FROM union_total_registros
		WHERE NOT (terreno_total_registros = predio_total_registros AND predio_total_registros = derecho_total_registros);
    """,
    """
    ----2.3 - Los predios deben corresponder a la UIT, municipio, departamento de entrega a nivel alfanumerico según la tabla cca_predio y a nivel espacial
    
    SELECT uit, count(uit) as numero_registros, municipio, departamento
    from cca_predio 
    group by uit,municipio,departamento
    """,
    """
    --- 3.1 - No debe existir QR derivados repetidos
    
    select qr_operacion_definitivo, count(qr_operacion_definitivo) as repetidos 
    from CCA_Predio
    group by qr_operacion_definitivo
    HAVING count(qr_operacion_definitivo) > 1
    """,
    """
    --- 3.2. No debe existir t_ili_tid repetidos en cca_terreno
    
    select t_ili_tid, count(t_ili_tid) as repetidos 
    from cca_terreno
    group by t_ili_tid
    HAVING count(t_ili_tid) > 1
    """,
    """
    --- 3.3 - No debe existir t_ili_tid repetidos en cca_predio
    
    select qr_operacion_definitivo, t_ili_tid, count(t_ili_tid) as repetidos 
    from cca_Predio
    group by t_ili_tid, qr_operacion_definitivo
    HAVING count(t_ili_tid) > 1
    
    """,
    """
    --- 3.4 - No debe existir t_ili_tid repetidos en cca_derecho
    
    select t_ili_tid, count(t_ili_tid) as repetidos 
    from cca_derecho
    group by t_ili_tid
    HAVING count(t_ili_tid) > 1
    """,
    """
    --- 3.5 - No debe existir t_ili_tid repetidos en cca_interesados
    select t_ili_tid, count(t_ili_tid) as repetidos 
    from cca_interesado
    group by t_ili_tid
    HAVING count(t_ili_tid) > 1

    """,
    """

    ---3.6 - No debe existir t_ili_tid repetidos en cca_fuenteadministrativa

    select t_ili_tid, count(t_ili_tid) as repetidos 
    from cca_fuenteadministrativa
    group by t_ili_tid
    HAVING count(t_ili_tid) > 1

    """,
    
    """
    ---3.7 - No debe existir t_ili_tid repetidos en cca_caracteristicasunidadconstruccion
    select t_ili_tid, count(t_ili_tid) as repetidos 
    from cca_caracteristicasunidadconstruccion
    group by t_ili_tid
    HAVING count(t_ili_tid) > 1
    """,
    """
    ---3.8 - No debe existir t_ili_tid repetidos en cca_unidadconstruccion
    select t_ili_tid, count(t_ili_tid) as repetidos 
    from cca_unidadconstruccion
    group by t_ili_tid
    HAVING count(t_ili_tid) > 1

    """,
    """
    -- 3.9 - No debe existir t_ili_tid repetidos en cca_puntoreferencia

    select t_ili_tid, count(t_ili_tid) as repetidos 
    from cca_puntoreferencia
    group by t_ili_tid
    HAVING count(t_ili_tid) > 1

    """,
    """
    --- 4.1 - Asociación adecuada de qr_operacion y qr_operacion_definitiva según condicion del predio
    
    SELECT 
    qr_operacion, 
    qr_operacion_definitivo, 
    cpt.ilicode as condicion_predio,
    case
        when qr_operacion = qr_operacion_definitivo and cpt.ilicode = 'NPH' then 'OK_FORMAL'
        when qr_operacion <> qr_operacion_definitivo and cpt.ilicode = 'Informal' then 'OK_INFORMAL'
        when qr_operacion = qr_operacion_definitivo and cpt.ilicode = 'Informal' then 'ERROR'
        when qr_operacion <> qr_operacion_definitivo and cpt.ilicode = 'NPH' then 'ERROR'
    end tipologia_bien
    from CCA_Predio pre
    join cca_condicionprediotipo cpt on pre.condicion_predio = cpt.t_id
    where  qr_operacion = qr_operacion_definitivo and cpt.ilicode = 'Informal' 
        or  qr_operacion <> qr_operacion_definitivo and cpt.ilicode = 'NPH'   

    """,
    """
    ----- 4.2 - Verificación de la condición del predio y tipo de derecho
    
    select pre.qr_operacion_definitivo, cpt.ilicode as "CONDICION DEL PREDIO",drt.ilicode as "DERECHO TIPO",
        CASE 
            WHEN cpt.ilicode = 'Informal' and drt.ilicode='Posesion' then 'OK'
            WHEN cpt.ilicode = 'Informal' and drt.ilicode='Ocupacion' then 'OK'
            WHEN cpt.ilicode = 'NPH' and drt.ilicode='Dominio' then 'OK'
            else 'VERIFICAR'
        end as "VALIDACION"	
    from cca_predio as pre
    join cca_condicionprediotipo cpt on pre.condicion_predio = cpt.t_id
    join cca_derecho der on pre.t_id=der.predio
    join cca_derechotipo drt on der.tipo=drt.t_id
    WHERE 
        (cpt.ilicode = 'Informal' AND drt.ilicode NOT IN ('Posesion', 'Ocupacion'))
        OR (cpt.ilicode = 'NPH' AND drt.ilicode NOT IN ('Dominio')) ;

       
    """,
    """
  
    ---5.1	Validación de fechas de visita predial y fecha de finalizado reconocedor

        --Si en la tabla de resultados salen fechas quiere decir que estan mal diligenciadas.
        
    SELECT pd.qr_operacion_definitivo, cpt.ilicode as condicion_predio,TO_CHAR(pd.fecha_visita_predial,'DD/MM/YYYY') AS FECHA_VISITA_PREDIAL, TO_CHAR(pd.fecha_finalizado_reconocedor,'DD/MM/YYYY') AS FECHA_FINALIZADO_RECONOCEDOR
    FROM cca_predio pd
    JOIN cca_condicionprediotipo cpt on pd.condicion_predio=cpt.t_id
    WHERE  fecha_visita_predial IS NULL OR  fecha_finalizado_reconocedor IS NULL
    OR fecha_visita_predial > now() OR fecha_finalizado_reconocedor > now()

       
    """,
    """
    -- 5.2 - validacion de fechas de inicio de tenencia

      
    SELECT  predio.qr_operacion_definitivo, cpt.ilicode as condicion_predio, TO_CHAR(dr.fecha_inicio_tenencia,'DD/MM/YYYY') as fecha_inicio_tenencia,
        case
            when (fecha_inicio_tenencia IS NULL OR  EXTRACT(YEAR FROM fecha_inicio_tenencia) < 1900) AND cpt.ilicode='NPH' then 'OK'
            when ((fecha_inicio_tenencia IS NULL OR fecha_inicio_tenencia > now() ) AND cpt.ilicode='Informal') OR fecha_inicio_tenencia > now() then 'VERIFICAR FECHA'
        end as validacion
        
        FROM cca_derecho dr
        join cca_predio predio on dr.predio=predio.t_id
        join cca_condicionprediotipo cpt on predio.condicion_predio=cpt.t_id
        WHERE ((fecha_inicio_tenencia IS NULL OR fecha_inicio_tenencia > now()) AND cpt.ilicode = 'Informal')
        OR fecha_inicio_tenencia > now();

    """,
    """

    -- 5.3 - validacion de fechas de nacimiento de los interesados

	SELECT predio.qr_operacion_definitivo, cpt.ilicode as condicion_predio, int.fecha_nacimiento, int.primer_nombre, int.segundo_nombre, int.primer_apellido, int.segundo_apellido,int.razon_social,'VERIFICAR FECHA' AS VALIDACION
	FROM cca_interesado int
	join cca_derecho dr on int.derecho =dr.t_id
	join cca_predio predio on dr.predio=predio.t_id
	join cca_condicionprediotipo cpt on predio.condicion_predio=cpt.t_id
	WHERE (fecha_nacimiento is NULL or 
	fecha_nacimiento > now()
    OR  EXTRACT(YEAR FROM fecha_nacimiento) < 1900) and cpt.ilicode='Informal'; 

    """,
    """
    ---5.4	Validacion fecha documento fuente administrativa

	select pre.qr_operacion_definitivo, fadt.ilicode as tipo_fuente_adm,fad.numero_fuente,fad.fecha_documento_fuente,cpt.ilicode as condicion_predio
	from cca_predio as pre
	join cca_condicionprediotipo cpt on pre.condicion_predio=cpt.t_id
	join cca_derecho der on pre.t_id=der.predio
	LEFT JOIN cca_fuenteadministrativa fad ON der.t_id = fad.derecho
	join cca_fuenteadministrativatipo fadt on fad.tipo=fadt.t_id
	where  fad.fecha_documento_fuente > now()
    
    """,
    """
    ---5.5	Validación del año de la construccion

	SELECT pd.qr_operacion_definitivo, cuc.anio_construccion
	FROM cca_caracteristicasunidadconstruccion cuc
	JOIN cca_predio pd ON cuc.predio=pd.t_id
	where  cuc.anio_construccion > EXTRACT(YEAR FROM NOW());    

    """,
    """
    -- ---5.6	fecha de documento debe ser anterior a la fecha de inicio de tenencia

    SELECT 
        pre.qr_operacion_definitivo, 
        cpt.ilicode AS condicion_predio,
        fadt.ilicode AS tipo_fuente_adm, 
        fad.numero_fuente, 
        TO_CHAR(fad.fecha_documento_fuente,'DD/MM/YYYY') as fecha_documento_fuente,
        TO_CHAR(dr.fecha_inicio_tenencia,'DD/MM/YYYY') AS fecha_inicio_tenencia,
        CASE
            WHEN fad.fecha_documento_fuente > dr.fecha_inicio_tenencia THEN 'FECHA DOCUMENTO > FECHA INICIO TENENCIA, REVISAR CON EL PAR JURÍDICO'
            ELSE 'FECHA CORRECTA'
        END AS validacion
    FROM 
        cca_predio AS pre
    JOIN 
        cca_condicionprediotipo cpt ON pre.condicion_predio = cpt.t_id
    JOIN 
        cca_derecho dr ON pre.t_id = dr.predio
    LEFT JOIN 
        cca_fuenteadministrativa fad ON dr.t_id = fad.derecho
    JOIN 
        cca_fuenteadministrativatipo fadt ON fad.tipo = fadt.t_id
    WHERE 
        fad.fecha_documento_fuente > dr.fecha_inicio_tenencia

    """,
    """
    -- ---6.1	Documento_publico (escritura, sentencia, acto adm) debe tener un valor en numero_fuente
    
    
    select pre.qr_operacion_definitivo, cpt.ilicode as condicion_predio,fadt.ilicode tipo_fuente_adm,fad.numero_fuente,fad.fecha_documento_fuente, 'VERIFICAR RESPECTO A MTJ SI DEBE TENER NUM FUENTE ' AS validacion
    from cca_predio as pre
    join cca_derecho der on pre.t_id=der.predio
    join cca_condicionprediotipo cpt on pre.condicion_predio=cpt.t_id
    LEFT JOIN cca_fuenteadministrativa fad ON der.t_id = fad.derecho
    join cca_fuenteadministrativatipo fadt on fad.tipo=fadt.t_id
    WHERE ((fadt.ilicode = 'Documento_Publico.Acto_Administrativo' OR fadt.ilicode = 'Documento_Publico.Sentencia_Judicial' OR fadt.ilicode = 'Documento_Publico.Escritura_Publica') AND fad.numero_fuente IS NULL)
    or ((fadt.ilicode = 'Documento_Publico.Acto_Administrativo' OR fadt.ilicode = 'Documento_Publico.Sentencia_Judicial' OR fadt.ilicode = 'Documento_Publico.Escritura_Publica') AND fad.numero_fuente ='')
    or ((fadt.ilicode = 'Documento_Publico.Acto_Administrativo' OR fadt.ilicode = 'Documento_Publico.Sentencia_Judicial' OR fadt.ilicode = 'Documento_Publico.Escritura_Publica') AND fad.numero_fuente ='nan')
    or ((fadt.ilicode = 'Documento_Publico.Acto_Administrativo' OR fadt.ilicode = 'Documento_Publico.Sentencia_Judicial' OR fadt.ilicode = 'Documento_Publico.Escritura_Publica') AND fad.numero_fuente ='NA')
        or ((fadt.ilicode = 'Documento_Publico.Acto_Administrativo' OR fadt.ilicode = 'Documento_Publico.Sentencia_Judicial' OR fadt.ilicode = 'Documento_Publico.Escritura_Publica') AND fad.numero_fuente ='N/A')
        or ((fadt.ilicode = 'Documento_Publico.Acto_Administrativo' OR fadt.ilicode = 'Documento_Publico.Sentencia_Judicial' OR fadt.ilicode = 'Documento_Publico.Escritura_Publica') AND fad.numero_fuente ='na')
        or ((fadt.ilicode = 'Documento_Publico.Acto_Administrativo' OR fadt.ilicode = 'Documento_Publico.Sentencia_Judicial' OR fadt.ilicode = 'Documento_Publico.Escritura_Publica') AND fad.numero_fuente ='n/a')
        
    
    """,
    """

    ---6.2	Si tipo fuente es documento.publico entonces fecha documento fuente debe contener un valor

    select pre.qr_operacion_definitivo, fadt.ilicode,fad.numero_fuente,fad.fecha_documento_fuente, 'DEBE TENER FECHA DEL DOCUMENTO FUENTE ADM, VERIFICAR' as valiacion
    from cca_predio as pre
    join cca_derecho der on pre.t_id=der.predio
    LEFT JOIN cca_fuenteadministrativa fad ON der.t_id = fad.derecho
    join cca_fuenteadministrativatipo fadt on fad.tipo=fadt.t_id
    WHERE (fadt.ilicode = 'Documento_Publico.Acto_Administrativo' OR fadt.ilicode = 'Documento_Publico.Sentencia_Judicial' OR fadt.ilicode = 'Documento_Publico.Escritura_Publica')
    AND fad.fecha_documento_fuente IS NULL;

    """,
    """
    ---7.1 
    SELECT 
        predio.qr_operacion_definitivo,
        COUNT(DISTINCT uc.t_id) AS "NUMERO DE UNIDADES DE CONSTRUCCION POR CARACTERISTICA",
        cc.t_id AS "ID CARACTERISTICAS",
        STRING_AGG(uc.descripcion, ': ') AS "descripcion UC",
        'CORREGIR, CARACTERISTICA CON MAS DE 1 POLIGONO DE UNIDAD DE CONSTRUCCION' AS OBS
    FROM 
        cca_unidadconstruccion uc
    JOIN 
        cca_caracteristicasunidadconstruccion cc ON uc.caracteristicasunidadconstruccion = cc.t_id
    JOIN 
        cca_predio predio ON cc.predio = predio.t_id
    GROUP BY 
        uc.caracteristicasunidadconstruccion,
        cc.t_id,
        predio.qr_operacion_definitivo
    HAVING 
        COUNT(DISTINCT uc.t_id) > 1;

    """,
    """
    ---7.2	Todo predio deber tener asociada su dirección

    SELECT 
        cca_predio.t_id AS predio_id, qr_operacion_definitivo,
        'CORREGIR, FALTA DIRECCION DEL PREDIO' AS OBS
    FROM 
        cca_predio
    LEFT JOIN 
        cca_extdireccion ON cca_predio.t_id = cca_extdireccion.cca_predio_direccion
    WHERE (cca_extdireccion.cca_predio_direccion IS NULL)   

    """,
    """
    ---7.3	Todo terreno debe tener asociada su tabla cca_predio

    SELECT 
        cca_terreno.t_id AS terreno_id, qr_operacion,
        'CORREGIR, FALTA LA TABLA PREDIO A LOS TERRENOS' AS OBS
    FROM 
        cca_terreno
    LEFT JOIN 
        cca_predio ON cca_terreno.t_id = cca_predio.terreno
    WHERE 
        cca_predio.terreno  IS NULL;

    """,
    """
    ---7.4	Todo registro de cca_predio debe tener su derecho

    SELECT 
        cca_predio.t_id AS predio_id, qr_operacion_definitivo,
        'CORREGIR, FALTA RELACION PREDIO - DERECHO' AS OBS
    FROM 
        cca_predio
    LEFT JOIN 
        cca_derecho ON cca_predio.t_id = cca_derecho.predio
    WHERE 
        cca_derecho.predio IS NULL;
    
    """,
    """
    ---7.5	Todo registro en cca_derecho debe tener su interesado

    SELECT 
        cca_derecho.t_id AS derecho_id, cca_predio.qr_operacion_definitivo,
        'CORREGIR, FALTA RELACION DERECHO INTERESADO' AS OBS
    FROM 
        cca_derecho
    LEFT JOIN 
        cca_interesado ON cca_derecho.t_id = cca_interesado.derecho
    LEFT JOIN 
        cca_predio ON cca_derecho.predio = cca_predio.t_id
    WHERE 
        cca_interesado.derecho IS NULL;
     
    """,
    """

    ---7.6	Todo registro en cca_derecho debe tener su fuente administrativa
    
    SELECT 
        cca_derecho.t_id AS derecho_id, cca_predio.qr_operacion_definitivo,
        'CORREGIR, FALTA RELACION DERECHO FUENTE ADMINISTRATIVA' AS OBS
    FROM 
        cca_derecho
    LEFT JOIN 
        cca_fuenteadministrativa ON cca_derecho.t_id = cca_fuenteadministrativa.derecho
    LEFT JOIN 
        cca_predio ON cca_derecho.predio = cca_predio.t_id
    WHERE 
        cca_fuenteadministrativa.derecho IS NULL;   

    """,
    """
    ---7.7	Toda caracteristica unidad de construccion debe tener  su poligono de unidad de construccion

    SELECT 
        CUC.t_id AS caracteristicas_uc_id, cca_predio.qr_operacion_definitivo,
        'CORREGIR, FALTA UNIDAD DE CONSTRUCCION(POLIGONO DE CONSTRUCCION)' AS OBS
    FROM 
        cca_caracteristicasunidadconstruccion AS CUC
    LEFT JOIN 
        cca_unidadconstruccion AS UC ON CUC.t_id = UC.caracteristicasunidadconstruccion
    LEFT JOIN 
        cca_predio ON CUC.predio = cca_predio.t_id
    WHERE 
        UC.caracteristicasunidadconstruccion IS NULL;
        
    """,
    """
    ---8.1	Si interesado es persona juridica entonces razon social no puede estar vacio

    SELECT 
        cca_derecho.t_id AS derecho_id, cca_predio.qr_operacion_definitivo, 
		cpt.ilicode as condicion_predio , cca_interesadotipo.ilicode as interesado_tipo,
		intdt.ilicode as documento_tipo,cca_interesado.documento_identidad,cca_interesado.razon_social,'VERIFICAR' as validacion
    
    FROM cca_derecho
    LEFT JOIN cca_interesado ON cca_derecho.t_id = cca_interesado.derecho
    LEFT JOIN cca_predio ON cca_derecho.predio = cca_predio.t_id
    LEFT JOIN cca_condicionprediotipo cpt on cca_predio.condicion_predio=cpt.t_id
    left join cca_interesadotipo on cca_interesado.tipo=cca_interesadotipo.t_id
    left join cca_interesadodocumentotipo intdt on cca_interesado.tipo_documento=intdt.t_id
    WHERE (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.razon_social IS NULL)
    or (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.razon_social='')
    or (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.razon_social ILIKE 'nan')
    or (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.razon_social ILIKE 'NA')
    or (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.razon_social ILIKE 'N/A')
    or (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.documento_identidad IS NULL)
    or (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.documento_identidad ='')
    or (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.documento_identidad ILIKE 'nan')
    or (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.documento_identidad ILIKE 'NA')
    or (cca_interesadotipo.ilicode = 'Persona_Juridica' AND cca_interesado.documento_identidad ILIKE 'N/A')

    """,
    """
    ---8.2	si interesado es persona juridica entonces tipo de documento debe ser NIT
    
    SELECT 
        cca_derecho.t_id AS derecho_id, cca_predio.qr_operacion_definitivo,
		cca_interesadotipo.ilicode as tipo_interesado,
		intdt.ilicode as documento_tipo,cca_interesado.razon_social,'PERSONA JURIDICA CON TIPO DOC DIFERENTE A NIT, AJUSTAR' as validacion
    
    FROM cca_derecho
    LEFT JOIN cca_interesado ON cca_derecho.t_id = cca_interesado.derecho
    LEFT JOIN cca_predio ON cca_derecho.predio = cca_predio.t_id
    left join cca_interesadotipo on cca_interesado.tipo=cca_interesadotipo.t_id
    left join cca_interesadodocumentotipo intdt on cca_interesado.tipo_documento=intdt.t_id
    WHERE (cca_interesadotipo.ilicode = 'Persona_Juridica' and intdt.ilicode <> 'NIT')
    
    """,
    """
    ---8.3	Si interesado es persona natural entonces primer nombre, numero documento, primer apellido no puede estar vacio o en blanco


    SELECT 
        cca_derecho.t_id AS derecho_id, cca_predio.qr_operacion_definitivo, cpt.ilicode as condicion_predio, cca_interesadotipo.ilicode as tipo_interesado,intdt.ilicode as tipo_documento,cca_interesado.documento_identidad,
        cca_interesado.primer_nombre, cca_interesado.primer_apellido, cca_interesado.fecha_nacimiento
    
    FROM cca_derecho
    LEFT JOIN cca_interesado ON cca_derecho.t_id = cca_interesado.derecho
    LEFT JOIN cca_predio ON cca_derecho.predio = cca_predio.t_id
    left join cca_interesadotipo on cca_interesado.tipo=cca_interesadotipo.t_id
    LEFT JOIN cca_condicionprediotipo cpt on cca_predio.condicion_predio=cpt.t_id
    left join cca_interesadodocumentotipo intdt on cca_interesado.tipo_documento=intdt.t_id
    WHERE ((cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.documento_identidad is null )
    or (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.documento_identidad ='' )
    or (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.documento_identidad ILIKE 'nan' )
    or (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.documento_identidad ILIKE 'NA' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.primer_nombre is null )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.primer_nombre ILIKE 'nan' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.primer_nombre ='' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.primer_nombre ILIKE 'NA' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.primer_apellido is null )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.primer_apellido ='' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.primer_apellido ILIKE 'nan' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' AND cca_interesado.primer_apellido ILIKE 'NA' )) and cpt.ilicode ='Informal'



    """,
    """
    ---8.4	Si interesado es persona natural entonces tipo de documento NO puede ser NIT

    SELECT 
        cca_derecho.t_id AS derecho_id, cca_predio.qr_operacion_definitivo,cca_interesadotipo.ilicode as tipo_interesado,intdt.ilicode as tipo_documento,cca_interesado.documento_identidad,
        cca_interesado.primer_nombre, cca_interesado.primer_apellido, cca_interesado.fecha_nacimiento, 'PERSONA NATURAL CON NIT, AJUSTAR' as validacion
    
    FROM cca_derecho
    LEFT JOIN cca_interesado ON cca_derecho.t_id = cca_interesado.derecho
    LEFT JOIN cca_predio ON cca_derecho.predio = cca_predio.t_id
    left join cca_interesadotipo on cca_interesado.tipo=cca_interesadotipo.t_id
    left join cca_interesadodocumentotipo intdt on cca_interesado.tipo_documento=intdt.t_id
    WHERE (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode = 'NIT')

    """,
    """
    ---8.5	Si interesado es persona natural  y tipo documento  diferente a secuencial entonces fecha de nacimiento no debe estar vacia para las informalidades

    SELECT 
        cca_derecho.t_id AS derecho_id, cca_predio.qr_operacion_definitivo,cca_interesadotipo.ilicode as tipo_interesado,intdt.ilicode as tipo_documento,cca_interesado.documento_identidad,
        cca_interesado.primer_nombre, cca_interesado.primer_apellido, cpt.ilicode as condicion_predio, cca_interesado.fecha_nacimiento
    
    FROM cca_derecho
    LEFT JOIN cca_interesado ON cca_derecho.t_id = cca_interesado.derecho
    LEFT JOIN cca_predio ON cca_derecho.predio = cca_predio.t_id
    LEFt JOIN cca_condicionprediotipo cpt on cca_predio.condicion_predio=cpt.t_id
    left join cca_interesadotipo on cca_interesado.tipo=cca_interesadotipo.t_id
    left join cca_interesadodocumentotipo intdt on cca_interesado.tipo_documento=intdt.t_id
    WHERE (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' and cca_interesado.fecha_nacimiento is null )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.documento_identidad is null )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.documento_identidad ='' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.documento_identidad ILIKE 'nan' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.documento_identidad ILIKE 'NA' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.primer_nombre is null )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.primer_nombre ='' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.primer_nombre ='nan' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.primer_apellido is null )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.primer_apellido ='' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.primer_apellido ILIKE 'nan' )
    OR (cca_interesadotipo.ilicode = 'Persona_Natural' and intdt.ilicode <>'Secuencial' and cpt.ilicode ='Informal' AND cca_interesado.primer_apellido ILIKE 'NA' )

    """,
    """
    --- 8.6 Las informalidades y con ello los interesados no deberia tener secuenciales

    SELECT 
        cca_derecho.t_id AS derecho_id, cca_predio.qr_operacion_definitivo,cca_interesadotipo.ilicode as tipo_interesado,intdt.ilicode as tipo_documento,
        cpt.ilicode, cca_interesado.documento_identidad,
        cca_interesado.primer_nombre, cca_interesado.primer_apellido, cca_interesado.fecha_nacimiento, cca_interesado.razon_social, 'INTERESADO (POSIBLE SUJETO DE ORDENAMIENTO) CON SECUENCIAL, AJUSTAR' AS VALIDACION
    
    FROM cca_derecho
    LEFT JOIN cca_interesado ON cca_derecho.t_id = cca_interesado.derecho
    LEFT JOIN cca_predio ON cca_derecho.predio = cca_predio.t_id
    LEFt JOIN cca_condicionprediotipo cpt on cca_predio.condicion_predio=cpt.t_id
    left join cca_interesadotipo on cca_interesado.tipo=cca_interesadotipo.t_id
    left join cca_interesadodocumentotipo intdt on cca_interesado.tipo_documento=intdt.t_id
    WHERE  (intdt.ilicode = 'Secuencial' and cpt.ilicode='Informal')
	  
    """,
    """
        ------ 8.7 MISMO ID DIFERENTES NOMBRES   
    WITH diferencias_mismoid AS (
        SELECT documento_identidad
        FROM cca_interesado
        GROUP BY documento_identidad
        HAVING COUNT(*) > 1
    ),
    interesados_duplicados AS (
        SELECT 
            i.documento_identidad,
            idt.ilicode AS tipo_documento,
            cpt.ilicode as condicion_predio,
            CASE 
                WHEN idt.ilicode = 'NIT' THEN UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.razon_social, '\s+', '', 'g')), '[^A-Za-z]', '', 'g')))
                ELSE UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.primer_nombre, '\s+', '', 'g')), '[^A-Za-z]', '', 'g')))
            END AS primer_nombre,
            CASE 
                WHEN idt.ilicode = 'NIT' THEN NULL
                ELSE UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.segundo_nombre, '\s+', '', 'g')), '[^A-Za-z]', '', 'g')))
            END AS segundo_nombre,
            CASE 
                WHEN idt.ilicode = 'NIT' THEN NULL
                ELSE UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.primer_apellido, '\s+', '', 'g')), '[^A-Za-z]', '', 'g')))
            END AS primer_apellido,
            CASE 
                WHEN idt.ilicode = 'NIT' THEN NULL
                ELSE UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.segundo_apellido, '\s+', '', 'g')), '[^A-Za-z]', '', 'g')))
            END AS segundo_apellido,
            CASE 
                WHEN idt.ilicode = 'NIT' THEN UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.razon_social, '\s+', '', 'g')), '[^A-Za-z]', '', 'g')))
                ELSE CONCAT(
                    UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.primer_nombre, '\s+', '', 'g')), '[^A-Za-z]', '', 'g'))), ' ',
                    UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.segundo_nombre, '\s+', '', 'g')), '[^A-Za-z]', '', 'g'))), ' ',
                    UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.primer_apellido, '\s+', '', 'g')), '[^A-Za-z]', '', 'g'))), ' ',
                    UPPER(TRIM(REGEXP_REPLACE(unaccent(REGEXP_REPLACE(i.segundo_apellido, '\s+', '', 'g')), '[^A-Za-z]', '', 'g')))
                )
            END AS nombre_completo,
            pd.qr_operacion_definitivo
        FROM cca_interesado i
        JOIN cca_derecho dr ON i.derecho = dr.t_id
        JOIN cca_interesadodocumentotipo idt ON i.tipo_documento = idt.t_id
        JOIN cca_predio pd ON dr.predio = pd.t_id
        join cca_condicionprediotipo cpt on pd.condicion_predio = cpt.t_id
        WHERE i.documento_identidad IN (SELECT documento_identidad FROM diferencias_mismoid)
    )
    SELECT id.documento_identidad, id.tipo_documento, id.primer_nombre, id.segundo_nombre, id.primer_apellido, id.segundo_apellido, id.nombre_completo, id.qr_operacion_definitivo,id.condicion_predio,
        CASE 
            WHEN sub.tipo_doc_count > 1 THEN 'Diferentes tipos de documento'
            ELSE '' END || 
        CASE 
            WHEN sub.primer_nombre_count > 1 THEN ', ' || 'Variación en primer nombre'
            ELSE '' END || 
        CASE 
            WHEN sub.segundo_nombre_count > 1 THEN ', ' || 'Variación en segundo nombre'
            ELSE '' END || 
        CASE 
            WHEN sub.primer_apellido_count > 1 THEN ', ' || 'Variación en primer apellido'
            ELSE '' END || 
        CASE 
            WHEN sub.segundo_apellido_count > 1 THEN ', ' || 'Variación en segundo apellido'
            ELSE '' END AS diferencias
    FROM interesados_duplicados id
    JOIN 
        (SELECT 
            documento_identidad,
            COUNT(DISTINCT tipo_documento) AS tipo_doc_count,
            COUNT(DISTINCT primer_nombre) AS primer_nombre_count,
            COUNT(DISTINCT segundo_nombre) AS segundo_nombre_count,
            COUNT(DISTINCT primer_apellido) AS primer_apellido_count,
            COUNT(DISTINCT segundo_apellido) AS segundo_apellido_count
        FROM interesados_duplicados
        GROUP BY 
            documento_identidad
        HAVING 
            COUNT(DISTINCT tipo_documento) > 1 
            OR COUNT(DISTINCT primer_nombre) > 1 
            OR COUNT(DISTINCT segundo_nombre) > 1 
            OR COUNT(DISTINCT primer_apellido) > 1 
            OR COUNT(DISTINCT segundo_apellido) > 1
        ) sub
    ON 
        id.documento_identidad = sub.documento_identidad
    ORDER BY 
        id.documento_identidad, id.tipo_documento, id.nombre_completo;

    """,
    """
    --- 9.1	El tipo de unidad de construcción debe corresponder con sus respectivos dominios de Uso (ejemplo tipo residencial no puede tener usos de anexos)
    SELECT 
        cuc.identificador, 
        uct.ilicode AS tipo_unidad_cons, 
        usocons.ilicode AS uso_construccion, 
        pd.qr_operacion_definitivo, 'NO CORRESPONDE EL TIPO DE UNIDAD CON EL USO, AJUSTAR' AS VALIDACION
    FROM cca_caracteristicasunidadconstruccion cuc
    JOIN cca_predio pd ON cuc.predio = pd.t_id
    JOIN cca_unidadconstrucciontipo uct ON cuc.tipo_unidad_construccion = uct.t_id
    JOIN cca_usouconstipo usocons ON cuc.uso = usocons.t_id
    WHERE 
        (
            (uct.ilicode = 'Residencial' AND usocons.ilicode NOT IN (
                'Residencial.Apartamentos_4_y_mas_pisos_en_PH','Residencial.Apartamentos_Mas_De_4_Pisos','Residencial.Barracas','Residencial.Casa_Elbas','Residencial.Depositos_Lockers','Residencial.Garajes_Cubiertos','Residencial.Garajes_En_PH','Residencial.Salon_Comunal','Residencial.Secadero_Ropa','Residencial.Vivienda_Colonial','Residencial.Vivienda_Colonial_en_PH','Residencial.Vivienda_Hasta_3_Pisos', 'Residencial.Vivienda_Hasta_3_Pisos_En_PH', 'Residencial.Vivienda_Recreacional','Residencial.Vivienda_Recreacional_En_PH'
            ))
            OR
            (uct.ilicode = 'Anexo' AND usocons.ilicode NOT IN (
                'Anexo.Albercas_Banaderas','Anexo.Beneficiaderos','Anexo.Camaroneras','Anexo.Canchas','Anexo.Canchas_de_Tenis','Anexo.Carretera','Anexo.Cerramiento','Anexo.Cimientos_Estructura_Muros_y_Placa_Base','Anexo.Cocheras_Marraneras_Porquerizas','Anexo.Construccion_en_Membrana_Arquitectonica','Anexo.Contenedor','Anexo.Corrales','Anexo.Establos_Pesebreras_Caballerizas','Anexo.Estacion_Bombeo','Anexo.Estacion_Sistema_Transporte','Anexo.Galpones_Gallineros','Anexo.Glamping','Anexo.Hangar','Anexo.Kioscos','Anexo.Lagunas_de_Oxidacion','Anexo.Marquesinas_Patios_Cubiertos','Anexo.Muelles','Anexo.Murallas','Anexo.Pergolas','Anexo.Piscinas','Anexo.Pista_Aeropuerto','Anexo.Pozos','Anexo.Ramadas_Cobertizos_Caneyes','Anexo.Secaderos','Anexo.Silos','Anexo.Tanques','Anexo.Toboganes','Anexo.Torre_de_Control','Anexo.Torres_de_Enfriamiento','Anexo.Via_Ferrea'
            ))
            OR
            (uct.ilicode = 'Comercial' AND usocons.ilicode NOT IN (
                'Comercial.Bodegas_Comerciales_Grandes_Almacenes','Comercial.Bodegas_Comerciales_en_PH','Comercial.Centros_Comerciales','Comercial.Centros_Comerciales_en_PH','Comercial.Clubes_Casinos','Comercial.Comercio','Comercial.Comercio_Colonial','Comercial.Comercio_en_PH','Comercial.Hotel_Colonial','Comercial.Hoteles','Comercial.Hoteles_en_PH','Comercial.Oficinas_Consultorios','Comercial.Oficinas_Consultorios_Coloniales','Comercial.Oficinas_Consultorios_en_PH','Comercial.Parque_Diversiones','Comercial.Parqueaderos','Comercial.Parqueaderos_en_PH','Comercial.Pensiones_y_Residencias','Comercial.Plaza_Mercado','Comercial.Restaurante_Colonial','Comercial.Restaurantes','Comercial.Restaurantes_en_PH','Comercial.Teatro_Cinemas','Comercial.Teatro_Cinemas_en_PH'
            ))
            OR
            (uct.ilicode = 'Institucional' AND usocons.ilicode NOT IN (
                'Institucional.Aulas_de_Clases','Institucional.Biblioteca','Institucional.Carceles','Institucional.Casas_de_Culto','Institucional.Clinicas_Hospitales_Centros_Medicos','Institucional.Colegio_y_Universidades','Institucional.Coliseos','Institucional.Entidad_Educativa_Colonial_Colegio_Colonial','Institucional.Estadios','Institucional.Fuertes_y_Castillos','Institucional.Iglesia','Institucional.Iglesia_en_PH','Institucional.Instalaciones_Militares','Institucional.Jardin_Infantil_en_Casa','Institucional.Parque_Cementerio','Institucional.Planetario','Institucional.Plaza_de_Toros','Institucional.Puestos_de_Salud','Institucional.Museos','Institucional.Seminarios_Conventos','Institucional.Teatro','Institucional.Unidad_Deportiva','Institucional.Velodromo_Patinodromo'
            ))
            OR
            (uct.ilicode = 'Industrial' AND usocons.ilicode NOT IN (
                'Industrial.Bodega_Casa_Bomba','Industrial.Bodegas_Casa_Bomba_en_PH','Industrial.Industrias','Industrial.Industrias_en_PH','Industrial.Talleres'
            ))
        );
        
        
    """,
    """
    --- 9.2	Si la construccion es convencional (diferente a anexos) debe tener diligenciado  estrato, estructura armazon, acabados, cercha, cubierta, urbanizacion
    
    SELECT 
        uct.ilicode AS tipo_unidad_cons, 
        usocons.ilicode AS uso_construccion, 
        pd.qr_operacion_definitivo,
        CONCAT_WS(', ',
            CASE 
                WHEN uct.ilicode IN ('Residencial', 'Comercial', 'Industrial', 'Institucional') AND cuc.estrato_tipo IS NULL THEN 'FALTA DILIGENCIAR ESTRATO'
                ELSE NULL
            END,
            CASE 
                WHEN uct.ilicode IN ('Residencial', 'Comercial', 'Industrial', 'Institucional') AND cuc.estructura_armazon IS NULL THEN 'FALTA DILIGENCIAR ESTRUCTURA_ARMANON'
                ELSE NULL
            END,
            CASE 
                WHEN uct.ilicode IN ('Residencial', 'Comercial', 'Industrial', 'Institucional') AND cuc.acabados IS NULL THEN 'FALTA DILIGENCIAR ACABADOS'
                ELSE NULL
            END,
            CASE 
                WHEN uct.ilicode IN ('Residencial', 'Comercial', 'Industrial', 'Institucional') AND cuc.cercha IS NULL THEN 'FALTA DILIGENCIAR CERCHA'
                ELSE NULL
            END,
            CASE 
                WHEN uct.ilicode IN ('Residencial', 'Comercial', 'Industrial', 'Institucional') AND cuc.cubierta IS NULL THEN 'FALTA DILIGENCIAR CUBIERTA'
                ELSE NULL
            END,
            CASE 
                WHEN uct.ilicode IN ('Residencial', 'Comercial', 'Industrial', 'Institucional') AND cuc.uso IS NULL THEN 'FALTA DILIGENCIAR USO'
                ELSE NULL
            END,			  
            CASE 
                WHEN uct.ilicode IN ('Residencial', 'Comercial', 'Industrial', 'Institucional') AND cuc.urbanizacion IS NULL THEN 'FALTA DILIGENCIAR URBANIZACION(SI/NO)'
                ELSE NULL
            END
        ) AS validacion
    FROM cca_caracteristicasunidadconstruccion cuc
    JOIN cca_predio pd ON cuc.predio = pd.t_id
    LEFT JOIN cca_unidadconstrucciontipo uct ON cuc.tipo_unidad_construccion = uct.t_id
    LEFT JOIN cca_usouconstipo usocons ON cuc.uso = usocons.t_id
    WHERE 
        uct.ilicode IN ('Residencial', 'Comercial', 'Industrial', 'Institucional') AND (
        cuc.estrato_tipo IS NULL OR
        cuc.estructura_armazon IS NULL OR
        cuc.acabados IS NULL OR
        cuc.cercha IS NULL OR
        cuc.cubierta IS NULL OR
        cuc.uso IS NULL OR
        cuc.urbanizacion IS NULL
        )
    GROUP BY 
        uct.ilicode, 
        usocons.ilicode, 
        pd.qr_operacion_definitivo,cuc.estrato_tipo,  cuc.estructura_armazon,cuc.cercha, cuc.cubierta,cuc.urbanizacion,cuc.acabados,cuc.uso ;   
    
    
    """,
    """
    ---9.3	Si el tipo de unidad es no convencional (Anexo)
    
    SELECT pd.qr_operacion_definitivo, uct.ilicode as tipo_unidad_construccion, usocons.ilicode as uso, ant.ilicode as tipo_anexo, 'VERIFICAR TIPOS Y USOS' AS VALIDACION

    FROM cca_caracteristicasunidadconstruccion cuc
    JOIN cca_predio pd ON cuc.predio = pd.t_id
    LEFT JOIN cca_unidadconstrucciontipo uct ON cuc.tipo_unidad_construccion =uct.t_id
    LEFT JOIN cca_anexotipo ant on cuc.tipo_anexo=ant.t_id
    LEFT JOIN cca_usouconstipo usocons ON cuc.uso = usocons.t_id
    where uct.ilicode='Anexo' AND  ant.ilicode is NULL
    OR ((usocons.ilicode = 'Anexo.Beneficiaderos' AND ant.ilicode NOT IN ('Beneficiaderos.Tipo_80', 'Beneficiaderos.Tipo_60', 'Beneficiaderos.Tipo_40')))
    OR ((usocons.ilicode = 'Anexo.Albercas_Banaderas' AND ant.ilicode NOT IN ('Albercas_Baniaderas.Tipo_80','Albercas_Baniaderas.Tipo_60','Albercas_Baniaderas.Tipo_40')))
    OR ((usocons.ilicode = 'Anexo.Canchas_de_Tenis' AND ant.ilicode NOT IN ('CanchasTenis.Tipo_20', 'CanchasTenis.Tipo_10')))
    OR (( usocons.ilicode ='Anexo.Carretera' AND ant.ilicode NOT IN ('Carreteras.Tipo_40','Carreteras.Tipo_60')))
    OR (( usocons.ilicode ='Anexo.Cimientos_Estructura_Muros_y_Placa_Base' AND ant.ilicode NOT IN ('Cimientos_Estructura_Muros_Placabase.Tipo_20','Cimientos_Estructura_Muros_Placabase.Tipo_40','Cimientos_Estructura_Muros_Placabase.Tipo_60','Cimientos_Estructura_Muros_Placabase.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Cocheras_Marraneras_Porquerizas' AND ant.ilicode NOT IN ('Cocheras_Marraneras_Porquerizas.Tipo_20','Cocheras_Marraneras_Porquerizas.Tipo_40','Cocheras_Marraneras_Porquerizas.Tipo_60','Cocheras_Marraneras_Porquerizas.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Corrales' AND ant.ilicode NOT IN ('Corrales.Tipo_20','Corrales.Tipo_40','Corrales.Tipo_60','Corrales.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Establos_Pesebreras_Caballerizas' AND ant.ilicode NOT IN ('Establos_Pesebreras.Tipo_20','Establos_Pesebreras.Tipo_40','Establos_Pesebreras.Tipo_60','Establos_Pesebreras.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Galpones_Gallineros' AND ant.ilicode NOT IN ('Galpones_Gallineros.Tipo_20','Galpones_Gallineros.Tipo_40','Galpones_Gallineros.Tipo_60','Galpones_Gallineros.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Kioscos' AND ant.ilicode NOT IN ('Kioscos.Tipo_20','Kioscos.Tipo_40','Kioscos.Tipo_60','Kioscos.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Lagunas_de_Oxidacion' AND ant.ilicode NOT IN ('Lagunas_de_Oxidacion.Tipo_20')))
    OR (( usocons.ilicode ='Anexo.Marquesinas_Patios_Cubiertos' AND ant.ilicode NOT IN ('Marquesinas_Patios_Cubiertos.Tipo_20','Marquesinas_Patios_Cubiertos.Tipo_40','Marquesinas_Patios_Cubiertos.Tipo_60','Marquesinas_Patios_Cubiertos.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Muelles' AND ant.ilicode NOT IN ('Muelles.Tipo_40','Muelles.Tipo_60','Muelles.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Piscinas' AND ant.ilicode NOT IN ('Piscinas.Tipo_40','Piscinas.Tipo_50','Piscinas.Tipo_60','Piscinas.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Pozos' AND ant.ilicode NOT IN ('Pozos.Tipo_40','Pozos.Tipo_60','Pozos.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Ramadas_Cobertizos_Caneyes' AND ant.ilicode NOT IN ('Enramadas_Cobertizos_Caneyes.Tipo_40','Enramadas_Cobertizos_Caneyes.Tipo_60','Enramadas_Cobertizos_Caneyes.Tipo_80','Enramadas_Cobertizos_Caneyes.Tipo_90')))
    OR (( usocons.ilicode ='Anexo.Secaderos' AND ant.ilicode NOT IN ('Secaderos.Tipo_40','Secaderos.Tipo_60','Secaderos.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Silos' AND ant.ilicode NOT IN ('Silos.Tipo_60','Silos.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Tanques' AND ant.ilicode NOT IN ('Tanques.Tipo_40','Tanques.Tipo_50','Tanques.Tipo_60','Tanques.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Toboganes' AND ant.ilicode NOT IN ('Toboganes.Tipo_40','Toboganes.Tipo_50','Toboganes.Tipo_60','Toboganes.Tipo_80')))
    OR (( usocons.ilicode ='Anexo.Torres_de_Enfriamiento' AND ant.ilicode NOT IN ('TorresEnfriamiento')))
    OR (( usocons.ilicode ='Anexo.Via_Ferrea' AND ant.ilicode NOT IN ('Via_Ferrea.Tipo_60','Via_Ferrea.Tipo_80')))   
    
    """,
    """
    ---9.4	toda caracteristica de unidad de construccion debe tener diligenciado la conservacion de la tipologia y año de la construccion 

    SELECT pd.qr_operacion_definitivo, cpt.ilicode as condicion_predio, ect.ilicode as conservacion_tipologia, cuc.anio_construccion,'COMPLETAR INFORMACION' as VALIDACION

    FROM cca_caracteristicasunidadconstruccion cuc
    left JOIN cca_predio pd ON cuc.predio = pd.t_id
    left join cca_condicionprediotipo cpt ON pd.condicion_predio=cpt.t_id
    LEFT JOIN cca_estadoconservaciontipo ect ON cuc.conservacion_tipologia=ect.t_id
    where  cuc.conservacion_tipologia IS NULL
    OR  cuc.anio_construccion IS NULL

    """,
    """
    --- 9.5	Los identificadores de las construcciones deben estar entre A-Z por ende no puede tener identificadores numéricos

    SELECT pd.qr_operacion_definitivo, cuc.identificador,'NO DEBERÍA SER NUMERICO' as VALIDACION

    FROM cca_caracteristicasunidadconstruccion cuc
    left JOIN cca_predio pd ON cuc.predio = pd.t_id
    WHERE cuc.identificador NOT SIMILAR TO '%[A-Za-z]%'
    GROUP BY pd.qr_operacion_definitivo, cuc.identificador
    """,
    """
    ---9.6 - Si existe mas de 1 caracteristica de unidad construccion entonces los identificadores deben relacionarse en orden alfabetico y no deben repetirse
    
    WITH Identificadores_Ordenados AS (
        SELECT 
            pd.qr_operacion_definitivo, 
            STRING_AGG(UPPER(cuc.identificador::text), ', ' ORDER BY UPPER(cuc.identificador)) AS identificadores,
            ARRAY_AGG(UPPER(cuc.identificador) ORDER BY UPPER(cuc.identificador)) AS identificadores_array
        FROM 
            cca_caracteristicasunidadconstruccion cuc
        LEFT JOIN 
            cca_predio pd ON cuc.predio = pd.t_id
        GROUP BY 
            pd.qr_operacion_definitivo
    ),
    Secuencia_Validada AS (
        SELECT
            io.qr_operacion_definitivo,
            io.identificadores,
            io.identificadores_array,
            CASE 
                WHEN (
                    SELECT bool_and(
                        id_next IS NULL 
                        OR ASCII(id_next) = ASCII(id) + 1
                    )
                    FROM (
                        SELECT 
                            id, 
                            LEAD(id) OVER (ORDER BY ord) AS id_next
                        FROM unnest(io.identificadores_array) WITH ORDINALITY AS t(id, ord)
                    ) sub
                ) THEN 'CORRECTO'
                ELSE 'ORDEN NO SECUENCIAL- AJUSTAR'
            END AS validacion
        FROM 
            Identificadores_Ordenados io
    )
    SELECT * FROM Secuencia_Validada
    WHERE validacion = 'ORDEN NO SECUENCIAL- AJUSTAR';    
    
    
    """,


    """


    --- 10 datos por diligenciar

    SELECT
        pd.qr_operacion,
        pd.qr_operacion_definitivo,
        cpt.ilicode as condicion_predio,

        -- Usamos STRING_AGG para concatenar los campos faltantes en una sola fila
        STRING_AGG(
            CONCAT_WS(', ',
                CASE WHEN pd.departamento IS NULL OR TRIM(pd.departamento) = '' THEN 'departamento' END,
                CASE WHEN pd.municipio IS NULL OR TRIM(pd.municipio) = '' THEN 'municipio' END,
                CASE WHEN pd.uit IS NULL OR TRIM(pd.uit::text) = '' THEN 'uit' END,
                CASE WHEN pd.vereda IS NULL OR TRIM(pd.vereda) = '' THEN 'vereda' END,
                CASE WHEN pd.numero_predial IS NULL OR TRIM(pd.numero_predial::text) = '' THEN 'numero_predial' END,
                CASE WHEN pd.condicion_predio IS NULL THEN 'condicion_predio' END,
                CASE WHEN pd.destinacion_economica IS NULL THEN 'destinacion_economica' END,
                CASE WHEN pd.resultado_visita IS NULL THEN 'resultado_visita' END,
                CASE WHEN pd.fecha_visita_predial IS NULL THEN 'fecha_visita_predial' END,
                CASE WHEN pd.historia_predio IS NULL OR TRIM(pd.historia_predio) = '' THEN 'historia_predio' END,
                CASE WHEN pd.no_personas_habitan_predio IS NULL THEN 'no_personas_habitan_predio' END,
                CASE WHEN pd.ninos_ninas_adolesc IS NULL THEN 'ninos_ninas_adolesc' END,
                CASE WHEN pd.personas_tercera_edad IS NULL THEN 'personas_tercera_edad' END,
                CASE WHEN pd.mujeres_adultas IS NULL THEN 'mujeres_adultas' END,
                CASE WHEN pd.jefatura IS NULL THEN 'jefatura' END,
                CASE WHEN pd.personas_discapacidad IS NULL THEN 'personas_discapacidad' END,
                CASE WHEN pd.personas_campesinos IS NULL THEN 'personas_campesinos' END,
                CASE WHEN pd.identidad_etnica IS NULL THEN 'identidad_etnica' END,
                CASE WHEN pd.pretension_colectiva IS NULL THEN 'pretension_colectiva' END,
                CASE WHEN pd.metodointervencion IS NULL THEN 'metodointervencion' END,
                CASE WHEN pd.fecha_finalizado_reconocedor IS NULL THEN 'fecha_finalizado_reconocedor' END,
                CASE WHEN pd.solicitante_explota IS NULL THEN 'solicitante_explota' END,
                CASE WHEN der.tipo IS NULL THEN 'tipo_derecho' END,
                CASE WHEN der.fecha_inicio_tenencia IS NULL THEN 'fecha_inicio_tenencia' END,
                CASE WHEN inter.tipo IS NULL THEN 'tipo_interesado' END,
                CASE WHEN inter.tipo_documento IS NULL THEN 'tipo_documento' END,
                CASE WHEN inter.documento_identidad IS NULL OR TRIM(inter.documento_identidad::text) = '' THEN 'documento_identidad' END,
                CASE WHEN inter.grupo_etnico IS NULL THEN 'grupo_etnico' END,
                CASE WHEN inter.interesado_jefe_hogar IS NULL THEN 'interesado_jefe_hogar' END,
                CASE WHEN inter.acepta_ospr IS NULL THEN 'acepta_ospr' END,
                CASE WHEN inter.declaracion_informacion_veridica IS NULL THEN 'declaracion_informacion_veridica' END,
                CASE 
                    WHEN fadt.ilicode <> 'Sin_Documento' AND (fad.tipo IS NULL) THEN 'tipo_fuenteadm'
                END,
                CASE 
                    WHEN fadt.ilicode <> 'Sin_Documento' AND (fad.ente_emisor IS NULL OR TRIM(fad.ente_emisor) = '') THEN 'ente_emisor'
                END
            ), ', '
        ) AS "POR_DILIGENCIAR"

    FROM
        cca_terreno ter 
    JOIN cca_predio pd ON ter.t_id = pd.terreno
    JOIN cca_condicionprediotipo cpt ON pd.condicion_predio = cpt.t_id
    JOIN cca_derecho der ON pd.t_id = der.predio
    JOIN cca_interesado inter ON der.t_id = inter.derecho
    JOIN cca_fuenteadministrativa fad ON der.t_id = fad.derecho
    JOIN cca_fuenteadministrativatipo fadt ON fad.tipo = fadt.t_id

    -- Filtro para mostrar solo los registros con datos por diligenciar
    WHERE 
        LENGTH(CONCAT_WS(', ',
            CASE WHEN pd.departamento IS NULL OR TRIM(pd.departamento) = '' THEN 'departamento' END,
            CASE WHEN pd.municipio IS NULL OR TRIM(pd.municipio) = '' THEN 'municipio' END,
            CASE WHEN pd.uit IS NULL OR TRIM(pd.uit::text) = '' THEN 'uit' END,
            CASE WHEN pd.vereda IS NULL OR TRIM(pd.vereda) = '' THEN 'vereda' END,
            CASE WHEN pd.numero_predial IS NULL OR TRIM(pd.numero_predial::text) = '' THEN 'numero_predial' END,
            CASE WHEN pd.condicion_predio IS NULL THEN 'condicion_predio' END,
            CASE WHEN pd.destinacion_economica IS NULL THEN 'destinacion_economica' END,
            CASE WHEN pd.resultado_visita IS NULL THEN 'resultado_visita' END,
            CASE WHEN pd.fecha_visita_predial IS NULL THEN 'fecha_visita_predial' END,
            CASE WHEN pd.historia_predio IS NULL OR TRIM(pd.historia_predio) = '' THEN 'historia_predio' END,
            CASE WHEN pd.no_personas_habitan_predio IS NULL THEN 'no_personas_habitan_predio' END,
            CASE WHEN pd.ninos_ninas_adolesc IS NULL THEN 'ninos_ninas_adolesc' END,
            CASE WHEN pd.personas_tercera_edad IS NULL THEN 'personas_tercera_edad' END,
            CASE WHEN pd.mujeres_adultas IS NULL THEN 'mujeres_adultas' END,
            CASE WHEN pd.jefatura IS NULL THEN 'jefatura' END,
            CASE WHEN pd.personas_discapacidad IS NULL THEN 'personas_discapacidad' END,
            CASE WHEN pd.personas_campesinos IS NULL THEN 'personas_campesinos' END,
            CASE WHEN pd.identidad_etnica IS NULL THEN 'identidad_etnica' END,
            CASE WHEN pd.pretension_colectiva IS NULL THEN 'pretension_colectiva' END,
            CASE WHEN pd.metodointervencion IS NULL THEN 'metodointervencion' END,
            CASE WHEN pd.fecha_finalizado_reconocedor IS NULL THEN 'fecha_finalizado_reconocedor' END,
            CASE WHEN pd.solicitante_explota IS NULL THEN 'solicitante_explota' END,
            CASE WHEN der.tipo IS NULL THEN 'tipo_derecho' END,
            CASE WHEN der.fecha_inicio_tenencia IS NULL THEN 'fecha_inicio_tenencia' END,
            CASE WHEN inter.tipo IS NULL THEN 'tipo_interesado' END,
            CASE WHEN inter.tipo_documento IS NULL THEN 'tipo_documento' END,
            CASE WHEN inter.documento_identidad IS NULL OR TRIM(inter.documento_identidad::text) = '' THEN 'documento_identidad' END,
            CASE WHEN inter.grupo_etnico IS NULL THEN 'grupo_etnico' END,
            CASE WHEN inter.interesado_jefe_hogar IS NULL THEN 'interesado_jefe_hogar' END,
            CASE WHEN inter.acepta_ospr IS NULL THEN 'acepta_ospr' END,
            CASE WHEN inter.declaracion_informacion_veridica IS NULL THEN 'declaracion_informacion_veridica' END,
            CASE 
                WHEN fadt.ilicode <> 'Sin_Documento' AND (fad.tipo IS NULL) THEN 'tipo_fuenteadm'
            END,
            CASE 
                WHEN fadt.ilicode <> 'Sin_Documento' AND (fad.ente_emisor IS NULL OR TRIM(fad.ente_emisor) = '') THEN 'ente_emisor'
            END
        )) > 0  

    GROUP BY
        pd.qr_operacion, cpt.ilicode, pd.qr_operacion_definitivo;






    """,
    """
    ---11.1 No debe existir poligonos de construcciones multiparte o inválidas
    

    SELECT 
        t_id as "ID UNIDAD CONS",    
        CASE 
            WHEN ST_IsValid(geometria) THEN 'VÁLIDA'
            ELSE 'NO VÁLIDA'
        END AS "VAL GEOMETRIA",
        CASE 
            WHEN ST_NumGeometries(geometria) = 1 THEN 'NO ES MULTIPARTE'
            ELSE 'ES MULTIPARTE'
        END AS "VAL MULTIPARTE",
        geometria
    FROM 
        cca_unidadconstruccion 
    WHERE 
        NOT ST_IsValid(geometria) OR ST_NumGeometries(geometria) > 1;
        
    """,

   """

    SELECT 
        a.t_id as "ID UNIDAD CONS A", 
        b.t_id as "ID UNIDAD CONS B", 
        ST_Overlaps(a.geometria, b.geometria) as "SUPERPOSICIÓN",
        ST_Area(ST_Intersection(a.geometria, b.geometria)) as "AREA_SUPERPOSICION"
    FROM 
        cca_unidadconstruccion a,
        cca_unidadconstruccion b
    WHERE 
        a.t_id <> b.t_id  -- Para evitar comparar una geometría consigo misma
        AND ST_Overlaps(a.geometria, b.geometria) = TRUE; 



   """,



   """
    --- 11.2	Predios multiparte

    SELECT 
        pd.qr_operacion_definitivo ,cpt.ilicode,
        CASE 
            WHEN ST_IsValid(geometria) THEN 'VÁLIDA'
            ELSE 'NO VÁLIDA'
        END AS " GEOMETRIA VÁLIDA",
        CASE 
            WHEN ST_NumGeometries(geometria) = 1 THEN 'NO ES MULTIPARTE'
            ELSE 'ES MULTIPARTE'
        END AS "VAL MULTIPARTE",
		'EQUIPO DE VALIDACION VERIFICARÁ SI ES ADCUADA SU ESTRUCTURACIÓN' AS VALIDACION
      

    FROM 
        cca_terreno te
    join cca_predio pd on te.t_id=pd.terreno
    join cca_condicionprediotipo cpt on pd.condicion_predio =cpt.t_id
    WHERE NOT ST_IsValid(te.geometria) OR ST_NumGeometries(te.geometria) > 1
	ORDER by cpt.ilicode ASC;
    """,
    """
    --- 12.2 los predios formales no se pueden superponer entre si 

    WITH predios_formales AS (
        SELECT 
            ter.t_id as terreno_id, 
            ST_Simplify(ST_MakeValid(ter.geometria), 0.0001) as geometria,  
            pd.qr_operacion, 
            pd.qr_operacion_definitivo, 
            cpt.ilicode as condicion_predio
        FROM 
            cca_terreno ter
        JOIN 
            cca_predio pd ON ter.t_id = pd.terreno
        JOIN 
            cca_condicionprediotipo cpt ON pd.condicion_predio = cpt.t_id
        WHERE 
            cpt.ilicode = 'NPH'  
    )
    SELECT 
        a.terreno_id as "ID TERRENO A", 
        a.qr_operacion_definitivo as "QR OPERACION DEFINITIVO A",  
        b.terreno_id as "ID TERRENO B", 
        b.qr_operacion_definitivo as "QR OPERACION DEFINITIVO B",  
        CASE 
            WHEN ST_GeometryType(ST_Intersection(a.geometria, b.geometria)) = 'ST_Polygon' THEN 
                ST_Area(ST_Intersection(a.geometria, b.geometria)) 
            WHEN ST_GeometryType(ST_Intersection(a.geometria, b.geometria)) = 'ST_LineString' THEN 
                ST_Length(ST_Intersection(a.geometria, b.geometria))  
        END as "SUPERFICIE_O_LONGITUD",  
        ST_AsText(ST_Intersection(a.geometria, b.geometria)) as "GEOMETRÍA_INTERSECCIÓN_WKT"

    FROM 
        predios_formales a,
        predios_formales b
    WHERE 
        a.terreno_id <> b.terreno_id
        AND ST_Intersects(a.geometria, b.geometria) = TRUE
        AND ST_GeometryType(ST_Intersection(a.geometria, b.geometria)) IN ('ST_Polygon', 'ST_LineString');




    """,

    """
    --- 12.4 los predios informales no se pueden superponer entre si 

    WITH predios_formales AS (
        SELECT 
            ter.t_id as terreno_id, 
            ST_Simplify(ST_MakeValid(ter.geometria), 0.0001) as geometria, 
            pd.qr_operacion, 
            pd.qr_operacion_definitivo, 
            cpt.ilicode as condicion_predio
        FROM 
            cca_terreno ter
        JOIN 
            cca_predio pd ON ter.t_id = pd.terreno
        JOIN 
            cca_condicionprediotipo cpt ON pd.condicion_predio = cpt.t_id
        WHERE 
            cpt.ilicode = 'Informal'  -- Filtra solo los predios formales (condición predio 'NPH')
    )
    SELECT 
        a.terreno_id as "ID TERRENO A", 
        a.qr_operacion_definitivo as "QR OPERACION DEFINITIVO A",  
        b.terreno_id as "ID TERRENO B", 
        b.qr_operacion_definitivo as "QR OPERACION DEFINITIVO B",  
        CASE 
            WHEN ST_GeometryType(ST_Intersection(a.geometria, b.geometria)) = 'ST_Polygon' THEN 
                ST_Area(ST_Intersection(a.geometria, b.geometria))  
            WHEN ST_GeometryType(ST_Intersection(a.geometria, b.geometria)) = 'ST_LineString' THEN 
                ST_Length(ST_Intersection(a.geometria, b.geometria))  
        END as "SUPERFICIE_O_LONGITUD",  
        ST_AsText(ST_Intersection(a.geometria, b.geometria)) as "GEOMETRÍA_INTERSECCIÓN_WKT"

    FROM 
        predios_formales a,
        predios_formales b
    WHERE 
        a.terreno_id <> b.terreno_id
        AND ST_Intersects(a.geometria, b.geometria) = TRUE
        AND ST_GeometryType(ST_Intersection(a.geometria, b.geometria)) IN ('ST_Polygon', 'ST_LineString'); 




    """







]

nombres_consultas_observaciones = [
    "2.1 - La cantidad de registros en terrreno, cca_predio y cca_derecho debe ser igual",
    "2.2 - Los predios deben corresponder a la UIT, municipio, departamento de entrega a nivel alfanumerico según la tabla cca_predio y a nivel espacial",
    "3.1 - No debe existir QR derivados repetidos",
    "3.2 - No debe existir t_ili_tid repetidos en cca_terreno",
    "3.3 - No debe existir t_ili_tid repetidos en cca_predio",
    "3.4 - No debe existir t_ili_tid repetidos en cca_derecho",
    "3.5 - No debe existir t_ili_tid repetidos en cca_interesados",
    "3.6 - No debe existir t_ili_tid repetidos en cca_fuenteadministrativa",
    "3.7 - No debe existir t_ili_tid repetidos en cca_caracteristicasunidadconstruccion",
    "3.8 - No debe existir t_ili_tid repetidos en cca_unidadconstruccion",
    "3.9 - No debe existir t_ili_tid repetidos en cca_puntoreferencia",
    "4.1 - Asociación adecuada de qr_operacion y qr_operacion_definitiva según condicion del predio",
    "4.2 - La de la condición del predio debe ser consecuente con el tipo de derecho",
    "5.1 - Las fechas de visita predial y fecha de finalizado reconocedor no pueden ser superiores a la fecha en curso o vacías",
    "5.2 - La fecha de inicio de tenencia particularmente para Informales no debe estar vacía ó superior a la fecha de la validación",
    "5.3 - La fecha de nacimiento de los interesados de las informalidades no debe estar vacía ó superior a la fecha de validación",
    "5.4 - La fecha del documento fuente administrativa no debe ser superior a la fecha de validación",
    "5.5 - El año de la construccion no puede ser superior al año en curso",
    "5.6 - La Fecha de documento debe ser anterior a la fecha de inicio de tenencia (REVISAR CON EL PAR JURIDICO SI ES EXCEPCIÓN)",
    "6.1 - Documento_publico (escritura, sentencia, acto adm) debe tener un valor en numero_fuente",
    "6.2 - Si tipo fuente es documento.publico entonces fecha documento fuente debe contener un valor",
    "7.1 - Toda caracteristica unidad de construccion debe tener solo 1 poligono de unidad de construccion",
    "7.2 - Todo predio deber tener asociada su dirección",
    "7.3 - Todo terreno debe tener asociada su tabla cca_predio",
    "7.4 - Todo registro de cca_predio debe tener su derecho",
    "7.5 - Todo registro en cca_derecho debe tener su interesado",
    "7.6 - Todo registro en cca_derecho debe tener su fuente administrativa",
    "7.7 - Toda caracteristica unidad de construccion debe tener  su poligono de unidad de construccion",
    "8.1 - Si interesado es persona juridica entonces razon social no puede estar vacio",
    "8.2 - si interesado es persona juridica entonces tipo de documento debe ser NIT",
    "8.3 - Si interesado es persona natural entonces primer nombre, numero documento, primer apellido no puede estar vacio o en blanco",
    "8.4 - Si interesado es persona natural entonces tipo de documento NO puede ser NIT",
    "8.5 - Si interesado es persona natural  y tipo documento  diferente a secuencial entonces fecha de nacimiento no debe estar vacia para las informalidades",
    "8.6 - Las informalidades y con ello los interesados no deberían tener secuenciales",
    "8.7 - un mismo numero documento de identificacion no puede estar relacionado a diferente tipo de documento y diferente interesado",
    "9.1 - El tipo de unidad de construcción debe corresponder con sus respectivos dominios de Uso (ejemplo tipo residencial no puede tener usos de anexos)",
    "9.2 - Si la construccion es convencional (diferente a anexos) debe tener diligenciado  estrato, estructura armazon, acabados, cercha, cubierta, urbanizacion",
    "9.3 - Si el tipo de unidad es no convencional (Anexo) , entonces el uso debe corresponder con dominios del tipo de unidad y a su vez debe tener el tipo de anexo y este  debe corresponder con el uso",
    "9.4 - toda caracteristica de unidad de construccion debe tener diligenciado la conservacion de la tipologia y año de la construccion ",
    "9.5 - Los identificadores de las construcciones deben estar entre A-Z por ende no deberían tener identificadores numéricos",
    "9.6 - Si existe mas de 1 caracteristica de unidad construccion entonces los identificadores deben relacionarse en orden alfabetico y no deben repetirse",
    "10.1 - Datos por diligenciar en el Formulario Integrado de Levantamiento",
    "11.1 - No debe existir poligonos de construcciones multiparte o inválidas",
    "11.2 - Las construcciones no se pueden superponer",
    "12.1 - Predios multiparte o no válidos que se deben verificar",
    "12.2 - Los predios formales No se pueden superponer entre sí",
    "12.4 - Los predios informales No se pueden superponer entre sí"



]
