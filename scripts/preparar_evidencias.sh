#!/bin/bash

set -e

WORKDIR="work"
mkdir -p "$WORKDIR"

cat > "$WORKDIR/auth.log" << 'EOF'
2026-06-19 18:00:00,Failed password,192.168.1.105,ssh
2026-06-19 18:01:00,Accepted password,192.168.1.20,ssh
2026-06-19 18:02:00,Failed password,192.168.1.112,ssh
2026-06-19 18:02:30,Failed password,192.168.1.105,ssh
2026-06-19 18:03:15,Failed password,192.168.1.105,ssh
EOF

cat > "$WORKDIR/procesos.txt" << 'EOF'
PID:101,App:nginx,CPU:85%
PID:102,App:mysql,CPU:45%
PID:103,App:php,CPU:92%
PID:104,App:redis,CPU:12%
EOF

cat > "$WORKDIR/red.log" << 'EOF'
NET_LOG: CRITICAL - Port:22
NET_LOG: INFO - Port:80
NET_LOG: CRITICAL - Port:22
NET_LOG: CRITICAL - Port:443
NET_LOG: CRITICAL - Port:22
EOF

echo "[preparar_evidencias.sh] Datos base generados en $WORKDIR/"


grep "Failed password" "$WORKDIR/auth.log" > "$WORKDIR/intentos_fallidos.log"

cut -d',' -f3 "$WORKDIR/intentos_fallidos.log" > "$WORKDIR/ips_fallidas.txt"

sort "$WORKDIR/ips_fallidas.txt" | uniq -c | sort -rn > "$WORKDIR/top_ips.txt"

awk -F',' '{
    split($1, pid_arr, ":");
    split($2, app_arr, ":");
    split($3, cpu_arr, ":");
    cpu_val = cpu_arr[2];
    gsub("%", "", cpu_val);
    if (cpu_val + 0 > 80) {
        print "ALERTA - Proceso critico: " app_arr[2] " (PID: " pid_arr[2] ")";
    }
}' "$WORKDIR/procesos.txt" > "$WORKDIR/procesos_criticos.txt"

cat "$WORKDIR/red.log" | grep "CRITICAL" | cut -d':' -f3 | sort | uniq -c | sort -rn > "$WORKDIR/puertos_bajo_ataque.report"

echo "[preparar_evidencias.sh] Procesamiento completado. Resultados en $WORKDIR/"

exit 0
