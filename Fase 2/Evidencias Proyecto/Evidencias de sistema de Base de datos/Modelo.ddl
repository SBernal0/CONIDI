-- Generado por Oracle SQL Developer Data Modeler 24.3.1.351.0831
--   en:        2025-10-09 21:54:20 CLST
--   sitio:      SQL Server 2012
--   tipo:      SQL Server 2012



CREATE TABLE ALERGIAS 
    (
     id_alergia NUMERIC (28) NOT NULL , 
     tipo_alergia VARCHAR (200) NOT NULL 
    )
GO

ALTER TABLE ALERGIAS ADD CONSTRAINT ALERGIAS_PK PRIMARY KEY CLUSTERED (id_alergia)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE CIUDAD 
    (
     ciudad_id NUMERIC (28) NOT NULL , 
     nom_ciudad VARCHAR (50) NOT NULL , 
     region_id NUMERIC (28) NOT NULL 
    )
GO

ALTER TABLE CIUDAD ADD CONSTRAINT CIUDAD_PK PRIMARY KEY CLUSTERED (ciudad_id)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE COMUNA 
    (
     comuna_id NUMERIC (28) NOT NULL , 
     nom_comuna VARCHAR (50) NOT NULL , 
     ciudad_id NUMERIC (28) NOT NULL 
    )
GO

ALTER TABLE COMUNA ADD CONSTRAINT COMUNA_PK PRIMARY KEY CLUSTERED (comuna_id)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE CONTROL 
    (
     contro_ninol_id NUMERIC (28) NOT NULL , 
     fecha_control DATETIME NOT NULL , 
     pesokg FLOAT NOT NULL , 
     talla_cm FLOAT NOT NULL , 
     imc FLOAT , 
     edad_meses NUMERIC (28) NOT NULL , 
     observaciones VARCHAR (200) , 
     estado_control VARCHAR (30) NOT NULL , 
     profesional VARCHAR (30) NOT NULL DEFAULT 'Pediatra' , 
     tipo_control VARCHAR (20) NOT NULL DEFAULT 'Control_salud' , 
     tipo_alimentacion VARCHAR (200) , 
     indi_antropometricos VARCHAR (10) , 
     nino_id NUMERIC (28) NOT NULL , 
     calificacion_nutricional VARCHAR (30) NOT NULL DEFAULT 'Normal o Eutrófico' , 
     rut_nino NUMERIC (28) NOT NULL , 
     derivación BIT NOT NULL , 
     nombre_control VARCHAR (200) NOT NULL , 
     fecha_realizacion_control DATETIME , 
     margen_fecha_control NUMERIC (28) NOT NULL , 
     pce FLOAT (2) , 
     calificacion_estatural VARCHAR (30) NOT NULL DEFAULT 'normal' , 
     calificacion_pce VARCHAR (20) DEFAULT 'normal' , 
     PROFESIONAL_profesional_rut VARCHAR (10) NOT NULL , 
     fecha_proximo_control DATETIME , 
     "p/t" FLOAT (2) NOT NULL , 
     "p/e" FLOAT (2) NOT NULL , 
     "t/e" FLOAT (2) NOT NULL , 
     Diag_des_integral VARCHAR (200) NOT NULL , 
     obs_desarrollo_integral VARCHAR (300) NOT NULL , 
     indicaciones VARCHAR (200) NOT NULL , 
     consulta_dental_realizada BIT , 
     derivacion_dentista BIT , 
     pa FLOAT (2) , 
     dig_pa VARCHAR (20) DEFAULT 'normal' , 
     pc_cm FLOAT (2) , 
     "pce/e" FLOAT (2) 
    )
GO 


ALTER TABLE CONTROL 
    ADD 
    CHECK ( tipo_control IN ('Control_nutricional', 'Control_preventivo', 'Control_salud') ) 
GO


ALTER TABLE CONTROL 
    ADD 
    CHECK ( indi_antropometricos IN ('PE', 'PT', 'TE') ) 
GO


