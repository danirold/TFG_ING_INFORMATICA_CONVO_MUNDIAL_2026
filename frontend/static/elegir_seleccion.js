document.addEventListener("DOMContentLoaded", () => {
    //Buscamos en el HTML el elemento que tenga el id="formulario_seleccion"
    const formulario = document.getElementById("formulario_seleccion");

    //Buscamos en el HTML el elemento con id="mensaje_respuesta"
    const mensajeRespuesta = document.getElementById("mensaje_respuesta");

    //Cuando el usuario haga clic en ese formulario, se ejecuta lo siguiente
    formulario.addEventListener("submit", (evento) => {
        //Para no recargar la pagina
        evento.preventDefault();

        //Recogemos la seleccion elegida para la prediccion de la convocatoria
        const seleccionElegida = document.getElementById("pais").value;

        //Comprobamos si el usuario intenta confirmar selección sin haber seleccionado ninguna
        if (seleccionElegida === "") {
            mensajeRespuesta.textContent = "Error: Debes elegir una selección válida.";
            mensajeRespuesta.style.color = "var(--color-error)";
            return;
        }

        //En caso de que haya elegido una, guardamos la elección temporalmente en el navegador
        localStorage.setItem("prediccion_pais", seleccionElegida);
        
        mensajeRespuesta.textContent = `Selección de ${seleccionElegida} confirmada. Pasando al siguiente paso...`;
        mensajeRespuesta.style.color = "var(--color-exito)";

        // Redirigimos al paso 2 después de 2 segundos (CU 3.2: Añadir base de datos)
        setTimeout(() => {
            window.location.href = "/anadir_bd_prediccion";
        }, 2000);
    });
});

