document.addEventListener("DOMContentLoaded", () => {
    const botonCerrar = document.getElementById("boton_cerrar_sesion");
    const mensajeHTML = document.getElementById("mensaje_respuesta");

    if (botonCerrar) {
        botonCerrar.addEventListener("click", () => {
            // Borramos la "sesión" (el email guardado)
            localStorage.removeItem("email_usuario");

            // Mostramos mensaje de cierre de sesión
            mensajeHTML.style.color = "var(--color-error)";
            mensajeHTML.textContent = "Cerrando sesión. Por favor, espere...";

            // Redirigimos a la pantalla de inicio de sesión tras 2 segundos
            setTimeout(() => {
                window.location.href = "/iniciar_sesion";
            }, 2000);
        });
    }
});



