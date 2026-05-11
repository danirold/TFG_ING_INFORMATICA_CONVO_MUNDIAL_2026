document.addEventListener("DOMContentLoaded", () => {
    const formulario = document.getElementById("formulario_inicio_sesion_admin");
    const mensajeRespuesta = document.getElementById("mensaje_respuesta");

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const email = document.getElementById("email").value;
        const contraseña = document.getElementById("contraseña").value;

        const datosInicioSesion = {
            email: email,
            contraseña: contraseña
        };

        try {
            const respuesta = await fetch("http://127.0.0.1:8000/api/auth/iniciar_sesion_admin", {
                method: "POST", 
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datosInicioSesion)
            });

            const data = await respuesta.json();

            if (respuesta.ok) {
                // Mensaje limpio y profesional
                mensajeRespuesta.textContent = "Bienvenido. Iniciando sesión como administrador...";
                mensajeRespuesta.style.color = "var(--color-exito)";
                
                if (data.email) {
                    localStorage.setItem("email_usuario", data.email);
                }

                formulario.reset(); 

                setTimeout(() => {
                    mensajeRespuesta.textContent = ""; 
                    window.location.href = "/menu_principal_adm"; 
                }, 2000);

            } else {
                // Filtramos emojis en caso de que vengan de la base de datos
                const errorLimpio = (data.detail || "Datos incorrectos.").replace(/[^\p{L}\p{N}\s\-_.]/gu, '').trim();
                mensajeRespuesta.textContent = "Error: " + errorLimpio;
                mensajeRespuesta.style.color = "var(--color-error)"; 
            }
        
        } catch (error) {
            console.error("Error al conectar con la API:", error);
            mensajeRespuesta.textContent = "Error de conexion con el servidor.";
            mensajeRespuesta.style.color = "var(--color-error)";
        }
    });
});