document.addEventListener("DOMContentLoaded", () => {
    // Cargar dinámicamente el nombre del modelo activo al entrar en la página
    const spanModeloActivo = document.getElementById("nombre_modelo_activo");
    if (spanModeloActivo) {
        fetch("http://127.0.0.1:8000/api/modelo/info")
            .then(res => res.json())
            .then(data => {
                // Si existe el campo, lo mostramos. Si no, avisamos de que no hay modelo.
                spanModeloActivo.textContent = data.archivo_original || "Ningún modelo configurado";
            })
            .catch(error => {
                spanModeloActivo.textContent = "Error al cargar estado";
            });
    }

    const formulario = document.getElementById("formulario_actualizar_modelo");
    const mensajeRespuesta = document.getElementById("mensaje_respuesta");

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        // Obtenemos el archivo seleccionado
        const inputArchivo = document.getElementById("archivo_modelo");
        const archivo = inputArchivo.files[0];

        if (!archivo) {
            mensajeRespuesta.textContent = "Error: Por favor, selecciona un archivo.";
            mensajeRespuesta.style.color = "var(--color-error)";
            return;
        }

        // Validamos explícitamente que sea .pkl
        if (!archivo.name.endsWith(".pkl")) {
            mensajeRespuesta.textContent = "Error: El archivo debe tener la extensión .pkl";
            mensajeRespuesta.style.color = "var(--color-error)";
            return;
        }

        // Obtenemos los textos introducidos
        const algoritmo = document.getElementById("meta_algoritmo").value;
        const ventana = document.getElementById("meta_ventana").value;
        const descripcion = document.getElementById("meta_descripcion").value;

        // Preparamos el FormData
        const formData = new FormData();
        formData.append("archivo", archivo); 
        formData.append("algoritmo", algoritmo);
        formData.append("ventana", ventana);
        formData.append("descripcion", descripcion);

        // Mensaje de carga
        mensajeRespuesta.textContent = "Actualizando modelo y metadatos. Por favor, espere...";
        mensajeRespuesta.style.color = "var(--texto-principal)";

        try {
            const respuesta = await fetch("http://127.0.0.1:8000/api/admin/actualizar_modelo_pred", {
                method: "POST",
                body: formData
            });

            const data = await respuesta.json();

            if (respuesta.ok) {
                // Limpiamos de emojis por si acaso
                const mensajeLimpio = (data.mensaje || "Modelo predictivo de IA actualizado correctamente.").replace(/[^\p{L}\p{N}\s\-_.]/gu, '').trim();
                mensajeRespuesta.textContent = mensajeLimpio;
                mensajeRespuesta.style.color = "var(--color-exito)";
                formulario.reset();

                // Esperamos 2 segundos y redirigimos
                setTimeout(() => {
                    window.location.href = "/menu_principal_adm";
                }, 2000);

            } else {
                const errorLimpio = (data.detail || "No se pudo actualizar el modelo.").replace(/[^\p{L}\p{N}\s\-_.]/gu, '').trim();
                mensajeRespuesta.textContent = "Error: " + errorLimpio;
                mensajeRespuesta.style.color = "var(--color-error)";
            }
        } catch (error) {
            console.error("Error en la petición:", error);
            mensajeRespuesta.textContent = "Error de conexión con el servidor.";
            mensajeRespuesta.style.color = "var(--color-error)";
        }
    });
});