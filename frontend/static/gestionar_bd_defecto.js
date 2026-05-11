document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_actualizar_bd");
    const mensajeRespuesta = document.getElementById("mensaje_respuesta");

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const inputArchivo = document.getElementById("archivo_bd");
        const archivo = inputArchivo.files[0];

        if (!archivo) {
            mensajeRespuesta.textContent = "Error: Por favor, selecciona un archivo válido.";
            mensajeRespuesta.style.color = "var(--color-error)";
            return;
        }

        // Mensaje de estado mientras carga
        mensajeRespuesta.textContent = "Subiendo archivo...";
        mensajeRespuesta.style.color = "var(--texto-principal)";

        const formData = new FormData();
        formData.append("archivo", archivo);

        try {
            const respuesta = await fetch("http://127.0.0.1:8000/api/admin/actualizar_bd_defecto", {
                method: "POST",
                body: formData
            });

            const data = await respuesta.json();

            if (respuesta.ok) {
                // Filtramos emojis por si el backend manda alguno
                const mensajeLimpio = (data.mensaje || "Base de datos actualizada correctamente.").replace(/[^\p{L}\p{N}\s\-_.]/gu, '').trim();
                mensajeRespuesta.textContent = mensajeLimpio;
                mensajeRespuesta.style.color = "var(--color-exito)";
                formulario.reset();

                // Esperamos 2 segundos y redirigimos
                setTimeout(() => {
                    window.location.href = "/menu_principal_adm";
                }, 2000);

            } else {
                const errorLimpio = (data.detail || "No se pudo actualizar el archivo.").replace(/[^\p{L}\p{N}\s\-_.]/gu, '').trim();
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