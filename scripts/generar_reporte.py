#!/usr/bin/env python3
import os
import subprocess
import re
import json


SCRIPT_BASH = os.path.join("scripts", "preparar_evidencias.sh")
WORKDIR = "work"
OUTPUTDIR = "output"

ARCHIVOS_AUXILIARES = [
    os.path.join(WORKDIR, "intentos_fallidos.log"),
    os.path.join(WORKDIR, "ips_fallidas.txt"),
    os.path.join(WORKDIR, "top_ips.txt"),
    os.path.join(WORKDIR, "procesos_criticos.txt"),
    os.path.join(WORKDIR, "puertos_bajo_ataque.report"),
]


def ejecutar_bash():
    print("Ejecutando script Bash de preparacion de evidencias...")
    try:
        resultado = subprocess.run(
            ["bash", SCRIPT_BASH],
            capture_output=True,
            text=True,
            check=True,
        )
        print(resultado.stdout)
        return True
    except subprocess.CalledProcessError as error:
        print("ERROR: el script Bash fallo durante su ejecucion.")
        print(error.stderr)
        return False
    except FileNotFoundError:
        print(f"ERROR: no se encontro el script Bash en '{SCRIPT_BASH}'.")
        return False


def validar_archivos_auxiliares():
    faltantes = []
    for ruta in ARCHIVOS_AUXILIARES:
        if not os.path.exists(ruta):
            faltantes.append(ruta)

    if faltantes:
        print("ERROR: faltan los siguientes archivos auxiliares:")
        for ruta in faltantes:
            print(f"  - {ruta}")
        return False

    return True


def leer_lineas(ruta):
    lineas = []
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                linea_limpia = linea.strip()
                if linea_limpia:
                    lineas.append(linea_limpia)
    except (OSError, IOError) as error:
        print(f"ERROR: no se pudo leer el archivo '{ruta}': {error}")
    return lineas


def clasificar_puerto(puerto):
    puertos_alto_riesgo = [22, 23, 21, 3389]
    puertos_medio_riesgo = [80, 443]

    if puerto in puertos_alto_riesgo:
        return "ALTO RIESGO"
    elif puerto in puertos_medio_riesgo:
        return "MEDIO RIESGO"
    else:
        return "BAJO RIESGO"


def analizar_intentos_fallidos():
    lineas_intentos = leer_lineas(os.path.join(WORKDIR, "intentos_fallidos.log"))
    total_intentos_fallidos = len(lineas_intentos)

    lineas_ips = leer_lineas(os.path.join(WORKDIR, "ips_fallidas.txt"))

    patron_ip = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    lista_ips = []
    for linea in lineas_ips:
        ips_encontradas = re.findall(patron_ip, linea)
        lista_ips.extend(ips_encontradas)

    ips_unicas_set = set(lista_ips)
    ips_unicas = len(ips_unicas_set)

    conteo_ips = {}
    for ip in lista_ips:
        if ip in conteo_ips:
            conteo_ips[ip] += 1
        else:
            conteo_ips[ip] = 1

    ip_mas_repetida = None
    max_conteo = 0
    for ip, conteo in conteo_ips.items():
        if conteo > max_conteo:
            max_conteo = conteo
            ip_mas_repetida = ip

    return total_intentos_fallidos, ips_unicas, ip_mas_repetida


def analizar_procesos_criticos():
    lineas = leer_lineas(os.path.join(WORKDIR, "procesos_criticos.txt"))
    return len(lineas)


def analizar_puertos_bajo_ataque():
    lineas = leer_lineas(os.path.join(WORKDIR, "puertos_bajo_ataque.report"))
    puertos_bajo_ataque = []

    for linea in lineas:
        partes = linea.split()
        if len(partes) == 2:
            conteo_str, puerto_str = partes
            try:
                conteo = int(conteo_str)
                puerto = int(puerto_str)
            except ValueError:
                continue

            riesgo = clasificar_puerto(puerto)
            puertos_bajo_ataque.append({
                "puerto": puerto,
                "conteo": conteo,
                "riesgo": riesgo,
            })

    return puertos_bajo_ataque


