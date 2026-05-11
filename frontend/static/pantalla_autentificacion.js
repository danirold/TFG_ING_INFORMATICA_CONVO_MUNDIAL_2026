document.addEventListener("DOMContentLoaded", () => {

    const botonIniciarSesionAdm = document.getElementById("boton_iniciar_sesion_adm");
    const botonIniciarSesionUsu = document.getElementById("boton_iniciar_sesion_usu");

    if (botonIniciarSesionAdm) {
        botonIniciarSesionAdm.addEventListener("click", () => {
            window.location.href = "/iniciar_sesion_adm"; 
        });
    }

    if (botonIniciarSesionUsu) {
        botonIniciarSesionUsu.addEventListener("click", () => {
            window.location.href = "/iniciar_sesion"; 
        });
    }
});