ALTER TABLE CONTROL 
    ADD 
    CHECK ( calificacion_estatural IN ('Talla Baja', 'Talla normal baja', 'normal', 'talla alta', 'talla normal alta') ) 
GO


ALTER TABLE CONTROL 
    ADD 
    CHECK ( calificacion_pce IN ('macrocefalia', 'microcefalia', 'normal') ) 
GO


ALTER TABLE CONTROL 
    ADD 
    CHECK ( dig_pa IN ('Hipertensión Etapa 2', 'Sospecha de Hipertensión Etapa 1', 'Sospecha de Prehipertensión', 'normal') ) 
GO

ALTER TABLE CONTROL ADD CONSTRAINT CONTROL_PK PRIMARY KEY CLUSTERED (contro_ninol_id)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE ENTREGA_ALIMENTOS 
    (
     id_entrega NUMERIC (28) NOT NULL , 
     fecha_entrega DATE NOT NULL , 
     fecha_entrega_efectiva DATE , 
     entregado BIT NOT NULL , 
     rut_nino NUMERIC (28) NOT NULL 
    )
GO

ALTER TABLE ENTREGA_ALIMENTOS ADD CONSTRAINT ENTREGA_ALIMENTOS_PK PRIMARY KEY CLUSTERED (id_entrega)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE NINO 
    (
     rut_nino NUMERIC (28) NOT NULL , 
     run VARCHAR (9) NOT NULL , 
     nombre VARCHAR (50) NOT NULL , 
     ap_paterno VARCHAR (30) NOT NULL , 
     ap_materno VARCHAR (30) , 
     fecha_nacimiento DATE NOT NULL , 
     sexo VARCHAR (20) NOT NULL , 
     direccion VARCHAR (200) NOT NULL , 
     fecha_registro DATETIME NOT NULL , 
     comuna_id NUMERIC (28) NOT NULL 
    )
GO

ALTER TABLE NINO ADD CONSTRAINT NINO_PK PRIMARY KEY CLUSTERED (rut_nino)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE NINO_TUTOR 
    (
     rut_tutor NUMERIC (28) NOT NULL , 
     rut_nino NUMERIC (28) NOT NULL , 
     fecha_ini DATETIME NOT NULL , 
     fecha_fin DATETIME 
    )
GO

CREATE TABLE PERIODO_CONTROL 
    (
     control_periodo_id NUMERIC (28) NOT NULL , 
     mes_control NUMERIC (28) NOT NULL , 
     nombre_mes_control VARCHAR (30) NOT NULL 
    )
GO

ALTER TABLE PERIODO_CONTROL ADD CONSTRAINT PERIODO_CONTROL_PK PRIMARY KEY CLUSTERED (control_periodo_id)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE PROFESIONAL 
    (
     profesional_rut VARCHAR (10) NOT NULL , 
     nombre_profesional VARCHAR (200) NOT NULL , 
     especialidad VARCHAR (30) NOT NULL DEFAULT 'Pediatra' 
    )
GO 


ALTER TABLE PROFESIONAL 
    ADD 
    CHECK ( especialidad IN ('Enfermero/a', 'Matron/a', 'Medico General', 'Nutricionista', 'Pediatra') ) 
GO

ALTER TABLE PROFESIONAL ADD CONSTRAINT PROFESIONAL_PK PRIMARY KEY CLUSTERED (profesional_rut)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE REGION 
    (
     region_id NUMERIC (28) NOT NULL , 
     nom_region VARCHAR (20) NOT NULL 
    )
GO

ALTER TABLE REGION ADD CONSTRAINT REGION_PK PRIMARY KEY CLUSTERED (region_id)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE REGISTRO_ALERGIAS 
    (
     fecha_aparicion DATETIME NOT NULL , 
     fecha_remision DATETIME , 
     rut_nino NUMERIC (28) NOT NULL , 
     id_alergia NUMERIC (28) NOT NULL 
    )
GO

CREATE TABLE ROL 
    (
     rol_id NUMERIC (28) NOT NULL , 
     nombre_rol VARCHAR (30) NOT NULL , 
     descripcion VARCHAR (200) NOT NULL 
    )
