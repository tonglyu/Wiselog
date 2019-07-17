# Create primary index:
ALTER TABLE log_geolocation ADD PRIMARY KEY (geoname_id,cik,date);
# Select index
select * from pg_indexes where tablename='log_geolocation';

# Group by city for a company
select cik, geoname_id, sum(count) as total
from log_geolocation
where cik = '1288776'
and date between '2016-08-01' and '2016-08-31'
group by geoname_id;

# Group by country for a company
select country_iso_code, sum(count) as total
from company_geo_table
where cik = '1288776'
and date between '2016-01-01' and '2016-01-31'
group by country_iso_code;

# Join city info
select  log.total as total, coord.country_name as country_name, coord.region_name as region,
coord.city_name as city, coord.lat as lat, coord.lng as lng
from city_coordinates coord,
(select geoname_id, sum(count) as total from log_geolocation
where cik = '1288776' and (date between '2016-10-01' and '2016-10-31')
group by geoname_id order by total desc limit 20) log
where log.geoname_id = coord.geoname_id;