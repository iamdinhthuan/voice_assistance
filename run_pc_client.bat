@echo off
echo Starting English Assistant Client on PC...
echo Make sure the server is running in another terminal (python -m server.main)
echo.
echo Using checkpoint: .\wekws\exp\wake_mdtc_noaug_avg\2.pt
echo.

python -m client.main --host localhost --port 8000 --checkpoint .\wekws\exp\wake_mdtc_noaug_avg\2.pt --config .\wekws\exp\wake_mdtc_noaug_avg\config.yaml

pause
