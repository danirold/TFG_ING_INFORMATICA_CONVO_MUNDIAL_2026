document.addEventListener("DOMContentLoaded", () => {
    const emailUsuario = localStorage.getItem("email_usuario");
    const mensajeHTML = document.getElementById("mensaje_respuesta");

    document.getElementById("formulario_notificaciones").addEventListener("submit", async (evento) => {
        evento.preventDefault();

        // Creamos el objeto con los datos
        const datosEnviar = {
            email: emailUsuario,
            // .checked devuelve true si está marcado, false si no
            activadas: document.getElementById("opcion_activar").checked 
        };

        try {
            // Enviamos la petición
            const respuesta = await fetch("http://127.0.0.1:8000/api/users/gestionar_notificaciones", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datosEnviar)
            });

            const data = await respuesta.json();

            if (respuesta.ok) {
                // Si todo ha ido bien: usamos nuestra variable de éxito
                mensajeHTML.style.color = "var(--color-exito)";
                mensajeHTML.textContent = "Preferencias actualizadas correctamente.";

                // Esperamos 2 segundos y borramos el mensaje para que quede limpio
                setTimeout(() => {
                    mensajeHTML.textContent = "";
                }, 2000);

            } else {
                // Si hay error, usamos nuestra variable de error
                mensajeHTML.style.color = "var(--color-error)";
                mensajeHTML.textContent = "Error: " + (data.detail || "No se pudieron actualizar las preferencias.");
            }
        } catch (error) {
            mensajeHTML.style.color = "var(--color-error)";
            mensajeHTML.textContent = "Error de conexión con el servidor.";
        }
    });
});