def determinar_estado_general(total_intentos_fallidos, procesos_criticos, puertos_bajo_ataque):
    hay_alto_riesgo = False
    for puerto_info in puertos_bajo_ataque:
        if puerto_info["riesgo"] == "ALTO RIESGO":
            hay_alto_riesgo = True

    if hay_alto_riesgo or procesos_criticos >= 2 or total_intentos_fallidos >= 4:
        return "ALERTA_ALTA"
    elif total_intentos_fallidos > 0 or procesos_criticos > 0 or len(puertos_bajo_ataque) > 0:
        return "ALERTA_MEDIA"
    else:
        return "SIN_ALERTAS"


def generar_reporte_json(reporte):
    ruta_json = os.path.join(OUTPUTDIR, "reporte_final.json")
    try:
        with open(ruta_json, "w", encoding="utf-8") as archivo:
            json.dump(reporte, archivo, indent=4, ensure_ascii=False)
        print(f"Reporte JSON generado en '{ruta_json}'")
    except (OSError, IOError) as error:
        print(f"ERROR: no se pudo escribir el reporte JSON: {error}")


def generar_resumen_ejecutivo(reporte, nombre_estudiante="Jhojan Castaño"):
    ruta_resumen = os.path.join(OUTPUTDIR, "resumen_ejecutivo.txt")
    try:
        with open(ruta_resumen, "w", encoding="utf-8") as archivo:
            archivo.write("=== RESUMEN DE AUDITORIA ===\n")
            archivo.write(f"Estudiante: {nombre_estudiante}\n")
            archivo.write(f"Intentos fallidos detectados: {reporte['total_intentos_fallidos']}\n")
            archivo.write(f"IPs unicas detectadas: {reporte['ips_unicas']}\n")
            archivo.write(f"IP con mayor cantidad de intentos: {reporte['ip_mas_repetida']}\n")
            archivo.write(f"Procesos criticos detectados: {reporte['procesos_criticos']}\n")
            archivo.write(f"Puertos bajo ataque detectados: {len(reporte['puertos_bajo_ataque'])}\n")
            archivo.write(f"Estado general: {reporte['estado_general']}\n")
        print(f"Resumen ejecutivo generado en '{ruta_resumen}'")
    except (OSError, IOError) as error:
        print(f"ERROR: no se pudo escribir el resumen ejecutivo: {error}")


def main():
    if not ejecutar_bash():
        print("El proyecto no puede continuar sin los resultados de Bash.")
        return

    if not validar_archivos_auxiliares():
        print("El proyecto no puede continuar: faltan archivos auxiliares.")
        return

    try:
        total_intentos_fallidos, ips_unicas, ip_mas_repetida = analizar_intentos_fallidos()
        procesos_criticos = analizar_procesos_criticos()
        puertos_bajo_ataque = analizar_puertos_bajo_ataque()

        estado_general = determinar_estado_general(
            total_intentos_fallidos, procesos_criticos, puertos_bajo_ataque
        )

        reporte = {
            "total_intentos_fallidos": total_intentos_fallidos,
            "ips_unicas": ips_unicas,
            "ip_mas_repetida": ip_mas_repetida,
            "procesos_criticos": procesos_criticos,
            "puertos_bajo_ataque": puertos_bajo_ataque,
            "estado_general": estado_general,
        }

        if not os.path.exists(OUTPUTDIR):
            os.makedirs(OUTPUTDIR)

        generar_reporte_json(reporte)
        generar_resumen_ejecutivo(reporte)

        print("\nProceso de auditoria completado exitosamente.")
        print(json.dumps(reporte, indent=4, ensure_ascii=False))

    except Exception as error:
        print(f"ERROR inesperado durante el analisis: {error}")


if __name__ == "__main__":
    main()
