# Sitio web Alberto Guerra — instrucciones de despliegue

**Para:** Jaime (IT)
**De:** Julio (julioernestolv@gmail.com)
**Dominio destino:** `albertoeguerrap.com` (hosting actual con GoDaddy)

---

## Qué te estoy entregando

Una carpeta llamada **`dist-multipage`** que contiene el sitio web completo de Alberto, listo para subir al servidor. Son **15 archivos** en total (HTML, CSS, una imagen, y configuración).

Tres formas de obtener los archivos, elige la que te quede más fácil:

1. **Descarga directa (.zip):** entra a https://github.com/dr-p1n/aglaw-preview → click verde "Code" → "Download ZIP". El zip contiene una carpeta `dist-multipage` dentro — esa es la que necesitas.

2. **Carpeta específica:** https://download-directory.github.io/?url=https://github.com/dr-p1n/aglaw-preview/tree/main/dist-multipage te descarga solo esa carpeta como zip.

3. **Te lo envío por WhatsApp:** dime y te paso el `.zip` directo (138 KB).

---

## Cómo verlo antes de subir (opcional, recomendado)

Si tienes 1 minuto, ábrelo localmente para confirmar que todo se ve bien antes de subirlo:

1. Descomprime la carpeta `dist-multipage` en cualquier lugar (Desktop, Documents, etc.)
2. Doble-click en el archivo `index.html` — se abre en tu navegador
3. Vas a ver la página principal de Alberto. Click en las pestañas del menú (Práctica, Red, Recursos, Perfil) para verificar que todo carga.

---

## Cómo subirlo a GoDaddy

### Si tienes acceso a cPanel:

1. Entra a tu panel de GoDaddy → **cPanel** → **File Manager**
2. Navega a la carpeta **`public_html`** (es el directorio raíz del sitio).
3. ⚠️ **Antes de subir, haz backup** de lo que esté actualmente ahí (la página vieja en WordPress). Selecciona todo, click derecho → Compress → guarda el zip fuera de `public_html` por si necesitas revertir.
4. Una vez respaldado, selecciona todo en `public_html` y bórralo.
5. Click **Upload** (arriba en la barra de cPanel) → selecciona los 15 archivos de la carpeta `dist-multipage` (NO subas la carpeta dist-multipage como tal — sube su **contenido**).
6. Confirma que la estructura de carpetas se mantenga: `/en/` debe quedar como carpeta dentro de `public_html`, igual `/img/`, `/practica/`, `/red/`, `/recursos/`, `/perfil/`.

### Si usas FTP en lugar de cPanel:

Mismo proceso usando FileZilla / Cyberduck. Conecta al servidor de GoDaddy con las credenciales FTP, navega a `public_html`, haz backup, sube los 15 archivos manteniendo la estructura de carpetas.

---

## Checklist post-deploy

Después de subir, abre el sitio en tu navegador (https://albertoeguerrap.com):

- [ ] Página principal carga con foto de Alberto y el texto "Criterio experto. Perspectiva global. Red mundial."
- [ ] El menú de arriba muestra: Práctica · Red · Recursos · Perfil · WhatsApp · ES/EN
- [ ] Click en cada pestaña del menú abre su página sin error 404.
- [ ] Click en el botón verde "WhatsApp" (esquina superior derecha) abre WhatsApp con un mensaje pre-cargado.
- [ ] Click en "EN" arriba a la derecha cambia el sitio a inglés.
- [ ] Bajando hasta el final de la página principal, ves el mapa de Google con la ubicación de la oficina.

Si algo no carga (especialmente CSS o imágenes), probablemente sea un tema de permisos o estructura de carpetas en el servidor. Avísame.

---

## El formulario de contacto

⚠️ **Importante:** la página principal incluye un formulario al final ("¿Su asunto cruza fronteras?"). Ese formulario **no está conectado todavía** a ningún backend — si alguien lo llena ahora, va a fallar.

Eso lo conecto yo desde el lado de Julio. Mientras tanto, los visitantes pueden contactar a Alberto por:
- WhatsApp (botón en el menú + número en sección de contacto)
- Dirección física + horario (también en sección de contacto)
- Google Maps embebido

El formulario queda visible como "preview" del look final. Cuando esté conectado el backend (1-2 horas de trabajo del lado mío), empieza a funcionar sin que tengas que tocar nada en el servidor.

---

## Si surge algo

WhatsApp: +507 [tu número]
Email: julioernestolv@gmail.com

Si tienes que revertir al sitio WordPress, restaura el backup que hiciste en el paso 3 — solo borra lo nuevo y descomprime el viejo en `public_html`.
