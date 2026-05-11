document.addEventListener("DOMContentLoaded", () => {
    // Recuperar contexto
    const email = localStorage.getItem("email_usuario") || "usuario@ejemplo.com";
    let seleccion = localStorage.getItem("prediccion_pais") || "ESP";
    if (seleccion === "España") seleccion = "ESP";

    const tipoBd = localStorage.getItem("prediccion_tipo_bd") || "defecto";
    let filtros = { edad_min: null, edad_max: null, posiciones_excluidas: [], ligas_incluidas: [] };

    try {
        const filtrosGuardados = localStorage.getItem("prediccion_filtros");
        if (filtrosGuardados) filtros = JSON.parse(filtrosGuardados);
    } catch (e) { console.warn("No se pudieron cargar los filtros."); }

    // Mostrar resumen inicial
    document.getElementById("res_sel").textContent = seleccion === "ESP" ? "España" : seleccion;
    document.getElementById("res_bd").textContent = tipoBd === "defecto" ? "Oficial (Defecto)" : "Personalizada (Propia)";

    const btnGenerar = document.getElementById("btn_generar");
    const mensajeEstado = document.getElementById("mensaje_estado");
    
    // Contenedor para el CU 3.5
    const contenedorVisualizar = document.getElementById("contenedor_visualizar");
    const btnVisualizar = document.getElementById("btn_visualizar");

    // Generar convocatoria
    btnGenerar.addEventListener("click", async () => {
        // Estado de carga
        mensajeEstado.style.display = "block";
        mensajeEstado.textContent = "Generando convocatoria. Por favor, espere...";
        mensajeEstado.style.color = "var(--texto-principal)";
        mensajeEstado.style.fontWeight = "600";
        
        btnGenerar.disabled = true;
        contenedorVisualizar.style.display = "none";

        const datosEnvio = { email: email, seleccion: seleccion, tipo_bd: tipoBd, filtros: filtros };

        try {
            const respuesta = await fetch("http://127.0.0.1:8000/api/predict/generar_convocatoria", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datosEnvio)
            });

            const data = await respuesta.json();

            if (respuesta.ok) {
                // Éxito
                mensajeEstado.textContent = "Convocatoria generada correctamente. Lista para su visualizacion.";
                mensajeEstado.style.color = "var(--color-exito)";
                
                // GUARDAMOS LOS RESULTADOS PARA EL CU 3.5
                localStorage.setItem("prediccion_resultados", JSON.stringify(data));
                
                // Damos paso al CU 3.5 mostrando el botón
                contenedorVisualizar.style.display = "block";
            } else {
                mensajeEstado.textContent = "Error: " + (data.detail || "No se pudo generar la prediccion.");
                mensajeEstado.style.color = "var(--color-error)";
                btnGenerar.disabled = false;
            }
        } catch (error) {
            mensajeEstado.textContent = "Error de conexion con el servidor de IA.";
            mensajeEstado.style.color = "var(--color-error)";
            btnGenerar.disabled = false;
        }
    });

    // Movemos al CU 3.5: Visualizar resultados
    btnVisualizar.addEventListener("click", () => {
        window.location.href = "/visualizar_resultados";
    });
});