GO

ALTER TABLE ROL ADD CONSTRAINT ROL_PK PRIMARY KEY CLUSTERED (rol_id)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE TUTOR 
    (
     rut_tutor NUMERIC (28) NOT NULL , 
     nombre_completo VARCHAR (200) NOT NULL , 
     telefono NUMERIC (28) , 
     email VARCHAR (100) , 
     direccion VARCHAR (200) , 
     parentesco VARCHAR (35) NOT NULL DEFAULT 'Madre' , 
     fecha_ini DATE NOT NULL , 
     fecha_fin DATE , 
     usuario_id NUMERIC (28) NOT NULL 
    )
GO 


ALTER TABLE TUTOR 
    ADD 
    CHECK ( parentesco IN ('Abuela', 'Abuelo', 'Hermano/a', 'Madre', 'Padre', 'Tutor legal', 'Tía', 'Tío') ) 
GO

    


CREATE UNIQUE NONCLUSTERED INDEX 
    TUTOR__IDX ON TUTOR 
    ( 
     usuario_id 
    ) 
GO

ALTER TABLE TUTOR ADD CONSTRAINT TUTOR_PK PRIMARY KEY CLUSTERED (rut_tutor)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE USUARIO 
    (
     usuario_id NUMERIC (28) NOT NULL , 
     rut VARCHAR (10) NOT NULL , 
     contrasena VARCHAR (100) NOT NULL , 
     nombre_completo VARCHAR (200) NOT NULL , 
     fecha_creacion DATETIME NOT NULL , 
     activo BIT NOT NULL , 
     correo VARCHAR (40) NOT NULL , 
     rol_id NUMERIC (28) 
    )
GO 



EXEC sp_addextendedproperty 'MS_Description' , 'si esta el usuario activo o no para usar la plataforma' , 'USER' , 'dbo' , 'TABLE' , 'USUARIO' , 'COLUMN' , 'activo' 
GO

ALTER TABLE USUARIO ADD CONSTRAINT USUARIO_PK PRIMARY KEY CLUSTERED (usuario_id)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE VACUNA 
    (
     vacuna_id NUMERIC (28) NOT NULL , 
     nom_vacuna VARCHAR (200) NOT NULL , 
     descripcion VARCHAR (200) 
    )
GO

ALTER TABLE VACUNA ADD CONSTRAINT VACUNA_PK PRIMARY KEY CLUSTERED (vacuna_id)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

CREATE TABLE VACUNA_APLICADA 
    (
     vacuna_aplicada_id NUMERIC (28) NOT NULL , 
     fecha_aplicacion DATE NOT NULL , 
     dosis FLOAT (1) NOT NULL , 
     lugar VARCHAR (100) NOT NULL , 
     negacion BIT NOT NULL , 
     via VARCHAR (10) NOT NULL DEFAULT 'N/A' , 
     fecha_inoculación DATE , 
     vacuna_id NUMERIC (28) NOT NULL , 
     rut_nino NUMERIC (28) NOT NULL 
    )
GO 


ALTER TABLE VACUNA_APLICADA 
    ADD 
    CHECK ( via IN ('I.D', 'I.M', 'N/A', 'S.C', 'V.O') ) 
GO

ALTER TABLE VACUNA_APLICADA ADD CONSTRAINT VACUNA_APLICADA_PK PRIMARY KEY CLUSTERED (vacuna_aplicada_id)
     WITH (
     ALLOW_PAGE_LOCKS = ON , 
     ALLOW_ROW_LOCKS = ON )
GO

