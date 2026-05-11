document.addEventListener("DOMContentLoaded", () => {
    const botonCerrar = document.getElementById("boton_cerrar_sesion");
    const mensajeHTML = document.getElementById("mensaje_respuesta");

    if (botonCerrar) {
        botonCerrar.addEventListener("click", () => {
            // Borramos la "sesión" (el email guardado)
            localStorage.removeItem("email_usuario");

            // Mostramos mensaje
            mensajeHTML.style.color = "var(--color-error)";
            mensajeHTML.textContent = "Cerrando sesion. Por favor, espere...";

            // Redirigimos tras 2 segundos
            setTimeout(() => {
                window.location.href = "/iniciar_sesion_adm";
            }, 2000);
        });
    }
});