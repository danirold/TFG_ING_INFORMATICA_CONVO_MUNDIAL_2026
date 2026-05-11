document.addEventListener("DOMContentLoaded", async () => {
    // 1. Recuperamos el email actual
    const emailUsuario = localStorage.getItem("email_usuario");
    const mensajeHTML = document.getElementById("mensaje_respuesta");

    // --- PARTE 1: CARGAR DATOS ACTUALES (GET) ---
    try {
        const respuesta = await fetch(`http://127.0.0.1:8000/api/users/obtener_perfil?email=${emailUsuario}`);
        const data = await respuesta.json();

        // Los IDs deben coincidir con tu HTML
        document.getElementById("nombre").value = data.nombre;
        document.getElementById("apellido1").value = data.primer_apellido;   
        document.getElementById("apellido2").value = data.segundo_apellido;  
        document.getElementById("email").value = data.email;
        document.getElementById("contra").value = "********"; 

    } catch (error) {
        console.error("Error al cargar el perfil:", error);
    }

    // --- PARTE 2: GUARDAR CAMBIOS (PUT) ---
    const formulario = document.getElementById("formulario_perfil");

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault(); 

        mensajeHTML.textContent = "Guardando cambios. Por favor, espere...";
        mensajeHTML.style.color = "var(--texto-principal)";

        // Preparamos los datos
        const datosParaEnviar = {
            email_actual: emailUsuario, 
            nombre_nuevo: document.getElementById("nombre").value,
            primer_apellido_nuevo: document.getElementById("apellido1").value,   
            segundo_apellido_nuevo: document.getElementById("apellido2").value,  
            email_nuevo: document.getElementById("email").value,
            contraseña_nueva: document.getElementById("contra").value
        };

        try {
            const respuestaPut = await fetch("http://127.0.0.1:8000/api/users/cambiar_informacion_perfil", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(datosParaEnviar)
            });

            const dataPut = await respuestaPut.json();

            if (respuestaPut.ok) {
                // ÉXITO
                mensajeHTML.style.color = "var(--color-exito)";
                mensajeHTML.textContent = dataPut.mensaje || "Perfil actualizado correctamente."; 

                // Si cambió el email, actualizamos localStorage
                if (datosParaEnviar.email_nuevo !== emailUsuario) {
                    localStorage.setItem("email_usuario", datosParaEnviar.email_nuevo);
                }

                setTimeout(() => location.reload(), 2000);

            } else {
                // ERROR
                mensajeHTML.style.color = "var(--color-error)";
                mensajeHTML.textContent = "Error: " + (dataPut.detail || "No se pudo actualizar el perfil.");
            }

        } catch (error) {
            console.error(error);
            mensajeHTML.style.color = "var(--color-error)";
            mensajeHTML.textContent = "Error de conexión con el servidor.";
        }
    });
});