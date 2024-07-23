@echo off

:: Set the database connection details
for /f "tokens=1,2 delims==" %%a in (config.txt) do set %%a=%%b
:: Execute the SQL script
psql -U %PGUSER% -d %PGDATABASE% -c "INSERT INTO tb_estados (id, ddd,nome_estado,uf,matchstring) VALUES (5, '71','Bahia', 'BA', 'estado da bahia' );

