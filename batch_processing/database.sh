# Create index:
ALTER TABLE log_geolocation ADD PRIMARY KEY (geoname_id,cik,date);
create index date_idx on log_geolocation using brin(date);
create index cik_country_idx on log_geolocation(cik, country_iso_code);
create index cik_geoname_idx on log_geolocation(cik, geoname_id);


select * from pg_indexes where tablename='log_geolocation';