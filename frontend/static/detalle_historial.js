document.addEventListener("DOMContentLoaded", () => {
    
    // =========================================================================
    // 1. CARGA INICIAL DE DATOS
    // =========================================================================
    const datosRaw = localStorage.getItem("prediccion_resultados");
    const nombreGuardado = localStorage.getItem("nombre_historial_activo");
    
    const contenedorTitulares = document.getElementById("contenedor_titulares");
    const contenedorReservas = document.getElementById("contenedor_reservas");
    const titulo = document.getElementById("titulo_detalle");

    if (!datosRaw) {
        alert("No se encontraron datos de la convocatoria.");
        window.location.href = "/historial_predicciones";
        return;
    }

    // Ponemos el nombre personalizado en el título
    if (nombreGuardado) {
        const nombreLimpio = nombreGuardado.replace(/[^\p{L}\p{N}\s\-_.]/gu, '').trim(); 
        titulo.textContent = nombreLimpio ? nombreLimpio : "Detalle de Convocatoria";
    }

    const datos = JSON.parse(datosRaw);
    pintarLista(datos.titulares, contenedorTitulares, true);
    pintarLista(datos.reservas, contenedorReservas, false);

    function pintarLista(jugadores, contenedor, esOficial) {
        if (!jugadores || jugadores.length === 0) {
            contenedor.innerHTML = "<p>No hay datos disponibles.</p>";
            return;
        }

        if (esOficial) {
            ["GK", "DF", "MF", "FW"].forEach(pos => {
                const filtrados = jugadores.filter(j => j.posicion === pos);
                if (filtrados.length > 0) {
                    const div = document.createElement("div");
                    div.className = "seccion-posicion";
                    div.textContent = pos === "GK" ? "Porteros" : pos === "DF" ? "Defensas" : pos === "MF" ? "Medios" : "Delanteros";
                    contenedor.appendChild(div);
                    filtrados.forEach(j => contenedor.appendChild(crearCard(j)));
                }
            });
        } else {
            jugadores.forEach(j => contenedor.appendChild(crearCard(j)));
        }
    }

    function crearCard(j) {
        const div = document.createElement("div");
        div.className = "jugador-card";
        div.innerHTML = `
            <div>
                <span class="pos-tag">${j.posicion}</span> 
                <strong style="color: var(--texto-principal);">${j.nombre}</strong>
                <span style="font-size: 0.8rem; color: #6B7280; font-weight: normal; margin-left: 5px;">
                    (${j.equipo}, ${j.liga || "Liga desconocida"})
                </span>
            </div>
            <div class="prob-val">${j.probabilidad}%</div>
        `;
        return div;
    }

    // =========================================================================
    // 2. DESCARGAR PDF
    // =========================================================================
    const btnDescargar = document.getElementById("btn_descargar_detalle");
    if (btnDescargar) {
        btnDescargar.addEventListener("click", async () => {
            const estadoAccion = document.getElementById("estado_accion_detalle");
            
            btnDescargar.disabled = true;
            estadoAccion.textContent = "Generando PDF...";
            estadoAccion.style.color = "var(--texto-principal)"; 

            try {
                const payloadPDF = {
                    seleccion: localStorage.getItem("seleccion_actual") || "España",
                    modelo_predictivo: "Recuperado del Historial", 
                    titulares: datos.titulares,
                    reservas: datos.reservas
                };

                const res = await fetch("http://127.0.0.1:8000/api/predict/descargar_convocatoria_pdf", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify(payloadPDF)
                });
                
                if (!res.ok) throw new Error("Fallo en el documento");

                const blob = await res.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `${nombreGuardado ? nombreGuardado.replace(/\s+/g, '_') : 'informe_historial'}.pdf`;
                a.click();
                
                estadoAccion.textContent = "Descarga completada";
                estadoAccion.style.color = "var(--color-exito)";
                
                setTimeout(() => { estadoAccion.textContent = ""; }, 3000);

            } catch (e) {
                estadoAccion.textContent = "Error al descargar el PDF";
                estadoAccion.style.color = "var(--color-error)";
            } finally {
                btnDescargar.disabled = false;
            }
        });
    }
});