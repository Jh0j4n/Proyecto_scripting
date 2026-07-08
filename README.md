# Mini Auditoría Automatizada de Servidor

Proyecto de scripting que automatiza una auditoría básica de servidor combinando **Bash** y **Python**. Simula evidencias de seguridad (intentos de login fallidos, procesos con alto consumo de CPU y puertos bajo ataque), las procesa y genera reportes finales en JSON y texto plano.

## Descripción

- **Bash** prepara y filtra las evidencias simuladas usando `grep`, `cut`, `sort`, `uniq` y `awk`.
- **Python** ejecuta el script Bash automáticamente, analiza los resultados y genera los reportes finales.

No requiere ejecutar nada manualmente: con un solo comando se genera todo el flujo.

## Estructura del proyecto

```
proyecto_final_scripting/
├── scripts/
│   ├── preparar_evidencias.sh   # Prepara y procesa evidencias (Bash)
│   └── generar_reporte.py       # Orquesta todo y genera reportes (Python)
├── output/
│   ├── reporte_final.json       # Reporte estructurado
│   └── resumen_ejecutivo.txt    # Resumen legible
└── README.md
```

> La carpeta `work/` (archivos intermedios) se genera automáticamente al ejecutar el proyecto y no se versiona en este repositorio.

## Requisitos

- Bash
- Python 3 (solo librerías estándar: `os`, `subprocess`, `re`, `json`)

##  Cómo ejecutarlo

Desde la raíz del proyecto:

```bash
python3 scripts/generar_reporte.py
```

Esto ejecuta automáticamente el script Bash, valida los datos generados, los analiza y crea los reportes en `output/`.

## Qué hace cada script

**`preparar_evidencias.sh`**
- Genera datos simulados: `auth.log`, `procesos.txt`, `red.log`.
- Filtra intentos de login fallidos y extrae IPs con `cut`.
- Cuenta repeticiones por IP con `sort` + `uniq -c`.
- Detecta con `awk` procesos que superan 80% de CPU.
- Cuenta puertos marcados como `CRITICAL` con una tubería `cat | grep | cut | sort | uniq -c`.

**`generar_reporte.py`**
- Ejecuta el script Bash con `subprocess.run()` y valida los archivos generados.
- Extrae IPs con expresiones regulares (`re.findall()`).
- Clasifica puertos con `clasificar_puerto(puerto)`:

  | Puertos | Clasificación |
  |---|---|
  | 22, 23, 21, 3389 | ALTO RIESGO |
  | 80, 443 | MEDIO RIESGO |
  | otros | BAJO RIESGO |

- Calcula el `estado_general` (`ALERTA_ALTA`, `ALERTA_MEDIA`, `SIN_ALERTAS`).
- Genera `output/reporte_final.json` y `output/resumen_ejecutivo.txt`.

## Ejemplo de salida

```json
{
    "total_intentos_fallidos": 4,
    "ips_unicas": 2,
    "ip_mas_repetida": "192.168.1.105",
    "procesos_criticos": 2,
    "puertos_bajo_ataque": [
        { "puerto": 22, "conteo": 3, "riesgo": "ALTO RIESGO" },
        { "puerto": 443, "conteo": 1, "riesgo": "MEDIO RIESGO" }
    ],
    "estado_general": "ALERTA_ALTA"
}
```

## Notas

- No se usan librerías externas de Python.
- Todas las rutas son relativas a la raíz del proyecto.
