@echo

:: Set the database connection details
for /f "tokens=1,2 delims==" %%a in (config.txt) do set %%a=%%b
:: Execute the SQL script
psql -U postgres -d %PGDATABASE% -c "create user %PGUSER% with encrypted password '%PGPASSWORD%'"
psql -U postgres -d %PGDATABASE% -c "grant all privileges on database %PGDATABASE%  to %PGUSER%"

pause