ALTER TABLE CIUDAD 
    ADD CONSTRAINT CIUDAD_REGION_FK FOREIGN KEY 
    ( 
     region_id
    ) 
    REFERENCES REGION 
    ( 
     region_id 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE COMUNA 
    ADD CONSTRAINT COMUNA_CIUDAD_FK FOREIGN KEY 
    ( 
     ciudad_id
    ) 
    REFERENCES CIUDAD 
    ( 
     ciudad_id 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE CONTROL 
    ADD CONSTRAINT CONTROL_NINO_FK FOREIGN KEY 
    ( 
     rut_nino
    ) 
    REFERENCES NINO 
    ( 
     rut_nino 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE CONTROL 
    ADD CONSTRAINT CONTROL_PROFESIONAL_FK FOREIGN KEY 
    ( 
     PROFESIONAL_profesional_rut
    ) 
    REFERENCES PROFESIONAL 
    ( 
     profesional_rut 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE ENTREGA_ALIMENTOS 
    ADD CONSTRAINT ENTREGA_ALIMENTOS_NINO_FK FOREIGN KEY 
    ( 
     rut_nino
    ) 
    REFERENCES NINO 
    ( 
     rut_nino 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE NINO 
    ADD CONSTRAINT NINO_COMUNA_FK FOREIGN KEY 
    ( 
     comuna_id
    ) 
    REFERENCES COMUNA 
    ( 
     comuna_id 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE NINO_TUTOR 
    ADD CONSTRAINT NINO_TUTOR_NINO_FK FOREIGN KEY 
    ( 
     rut_nino
    ) 
    REFERENCES NINO 
    ( 
     rut_nino 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE NINO_TUTOR 
    ADD CONSTRAINT NINO_TUTOR_TUTOR_FK FOREIGN KEY 
    ( 
     rut_tutor
    ) 
    REFERENCES TUTOR 
    ( 
     rut_tutor 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE REGISTRO_ALERGIAS 
    ADD CONSTRAINT REGISTRO_ALERGIAS_ALERGIAS_FK FOREIGN KEY 
    ( 
     id_alergia
    ) 
    REFERENCES ALERGIAS 
    ( 
     id_alergia 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE REGISTRO_ALERGIAS 
    ADD CONSTRAINT REGISTRO_ALERGIAS_NINO_FK FOREIGN KEY 
    ( 
     rut_nino
    ) 
    REFERENCES NINO 
    ( 
     rut_nino 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE TUTOR 
    ADD CONSTRAINT TUTOR_USUARIO_FK FOREIGN KEY 
    ( 
     usuario_id
    ) 
    REFERENCES USUARIO 
    ( 
     usuario_id 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE USUARIO 
    ADD CONSTRAINT USUARIO_ROL_FK FOREIGN KEY 
    ( 
     rol_id
    ) 
    REFERENCES ROL 
    ( 
     rol_id 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE VACUNA_APLICADA 
    ADD CONSTRAINT VACUNA_APLICADA_NINO_FK FOREIGN KEY 
    ( 
     rut_nino
    ) 
    REFERENCES NINO 
    ( 
     rut_nino 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO

ALTER TABLE VACUNA_APLICADA 
    ADD CONSTRAINT VACUNA_APLICADA_VACUNA_FK FOREIGN KEY 
    ( 
     vacuna_id
    ) 
    REFERENCES VACUNA 
    ( 
     vacuna_id 
    ) 
    ON DELETE NO ACTION 
    ON UPDATE NO ACTION 
GO



-- Informe de Resumen de Oracle SQL Developer Data Modeler: 
-- 
-- CREATE TABLE                            16
-- CREATE INDEX                             1
-- ALTER TABLE                             36
-- CREATE VIEW                              0
-- ALTER VIEW                               0
-- CREATE PACKAGE                           0
-- CREATE PACKAGE BODY                      0
-- CREATE PROCEDURE                         0
-- CREATE FUNCTION                          0
-- CREATE TRIGGER                           0
-- ALTER TRIGGER                            0
-- CREATE DATABASE                          0
-- CREATE DEFAULT                           0
-- CREATE INDEX ON VIEW                     0
-- CREATE ROLLBACK SEGMENT                  0
-- CREATE ROLE                              0
-- CREATE RULE                              0
-- CREATE SCHEMA                            0
-- CREATE SEQUENCE                          0
-- CREATE PARTITION FUNCTION                0
-- CREATE PARTITION SCHEME                  0
-- 
-- DROP DATABASE                            0
-- 
-- ERRORS                                   0
-- WARNINGS                                 0
