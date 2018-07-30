create table manxingbing_tbl if not exists(
   disease_id INT NOT NULL AUTO_INCREMENT,
   disease_name VARCHAR(40) NOT NULL,
   disease_alias VARCHAR(100),
   medicare VARCHAR(100),
   pathogenic_site VARCHAR(100),
   departmant VARCHAR(100),
   infectivity VARCHAR(100),
   therapies VARCHAR(100),
   cure_rate VARCHAR(100),
   treatment_cycle VARCHAR(100),
   susceptible VARCHAR(100),
   cost VARCHAR(100),
   symptom VARCHAR(100),
   examination VARCHAR(100),
   syndrome VARCHAR(100),
   drug VARCHAR(100),
   PRIMARY KEY ( disease_id )
);