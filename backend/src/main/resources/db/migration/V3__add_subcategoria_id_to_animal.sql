
ALTER TABLE ANIMAL ADD subcategoria_id NUMBER(19);


CREATE INDEX idx_animal_subcategoria ON ANIMAL(subcategoria_id);


UPDATE ANIMAL SET subcategoria_id = 101 WHERE subcategoria_id IS NULL;


ALTER TABLE ANIMAL MODIFY subcategoria_id NUMBER(19) NOT NULL;

