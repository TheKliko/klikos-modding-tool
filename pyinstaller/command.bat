@echo off

set "project_name=Kliko's modding tool"
set "temp_name=klikos-modding-tool"

set "parent=%~dp0"
set "work_path=%parent%\temp"
set "dist_path=%parent%\bin"

set "root_path=%parent%.."
set "libraries_path=%root_path%\libraries"
set "modules_path=%program_files_path%\modules"
set "config_path=%root_path%\config"
set "resources_path=%root_path%\resources"

set "icon_path=%resources_path%\favicon.ico"
set "splash_path=%resources_path%\splash.png"


if exist "%dist_path%" (
    rmdir /s /q "%dist_path%"
)


if not exist "%libraries_path%" (
    mkdir "%libraries_path%"
)
pip install --upgrade --target="%libraries_path%" pillow requests customtkinter

echo
echo run pyinstaller
pyinstaller ..\main.py ^
--distpath="%dist_path%" ^
--workpath="%work_path%" ^
--specpath="%work_path%" ^
--name="%temp_name%" ^
--icon="..\favicon.ico" ^
--splash="%splash_path%" ^
--clean --onefile --noconsole ^
--paths="%root_path%" ^
--paths="%libraries_path%" ^
--add-data="%resources_path%;resources" ^
--add-data="%config_path%/settings.json;config" ^
--add-data="%config_path%/integrations.json;config"


if exist "%dist_path%\%temp_name%.exe" (
    ren "%dist_path%\%temp_name%.exe" "%project_name%.exe"
)
if exist "%work_path%" (
    rmdir /s /q "%work_path%"
)

pause