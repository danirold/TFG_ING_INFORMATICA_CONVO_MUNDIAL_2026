document.addEventListener("DOMContentLoaded", async () => {
    const tabla = document.getElementById("tabla_historial");
    const cuerpo = document.getElementById("cuerpo_tabla");
    const mensaje = document.getElementById("mensaje_estado");
    
    // Elementos del modal
    const modalBorrado = document.getElementById("modal_confirmar_borrado");
    const textoConfirmacion = document.getElementById("texto_confirmacion_borrado");
    const btnCancelarBorrado = document.getElementById("btn_cancelar_borrado");
    const btnAceptarBorrado = document.getElementById("btn_aceptar_borrado");
    const msgErrorBorrado = document.getElementById("msg_error_borrado");

    // Variables de control
    let idSeleccionado = null;
    let filaSeleccionada = null;
    
    const email = localStorage.getItem("email_usuario");

    if (!email) {
        alert("Sesión no válida.");
        window.location.href = "/iniciar_sesion";
        return;
    }

    // --- CARGA INICIAL DEL HISTORIAL ---
    try {
        const respuesta = await fetch(`http://127.0.0.1:8000/api/users/historial?email=${email}`);
        const datos = await respuesta.json();

        if (respuesta.ok) {
            if (datos.length === 0) {
                mensaje.textContent = "Aún no tienes predicciones guardadas en tu historial.";
                return;
            }

            mensaje.style.display = "none";
            tabla.style.display = "table";

            datos.forEach(item => {
                const fila = document.createElement("tr");
                const fecha = new Date(item.fecha_guardado).toLocaleString('es-ES');

                // AQUI ESTÁ EL CAMBIO: Usamos btn-ghost (blanco) para Ver Detalles
                fila.innerHTML = `
                    <td><strong>${item.nombre_personalizado}</strong></td>
                    <td>${item.seleccion}</td>
                    <td>${fecha}</td>
                    <td>
                        <button class="btn btn-ghost btn-ver" style="padding: 6px 12px; font-size: 0.85rem;">Ver detalles</button>
                        <button class="btn btn-peligro btn-borrar" style="padding: 6px 12px; font-size: 0.85rem; margin-left: 5px;">Eliminar</button>
                    </td>
                `;

                // Acción: Ver Detalles
                fila.querySelector(".btn-ver").addEventListener("click", () => {
                    localStorage.setItem("prediccion_resultados", item.datos_json);
                    localStorage.setItem("seleccion_actual", item.seleccion);
                    localStorage.setItem("nombre_historial_activo", item.nombre_personalizado); 
                    window.location.href = "/detalle_historial"; 
                });

                // Acción: Abrir Modal de Borrado
                fila.querySelector(".btn-borrar").addEventListener("click", (e) => {
                    e.stopPropagation();
                    idSeleccionado = item.id;
                    filaSeleccionada = fila;
                    
                    textoConfirmacion.innerHTML = `¿Estás seguro de que quieres eliminar la convocatoria <strong>"${item.nombre_personalizado}"</strong>?<br><br><span style="color: #64748B; font-size: 0.9em;">Esta acción es permanente y no se podrá deshacer.</span>`;
                    msgErrorBorrado.style.display = "none";
                    modalBorrado.style.display = "flex";
                });

                cuerpo.appendChild(fila);
            });
        } else {
            throw new Error();
        }
    } catch (e) {
        mensaje.textContent = "Error al conectar con el servidor.";
        mensaje.style.color = "var(--color-error)";
    }

    // --- LÓGICA DEL MODAL ---

    btnCancelarBorrado.addEventListener("click", () => {
        modalBorrado.style.display = "none";
        idSeleccionado = null;
    });

    btnAceptarBorrado.addEventListener("click", async () => {
        if (!idSeleccionado) return;

        btnAceptarBorrado.disabled = true;
        btnAceptarBorrado.textContent = "Borrando...";

        try {
            const res = await fetch(`http://127.0.0.1:8000/api/users/historial/${idSeleccionado}?email=${email}`, {
                method: 'DELETE'
            });
            
            if (res.ok) {
                filaSeleccionada.remove();
                modalBorrado.style.display = "none";
                
                // Si la tabla queda vacía, mostramos el mensaje
                if (cuerpo.children.length === 0) {
                    tabla.style.display = "none";
                    mensaje.style.display = "block";
                    mensaje.style.color = "var(--texto-principal)";
                    mensaje.textContent = "Aún no tienes predicciones guardadas en tu historial.";
                }
            } else {
                const error = await res.json();
                msgErrorBorrado.textContent = "Error: " + (error.detail || "No se pudo borrar.");
                msgErrorBorrado.style.display = "block";
            }
        } catch (error) {
            msgErrorBorrado.textContent = "Error de conexión con el servidor.";
            msgErrorBorrado.style.display = "block";
        } finally {
            btnAceptarBorrado.disabled = false;
            btnAceptarBorrado.textContent = "Confirmar eliminación";
        }
    });
});