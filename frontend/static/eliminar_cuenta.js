document.addEventListener("DOMContentLoaded", () => {
    const emailUsuario = localStorage.getItem("email_usuario");
    const botonConfirmar = document.getElementById("boton_confirmar_eliminar");
    const mensajeHTML = document.getElementById("mensaje_respuesta");

    botonConfirmar.addEventListener("click", async () => {
        // Bloqueamos el botón y avisamos al usuario
        botonConfirmar.disabled = true;
        mensajeHTML.textContent = "Procesando...";
        mensajeHTML.style.color = "var(--texto-principal)";

        const datosEnviar = { email: emailUsuario };

        try {
            // Hacemos la petición DELETE
            const respuesta = await fetch("http://127.0.0.1:8000/api/users/eliminar_cuenta", {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datosEnviar)
            });

            const data = await respuesta.json();

            if (respuesta.ok) {
                mensajeHTML.style.color = "var(--color-exito)";
                mensajeHTML.textContent = "Cuenta eliminada correctamente.";

                // Borramos los datos de sesión del navegador
                localStorage.removeItem("email_usuario");

                // Redirigimos al inicio de sesión tras 2 segundos
                setTimeout(() => {
                    window.location.href = "/iniciar_sesion";
                }, 2000);

            } else {
                mensajeHTML.style.color = "var(--color-error)";
                mensajeHTML.textContent = "Error: " + (data.detail || "No se pudo eliminar la cuenta.");
                botonConfirmar.disabled = false;
            }

        } catch (error) {
            console.error(error);
            mensajeHTML.style.color = "var(--color-error)";
            mensajeHTML.textContent = "Error de conexión con el servidor.";
            botonConfirmar.disabled = false;
        }
    });
});