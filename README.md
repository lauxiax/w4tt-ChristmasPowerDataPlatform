# ⏳ Evita la procrastinación con Power Automate  
## 🧠 Gestor de tiempo inteligente  
### 👩‍💻 9º Evento Anfitrionas — w4tt (Women for Technical Talks) — 07/06/2025
### 👩‍💻 2º Evento Christmas Power Data Platform — 12/12/2025

Una herramienta diseñada para ayudarte a **enfrentar tus tareas pendientes**, reservando tiempo real en tu **agenda profesional** de forma automatizada y estratégica.

Feliz★* 。 • ˚ ˚ ˛ ˚ ˛ •
•。★Navidad★ 。* 。
° 。 ° ˛˚˛ * _Π_____*。*˚
˚ ˛ •˛•˚ */______/~＼。˚ ˚ ˛
˚ ˛ •˛• ˚ ｜ 田田 ｜門｜ ˚

-----

## 🧩 Componentes de la solución

- 🐍 **API Flask en Python**
- 🚂 **Contenedor desplegado en Railway**
- 🔄 **Flujo automatizado en Power Automate**

---

## 🔗 Integración Planner + Outlook

Desde **Microsoft Power Automate** se realiza una llamada a la **API publicada en Railway**.  
La API:

- 📋 Recoge las **tareas pendientes** de un proyecto en **Microsoft Planner**
- 📅 Consulta los **huecos NO DISPONIBLES** en la agenda de **Outlook**
- 🧠 Aplica reglas de negocio para devolver **slots óptimos** que se pueden reservar como ocupados

---

## ⚙️ Funcionamiento del flujo

1. 🔁 El flujo de Power Automate **llama a la API** con los datos necesarios.
2. 📥 Recoge la **respuesta JSON** con los slots recomendados.
3. 📆 Reserva automáticamente esos **slots en Outlook** como ocupados.
4. 🔐 La API **no gestiona credenciales** ni datos sensibles, solo intercambia JSON estructurado.

---

## 🎯 Objetivo

- ✅ **Forzar la acción** sobre tareas pendientes
- 📆 **Bloquear tiempo real** en la agenda profesional
- 🔄 **Automatizar la gestión del tiempo**
- 🧘‍♀️ **Reducir la procrastinación** con decisiones automatizadas

---
