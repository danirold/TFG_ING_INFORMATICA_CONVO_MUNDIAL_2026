document.addEventListener("DOMContentLoaded", () => {
    const emailUsuario = localStorage.getItem("email_usuario");
    const seleccionElegida = localStorage.getItem("prediccion_pais");       

    // Mostramos la selección que eligió en el paso anterior
    document.getElementById("seleccion_mostrada").textContent = seleccionElegida;

    // Lógica para mostrar/ocultar el input de archivo
    const radios = document.getElementsByName("opcion_bd");
    const divSubirArchivo = document.getElementById("div_subir_archivo");
    const inputArchivo = document.getElementById("archivo_bd");

    radios.forEach(radio => {
        radio.addEventListener("change", (e) => {
            if (e.target.value === "propia") {
                divSubirArchivo.style.display = "block";
                inputArchivo.setAttribute("required", "true"); // Lo hacemos obligatorio
            } else {
                divSubirArchivo.style.display = "none";
                inputArchivo.removeAttribute("required");
                inputArchivo.value = ""; // Limpiamos si se arrepiente
            }
        });
    });

    // Lógica al enviar el formulario
    const formulario = document.getElementById("formulario_bd_prediccion");
    const mensajeRespuesta = document.getElementById("mensaje_respuesta");

    formulario.addEventListener("submit", async (evento) => {
        evento.preventDefault();

        const opcionSeleccionada = document.querySelector('input[name="opcion_bd"]:checked').value;

        // Si elige la base de datos por defecto
        if (opcionSeleccionada === "defecto") {
            localStorage.setItem("prediccion_tipo_bd", "defecto");
            mensajeRespuesta.textContent = "Usando base de datos por defecto. Pasando al siguiente paso...";
            mensajeRespuesta.style.color = "var(--color-exito)";
            
            setTimeout(() => {
                window.location.href = "/filtros_convocatoria"; // Irá al CU 3.3
            }, 2000);
            return;
        }

        // Si elige subir la suya propia 
        const archivo = inputArchivo.files[0];
        if (!archivo) {
            mensajeRespuesta.textContent = "Por favor, selecciona un archivo CSV.";
            mensajeRespuesta.style.color = "var(--color-error)";
            return;
        }

        const formData = new FormData();
        formData.append("archivo", archivo);
        formData.append("email", emailUsuario); // Pasamos el email para que el backend lo asocie

        mensajeRespuesta.textContent = "Cargando y validando archivo...";
        mensajeRespuesta.style.color = "var(--texto-principal)";

        try {
            const respuesta = await fetch("http://127.0.0.1:8000/api/users/subir_bd_prediccion", {
                method: "POST",
                body: formData
            });

            const data = await respuesta.json();

            if (respuesta.ok) {
                // Guardamos en la sesión que usará su propia BD
                localStorage.setItem("prediccion_tipo_bd", "propia");
                mensajeRespuesta.textContent = data.mensaje; // "Base de datos cargada y validada correctamente"
                mensajeRespuesta.style.color = "var(--color-exito)";
                
                setTimeout(() => {
                    window.location.href = "/filtros_convocatoria"; // Irá al CU 3.3
                }, 2000);
            } else {
                mensajeRespuesta.textContent = "Error: " + (data.detail || "No se pudo cargar el archivo.");
                mensajeRespuesta.style.color = "var(--color-error)";
            }
        } catch (error) {
            console.error("Error en la petición:", error);
            mensajeRespuesta.textContent = "Error de conexión con el servidor.";
            mensajeRespuesta.style.color = "var(--color-error)";
        }
    });
});