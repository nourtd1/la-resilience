@echo off
color 0A
echo ========================================================
echo   INSTALLATION - HOTEL LA RESILIENCE
echo ========================================================
echo.
echo 1. Verification de Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERREUR] Python n'est pas installe.
    echo Veuillez installer Python depuis python.org et cocher "Add to PATH".
    pause
    exit
)
echo Python OK.
echo.
echo 2. Creation environnement virtuel...
python -m venv venv
echo.
echo 3. Activation et installation dependances...
call venv\Scripts\activate
pip install -r requirements.txt
echo.
echo 4. Bases de donnees...
python manage.py migrate
echo.
echo 5. Creation compte Admin...
echo (Laissez vide et faites Entree si vous voulez passer pour l'instant)
python manage.py createsuperuser
echo.
echo 6. Donnees de test...
python manage.py populate_db
echo.
echo INSTALLATION TERMINEE !
echo Utilisez lancer_application.bat pour demarrer.
pause
