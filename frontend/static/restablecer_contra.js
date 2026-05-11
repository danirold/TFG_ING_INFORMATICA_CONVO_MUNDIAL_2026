document.addEventListener("DOMContentLoaded", () => {
    
    const formulario = document.getElementById("formulario_nueva_contra");
    const mensajeRespuesta = document.getElementById("mensaje_respuesta");

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const email = document.getElementById("email").value;
        const nueva_contra = document.getElementById("nueva_contraseña").value;
        const nueva_contra_rep = document.getElementById("nueva_contraseña_repetida").value;

        if (nueva_contra !== nueva_contra_rep) {  
            mensajeRespuesta.textContent = "Error: Las contraseñas no coinciden.";
            mensajeRespuesta.style.color = "var(--color-error)";
            return; 
        }

        const cambioContraseña = {
            email: email,
            nueva_contraseña: nueva_contra
        };

        // Mensaje de carga
        mensajeRespuesta.textContent = "Restableciendo contraseña. Por favor, espere...";
        mensajeRespuesta.style.color = "var(--texto-principal)";

        try {
            const respuesta = await fetch("http://127.0.0.1:8000/api/auth/restablecer_contra", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(cambioContraseña)
            });

            const data = await respuesta.json();

            if (respuesta.ok) {
                // Mensaje limpio
                mensajeRespuesta.textContent = "Contraseña restablecida. Redirigiendo a iniciar sesión...";
                mensajeRespuesta.style.color = "var(--color-exito)";
                
                formulario.reset(); 

                setTimeout(() => {
                    mensajeRespuesta.textContent = ""; 
                    window.location.href = "/iniciar_sesion"; 
                }, 2000); 

            } else {
                const errorLimpio = (data.detail || "No se pudo restablecer la contraseña.").replace(/[^\p{L}\p{N}\s\-_.]/gu, '').trim();
                mensajeRespuesta.textContent = `Error: ${errorLimpio}`;
                mensajeRespuesta.style.color = "var(--color-error)";
            }
        } catch (error) {
            console.error("Error al conectar con la API:", error);
            mensajeRespuesta.textContent = "Error de conexión con el servidor.";
            mensajeRespuesta.style.color = "var(--color-error)";
        }
    });
});