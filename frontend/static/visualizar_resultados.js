document.addEventListener("DOMContentLoaded", () => {
    
    // =========================================================================
    // 1. CARGA INICIAL DE DATOS
    // =========================================================================
    const datosRaw = localStorage.getItem("prediccion_resultados");
    const contenedorTitulares = document.getElementById("contenedor_titulares");
    const contenedorReservas = document.getElementById("contenedor_reservas");

    if (!datosRaw) {
        alert("No hay resultados disponibles.");
        window.location.href = "/generar_prediccion";
        return;
    }

    const datos = JSON.parse(datosRaw);
    pintarLista(datos.titulares, contenedorTitulares, true);
    pintarLista(datos.reservas, contenedorReservas, false);

    function pintarLista(jugadores, contenedor, esOficial) {
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
                    (${j.equipo}, ${j.liga})
                </span>
            </div>
            <div class="prob-val">${j.probabilidad}%</div>
        `;
        return div;
    }

    // =========================================================================
    // 2. CONSULTAR INFO MODELO
    // =========================================================================
    document.getElementById("btn_info_modelo").addEventListener("click", async () => {
        document.getElementById("modal_info").style.display = "flex";
        try {
            const res = await fetch("http://127.0.0.1:8000/api/modelo/info");
            const info = await res.json();
            document.getElementById("info_archivo").textContent = info.archivo_original || "No disponible";
            document.getElementById("info_algoritmo").textContent = info.algoritmo || "No disponible";
            document.getElementById("info_ventana").textContent = info.ventana || "No disponible";
            document.getElementById("info_descripcion").textContent = info.descripcion || "No disponible";
        } catch (e) {
            console.error("Error al cargar metadatos:", e);
        }
    });

    // =========================================================================
    // 3. GUARDAR CONVOCATORIA
    // =========================================================================
    document.getElementById("btn_abrir_guardar").addEventListener("click", () => {
        document.getElementById("modal_guardar").style.display = "flex";
        document.getElementById("input_nombre_historial").focus(); 
    });

    document.getElementById("btn_confirmar_guardar").addEventListener("click", async () => {
        const nombre = document.getElementById("input_nombre_historial").value;
        const email = localStorage.getItem("email_usuario"); 
        const seleccion = localStorage.getItem("seleccion_actual") || "España";
        
        const errorMsg = document.getElementById("msg_error_guardar");
        const exitoMsg = document.getElementById("msg_exito_guardar"); 
        const btnConfirmar = document.getElementById("btn_confirmar_guardar"); 

        if (!nombre.trim()) {
            errorMsg.textContent = "Error: Debes introducir un nombre.";
            errorMsg.style.display = "block";
            exitoMsg.style.display = "none";
            return;
        }

        if (!email) {
            errorMsg.textContent = "Error: Tu sesión ha caducado. Vuelve a iniciar sesión.";
            errorMsg.style.display = "block";
            return;
        }

        btnConfirmar.disabled = true;
        btnConfirmar.textContent = "Guardando...";

        try {
            const res = await fetch("http://127.0.0.1:8000/api/users/guardar_convocatoria", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    email: email,
                    nombre_personalizado: nombre,
                    seleccion: seleccion,
                    datos_jugadores: datos 
                })
            });
            
            const result = await res.json();
            
            if (res.ok) {
                errorMsg.style.display = "none";
                exitoMsg.textContent = result.mensaje || "Guardado correctamente.";
                exitoMsg.style.color = "var(--color-exito)";
                exitoMsg.style.display = "block";
                
                setTimeout(() => {
                    cerrarModal('modal_guardar');
                    exitoMsg.style.display = "none"; 
                    document.getElementById("input_nombre_historial").value = ""; 
                    btnConfirmar.textContent = "Confirmar Guardado"; 
                    btnConfirmar.disabled = false;
                }, 2000);

            } else {
                exitoMsg.style.display = "none";
                const errorTexto = typeof result.detail === 'string' ? result.detail : "Error al guardar.";
                errorMsg.textContent = "Error: " + errorTexto;
                errorMsg.style.color = "var(--color-error)";
                errorMsg.style.display = "block";
                btnConfirmar.textContent = "Confirmar Guardado";
                btnConfirmar.disabled = false;
            }
        } catch (e) {
            exitoMsg.style.display = "none";
            errorMsg.textContent = "Error de conexión con el servidor.";
            errorMsg.style.color = "var(--color-error)";
            errorMsg.style.display = "block";
            btnConfirmar.textContent = "Confirmar Guardado";
            btnConfirmar.disabled = false;
        }
    });

    // =========================================================================
    // 4. DESCARGAR PDF
    // =========================================================================
    document.getElementById("btn_descargar").addEventListener("click", async () => {
        const btn = document.getElementById("btn_descargar");
        const estadoAccion = document.getElementById("estado_accion");
        
        btn.disabled = true;
        estadoAccion.textContent = "Generando PDF...";
        estadoAccion.style.color = "var(--texto-principal)";

        try {
            // Obtenemos la selección elegida en el paso 1
            const seleccion = localStorage.getItem("prediccion_pais") || "España";
            
            // Obtenemos el nombre del modelo (hacemos fetch si el usuario no abrió el modal antes)
            let modeloPDF = document.getElementById("info_archivo").textContent;
            if (!modeloPDF || modeloPDF === "") {
                try {
                    const resModelo = await fetch("http://127.0.0.1:8000/api/modelo/info");
                    const infoModelo = await resModelo.json();
                    modeloPDF = infoModelo.archivo_original || "Modelo de IA";
                } catch(e) {
                    modeloPDF = "Modelo por Defecto";
                }
            }

            // Preparamos el nuevo objeto estructurado
            const payloadPDF = {
                seleccion: seleccion,
                modelo_predictivo: modeloPDF,
                titulares: datos.titulares,
                reservas: datos.reservas
            };

            const res = await fetch("http://127.0.0.1:8000/api/predict/descargar_convocatoria_pdf", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payloadPDF) // Enviamos el nuevo objeto
            });
            
            if (!res.ok) throw new Error("Fallo al generar el documento");

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            // Damos un nombre chulo y dinámico a la descarga
            a.download = `Convocatoria_${seleccion.replace(/\s+/g, '_')}_2026.pdf`;
            a.click();
            
            estadoAccion.textContent = "Descarga completada";
            estadoAccion.style.color = "var(--color-exito)";
            
            setTimeout(() => {
                estadoAccion.textContent = "";
            }, 2000);

        } catch (e) {
            estadoAccion.textContent = "Error al descargar el PDF";
            estadoAccion.style.color = "var(--color-error)";
        } finally {
            btn.disabled = false;
        }
    });
});

// =========================================================================
// FUNCIONES GLOBALES
// =========================================================================
window.cerrarModal = function(id) {
    document.getElementById(id).style.display = "none";
    if(id === 'modal_guardar') {
        document.getElementById("msg_error_guardar").style.display = "none";
        document.getElementById("msg_exito_guardar").style.display = "none";
        document.getElementById("input_nombre_historial").value = "";
    }
};