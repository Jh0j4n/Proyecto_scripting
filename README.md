# Proyecto Final de Scripting - Mini Auditoria Automatizada de Servidor

**Nombre del estudiante:** Jhojan Stiven Castaño Jejen

**Descripcion breve del proyecto:**
Solucion de scripting que automatiza una mini auditoria de servidor combinando
Bash y Python. El script Bash prepara y procesa evidencias simuladas (logs de
autenticacion, procesos del sistema y logs de red), y el script Python ejecuta
el Bash automaticamente, analiza los resultados y genera dos reportes finales:
un JSON estructurado y un resumen ejecutivo en texto plano.

**Comando para ejecutar el proyecto:**

Desde la raiz de la carpeta `proyecto_final_scripting/`:

```
python3 scripts/generar_reporte.py
```

(En sistemas donde el comando `python` apunte a Python 3, tambien puede
usarse `python scripts/generar_reporte.py`).

**Que hace el script Bash (`scripts/preparar_evidencias.sh`):**
- Crea la carpeta de trabajo `work/`.
- Genera los datos base simulados: `auth.log`, `procesos.txt` y `red.log`.
- Filtra las lineas con `Failed password` de `auth.log`.
- Extrae las IPs de los intentos fallidos usando `cut`.
- Cuenta las repeticiones de cada IP fallida con `sort` y `uniq -c`.
- Usa `awk` para detectar procesos con CPU mayor a 80%.
- Usa una tuberia con `cat`, `grep`, `cut`, `sort` y `uniq -c` para contar
  los puertos marcados como `CRITICAL` en el log de red.
- Guarda todos los resultados auxiliares dentro de `work/` para que Python
  los pueda leer.

**Que hace el script Python (`scripts/generar_reporte.py`):**
- Ejecuta automaticamente `scripts/preparar_evidencias.sh` con `subprocess.run()`.
- Valida con `os.path.exists()` que existan los archivos auxiliares generados
  por Bash.
- Lee los archivos auxiliares con `with open()`.
- Usa `re.findall()` para extraer IPs, un `set` para eliminarlas duplicadas,
  listas para almacenar datos procesados y un diccionario para construir el
  reporte final.
- Clasifica los puertos bajo ataque mediante la funcion `clasificar_puerto(puerto)`.
- Determina el `estado_general` de la auditoria (`ALERTA_ALTA`, `ALERTA_MEDIA`
  o `SIN_ALERTAS`) segun las reglas del proyecto.
- Genera `output/reporte_final.json` y `output/resumen_ejecutivo.txt`.
- Maneja errores de ejecucion, lectura y procesamiento con `try/except`.

**Archivos finales generados:**
- `output/reporte_final.json`
- `output/resumen_ejecutivo.txt`

**Observaciones o errores conocidos:**
- No se utilizan librerias externas de Python, solo `os`, `subprocess`, `re` y `json`.
- Todas las rutas usadas en ambos scripts son relativas a la raiz del proyecto.
- La carpeta `work/` contiene archivos auxiliares intermedios y no es un
  entregable obligatorio, pero se conserva para facilitar la trazabilidad
  del proceso.
