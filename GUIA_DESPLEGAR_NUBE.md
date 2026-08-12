# 🚀 Guía para Publicar el Dashboard en Internet

Esta guía te lleva paso a paso para desplegar el dashboard en la nube y obtener una
**URL pública** que puedes compartir con tus compañeros. Funcionará en cualquier
dispositivo (computadora, tablet, celular) y desde cualquier lugar.

Usaremos **Render.com** porque tiene un plan **gratuito** y es el más sencillo para apps Flask.
(Al final hay alternativas: Railway y PythonAnywhere.)

---

## ✅ Lo que ya dejé preparado

No tienes que tocar código. Ya creé todos los archivos que la nube necesita:

| Archivo | Para qué sirve |
|---------|----------------|
| `requirements.txt` | Lista de librerías (sin WeasyPrint, usa reportlab para el PDF → despliegue limpio) |
| `Procfile` | Le dice a la nube cómo arrancar el servidor (gunicorn) |
| `runtime.txt` | Fija la versión de Python (3.12.7) |
| `render.yaml` | Configuración automática para Render |
| `.gitignore` | Evita subir archivos innecesarios (venv, uploads, etc.) |
| `app.py` (ajustado) | Ahora lee el puerto del entorno (`$PORT`) que asigna la nube |

---

## 📋 Requisitos previos (una sola vez)

1. Una cuenta gratis de **GitHub**: https://github.com/signup
2. Una cuenta gratis de **Render**: https://render.com (puedes entrar con tu cuenta de GitHub)
3. Tener **git** instalado (en Mac normalmente ya viene; verifica con `git --version`).

---

## PASO 1 — Subir el proyecto a GitHub

Abre la Terminal en la carpeta del proyecto y ejecuta estos comandos **uno por uno**.

> ⚠️ La carpeta tiene un espacio al final del nombre; el `cd` ya está escrito correctamente abajo.

```bash
cd "/Users/home/Desktop/flujo de caja "
```

```bash
git init
```

```bash
git add .
```

```bash
git commit -m "Dashboard de flujo de caja listo para desplegar"
```

Ahora crea un repositorio vacío en GitHub:
1. Ve a https://github.com/new
2. Nombre: `flujo-de-caja-dashboard` (o el que prefieras)
3. Déjalo en **Public** o **Private** (cualquiera sirve)
4. **NO** marques "Add a README" (ya tenemos archivos)
5. Clic en **Create repository**

GitHub te mostrará una URL como `https://github.com/TU-USUARIO/flujo-de-caja-dashboard.git`.
Cópiala y ejecuta (reemplazando la URL por la tuya):

```bash
git branch -M main
```

```bash
git remote add origin https://github.com/TU-USUARIO/flujo-de-caja-dashboard.git
```

```bash
git push -u origin main
```

Si te pide usuario/contraseña, usa tu usuario de GitHub y un **token** como contraseña
(GitHub → Settings → Developer settings → Personal access tokens → Generate new token).

---

## PASO 2 — Desplegar en Render

1. Entra a https://render.com y haz **Sign in with GitHub**.
2. Clic en **New +** → **Web Service**.
3. Conecta tu repositorio `flujo-de-caja-dashboard`.
4. Render detectará el `render.yaml` automáticamente. Si te pide datos manuales, usa:
   - **Runtime / Language:** Python
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --workers 1 --timeout 120 --bind 0.0.0.0:$PORT`
   - **Instance Type / Plan:** **Free**
5. Clic en **Create Web Service**.
6. Espera 2–4 minutos mientras construye e instala. Cuando veas **"Live"** en verde, ¡está listo!

Render te dará una URL como:
```
https://flujo-de-caja-dashboard.onrender.com
```
**Esa es la URL que compartes con tus compañeros.** ✅

---

## PASO 3 — Usarlo y compartirlo

- Abre la URL en cualquier dispositivo. Se adapta a celular, tablet y computadora.
- Cada persona puede **subir su propio Excel** con el botón "Seleccionar archivo".
- Comparte el enlace por correo, WhatsApp o el chat del equipo.

---

## ⚠️ Notas importantes del plan gratuito de Render

1. **Se "duerme" por inactividad:** si nadie lo usa por ~15 minutos, el servicio se apaga.
   La primera visita después de dormir tarda ~30–50 segundos en despertar. Es normal en el plan free.
2. **El estado no es permanente:** los datos del Excel que subes viven mientras el servicio
   está despierto. Si se reinicia, cada quien vuelve a subir su Excel. (El dashboard está pensado así.)
3. **Actualizar la app:** si cambias algo en el código, solo repite:
   ```bash
   git add . && git commit -m "cambios" && git push
   ```
   Render vuelve a desplegar solo (autoDeploy activado).

---

## 🔁 Alternativas (si prefieres otro servicio)

### Railway (https://railway.app)
- También gratis (con límite de horas/mes). Conecta el repo de GitHub.
- Usa el mismo `Procfile`. Variables: no necesitas configurar `PORT` (Railway lo inyecta).

### PythonAnywhere (https://www.pythonanywhere.com)
- Plan gratuito que **no se duerme**, pero la configuración es más manual (sin `Procfile`;
  se configura una "Web app" Flask apuntando a `app.py`). Bueno si quieres que esté siempre encendido.

---

## 🆘 Si algo falla

- **El build falla:** abre los "Logs" en Render y busca la línea en rojo. Casi siempre es
  una librería; verifica que `requirements.txt` se subió a GitHub.
- **Sale "Application failed to respond":** revisa que el **Start Command** sea exactamente
  el de arriba (con `gunicorn app:app ... $PORT`).
- **El PDF no se genera:** en la nube usa reportlab (ya incluido). Si quisieras el diseño de
  WeasyPrint, requiere librerías del sistema y configuración extra — avísame y te ayudo.

---

*Todo el código y la configuración ya están listos. Solo falta que sigas los pasos con tus
propias cuentas de GitHub y Render, porque el despliegue se hace con tus credenciales.*
