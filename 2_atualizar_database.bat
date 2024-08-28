@echo off

:: Set the database connection details
for /f "tokens=1,2 delims==" %%a in (config.txt) do set %%a=%%b
:: Execute the SQL script
psql -U %PGUSER% -d %PGDATABASE% -c "INSERT INTO tb_estados (id, ddd,nome_estado,uf,matchstring) VALUES (13, '51','Mato Grosso', 'MT', 'MATO GROSSO' );
psql -U %PGUSER% -d %PGDATABASE% -c "ALTER TABLE tb_publicacoes ADD tempo_servico INT;"
psql -U %PGUSER% -d %PGDATABASE% -c "ALTER TABLE tb_leads ALTER COLUMN cpf TYPE VARCHAR(14);"

