# Create index:
ALTER TABLE log_geolocation ADD PRIMARY KEY (geoname_id,cik,date);
create index date_idx on log_geolocation using brin(date);
create index cik_country_idx on log_geolocation(cik, country_iso_code);
create index cik_geoname_idx on log_geolocation(cik, geoname_id);


select * from pg_indexes where tablename='log_geolocation';

select cik, geoname_id, sum(count) as total
from company_geo_table
where cik = '1288776'
and date between '2016-08-01' and '2016-08-31'
group by cik, geoname_id;

select cik,  country_iso_code, sum(count) as total
from company_geo_table
where cik = '1288776'
and date between '2016-01-01' and '2016-01-31'
group by cik,  country_iso_code;

select log.cik as cik, log.total as total, coord.country_name as country_name, coord.region_name as region,
coord.city_name as city, coord.lat as lat, coord.lng as lng
from (select cik, geoname_id, sum(count) as total from company_geo_table
where cik = '1288776' and (date between '2016-03-01' and '2016-03-31')
group by (cik, geoname_id) order by total desc limit 20) log
inner join city_coordinates coord on log.geoname_id = coord.geoname_id;