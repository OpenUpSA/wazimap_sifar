export PGPASSWORD=wazimap_sifar

for table in $(psql -U wazimap_sifar -h development -d wazimap_sifar -t -c "Select table_name From information_schema.tables Where table_type='BASE TABLE' and table_name like 'senior_%'");
do pg_dump -t $table -U wazimap_sifar -h development wazimap_sifar > $table.sql;
done;
