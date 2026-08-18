# Sitio web Alberto Guerra — instrucciones de actualización

**Para:** Jaime (IT)
**De:** Julio (julioernestolv@gmail.com)
**Dominio:** `albertoeguerrap.com` (hosting GoDaddy)

---

## Qué cambió

El sitio ya está en línea y funcionando — esto **no** es un lanzamiento nuevo, es una actualización de archivos. Cuatro cambios:

1. **Se eliminó el formulario de contacto.** Nunca llegó a conectarse a un backend, así que a quien lo llenaba le salía un error. WhatsApp queda como el único canal de contacto: está en el menú, en el botón del hero, y en la sección Contacto con el número, la dirección y el horario.

2. **Se arregló el mapa de Google.** Una regla de seguridad del servidor (en el archivo `.htaccess`) estaba bloqueando el mapa sin querer, y en su lugar se veía un recuadro vacío en la sección Contacto. Ya está corregido — **pero solo si subes el archivo `.htaccess` nuevo junto con el resto.** Ese archivo es el que trae el arreglo.

3. **Se actualizó la trayectoria de 38 a 39 años.** Estaba desactualizada en varios lugares del sitio (español e inglés).

4. **Se agregó el ícono del sitio.** Es la letra "A" dorada que ahora aparece en la pestaña del navegador y cuando alguien guarda la página en favoritos o en la pantalla de inicio del celular. Antes salía un ícono genérico en blanco.

---

## Descarga

Un solo link, se descarga sin necesidad de tener cuenta de GitHub:

**https://github.com/dr-p1n/aglaw/raw/main/dist-multipage.zip**

Descomprímelo y vas a ver una carpeta `dist-multipage` con **18 archivos** dentro (HTML, CSS, una imagen y la configuración). Si prefieres que te lo pase por WhatsApp, dime y te lo envío.

---

## Cómo verlo antes de subir (opcional, 1 minuto)

1. Descomprime `dist-multipage` en cualquier lugar (Desktop, Documents).
2. Doble-click en `index.html` — se abre en tu navegador.
3. Revisa que el menú funcione (Práctica, Red, Recursos, Perfil).

Ojo: abriéndolo así, con doble-click, **el mapa puede no aparecer** — es normal, el arreglo del mapa depende del `.htaccess`, que solo funciona en el servidor. El mapa se verifica después de subir, no antes.

---

## Cómo subirlo a GoDaddy

1. Entra a tu panel de GoDaddy → **cPanel** → **File Manager**.
2. Navega a la carpeta **`public_html`**.
3. **Haz backup primero.** Selecciona todo lo que está en `public_html`, click derecho → **Compress** → guarda el `.zip` **fuera** de `public_html`. Así puedes revertir si algo sale mal.
4. Borra el contenido de `public_html`.
5. Click **Upload** → sube los **18 archivos** que están *dentro* de `dist-multipage` (sube el **contenido** de la carpeta, no la carpeta misma).
6. Verifica que la estructura de carpetas se mantenga: `/en/`, `/img/`, `/practica/`, `/red/`, `/recursos/`, `/perfil/` deben quedar como carpetas dentro de `public_html`.

⚠️ **El archivo `.htaccess` es importante y es fácil que se te pase**, porque en muchos programas los archivos que empiezan con punto están ocultos. En cPanel File Manager: **Settings** (arriba a la derecha) → marca **"Show Hidden Files (dotfiles)"**. Sin ese archivo el mapa sigue sin aparecer.

Si usas FTP (FileZilla / Cyberduck) en lugar de cPanel: mismo proceso, y ahí también hay que activar la opción de ver archivos ocultos.

---

## Checklist post-deploy

Abre https://albertoeguerrap.com y verifica:

- [ ] La página principal carga con la foto de Alberto y el texto "Criterio experto. Perspectiva global. Red mundial."
- [ ] El menú de arriba muestra: Práctica · Red · Recursos · Perfil · WhatsApp · ES/EN
- [ ] Cada pestaña del menú abre su página sin error 404.
- [ ] El botón "WhatsApp" abre WhatsApp con un mensaje pre-cargado.
- [ ] "EN" arriba a la derecha cambia el sitio a inglés.
- [ ] **Bajando hasta la sección Contacto, se ve el mapa de Google con la oficina** — no un recuadro vacío. Este es el punto clave de esta actualización.
- [ ] Al final de la página principal **ya no hay formulario**. La página cierra con la sección Contacto.
- [ ] En la pestaña del navegador, al lado del título, se ve una **"A" dorada** y no el ícono genérico. Si sigue saliendo el genérico, recarga con `Ctrl+Shift+R` (Windows) o `Cmd+Shift+R` (Mac) — los navegadores guardan ese ícono en caché por bastante tiempo.

Si el mapa sigue saliendo vacío, casi seguro es que el `.htaccess` no se subió. Revísalo con "Show Hidden Files" activado y avísame.

Si algo más no carga (CSS o imágenes), suele ser tema de permisos o estructura de carpetas. Avísame.

---

## Si surge algo

WhatsApp: +507 [tu número]
Email: julioernestolv@gmail.com

Para revertir: borra lo nuevo de `public_html` y descomprime ahí el backup del paso 3.
