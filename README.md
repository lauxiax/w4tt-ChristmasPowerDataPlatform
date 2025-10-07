# EVITA LA PROCRASTINACIÓN CON POWER AUTOMATE
## GESTOR DE TIEMPO INTELIGENTE
## 9º Evento Anfitrionas - w4tt - Women for technical talks - 07/06/2025

### Una herramienta para obligarte a enfrentar tus tareas pendientes, reservando tiempo en tu agenda profesional.

1. API Flask Python, configuración Railway
2. Flujo automatizado Power Automate

Desde Microsoft Power Automate llamamos a la API publicada en un contenedor de Railway. 
La API recoge las tareas pendientes de un proyecto Microsoft PLANNER y los huecos NO DISPONIBLES de la agenda de OUTLOOK.
La API devuelve slots de OUTLOOK a reservar como ocupados en OUTLOOK, habiéndolos distribuidos según las reglas de negocio de la API.

El flujo es quien llama a la API con datos y recoge la respuesta, y es el único que interactúa con Planner y Outlook.
La API solo recibe/envía datos JSON sin credenciales ni datos sensibles.
