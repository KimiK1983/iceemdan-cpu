# Copyright, procedencia y modificaciones

## Wrapper y código CPU

Wrapper original: Copyright 2025 Javier F. Santamaria. El titular autorizó distribuir el wrapper y sus aportaciones bajo Apache License, Version 2.0. Las correcciones del producto CPU de 2026-09-25 y 2026-09-28 se identifican en la cabecera de `ICEEMDAN.py`. El texto completo de la licencia está en `LICENSE` y en la constante `APACHE_2_0_LICENSE` del módulo.

## Geometría derivada de PyEMD

Copyright 2017 Dawid Laszuk. Apache License, Version 2.0. El bloque `BEGIN PyEMD-derived geometry` / `END PyEMD-derived geometry` de `ICEEMDAN.py` marca las funciones de reflexión de extremos e interpolación incorporadas desde PyEMD v1.10.0 (`EMD.py` y `splines.py`) en la referencia CPU suministrada. Este archivo integra y modifica ese material dentro de un EMD/ICEEMDAN CPU con contratos y correcciones numéricas propios; no se presenta como una copia sin cambios de PyEMD. Los avisos de copyright y modificación se conservan en el propio archivo. PyEMD no es dependencia de ejecución y no se redistribuye su paquete.

Proyecto de origen: https://github.com/laszukdawid/PyEMD . La fuente inmediata de esta distribución es el módulo CPU de producto, no una descarga nueva de PyEMD.
