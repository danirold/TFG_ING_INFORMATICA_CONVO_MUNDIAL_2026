document.addEventListener("DOMContentLoaded", () => {
    // Verificamos las precondiciones
    const emailUsuario = localStorage.getItem("email_usuario");
    const seleccionElegida = localStorage.getItem("prediccion_pais");
    const tipoBdElegida = localStorage.getItem("prediccion_tipo_bd");

    // Mostramos los datos de los pasos anteriores para dar contexto
    document.getElementById("seleccion_mostrada").textContent = seleccionElegida;
    document.getElementById("bd_mostrada").textContent = tipoBdElegida === "defecto" ? "Por defecto" : "Propia";

    const formulario = document.getElementById("formulario_filtros");
    const mensajeRespuesta = document.getElementById("mensaje_respuesta");

    formulario.addEventListener("submit", (evento) => {
        evento.preventDefault();

        // Recogemos los valores de edad
        const edadMin = parseInt(document.getElementById("edad_min").value, 10);
        const edadMax = parseInt(document.getElementById("edad_max").value, 10);

        // Comprobar filtros incompatibles
        if (!isNaN(edadMin) && !isNaN(edadMax) && edadMin > edadMax) {
            mensajeRespuesta.textContent = "Error: La edad minima no puede ser mayor que la maxima.";
            mensajeRespuesta.style.color = "var(--color-error)";
            return;
        }

        // Recogemos las posiciones NO marcadas para excluirlas
        const posicionesExcluidas = [];
        document.querySelectorAll('input[name="posicion"]:not(:checked)').forEach((checkbox) => {
            posicionesExcluidas.push(checkbox.value);
        });

        // Recogemos las ligas SI marcadas
        const ligasIncluidas = [];
        document.querySelectorAll('input[name="liga"]:checked').forEach((checkbox) => {
            ligasIncluidas.push(checkbox.value);
        });

        // Creamos un objeto con todos los filtros
        const filtrosAplicados = {
            edad_min: isNaN(edadMin) ? null : edadMin,
            edad_max: isNaN(edadMax) ? null : edadMax,
            posiciones_excluidas: posicionesExcluidas,
            ligas_incluidas: ligasIncluidas
        };

        // Guardamos los filtros en la sesión
        localStorage.setItem("prediccion_filtros", JSON.stringify(filtrosAplicados));

        // Mensaje de confirmación
        mensajeRespuesta.textContent = "Filtros aplicados. Preparando modelo de prediccion...";
        mensajeRespuesta.style.color = "var(--color-exito)";

        // Redirigimos al paso final después de 2 segundos
        setTimeout(() => {
            window.location.href = "/generar_prediccion"; 
        }, 2000);
    });
});