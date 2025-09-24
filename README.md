# Centro de Yoga Paz Interior - API

Sistema optimizado de gestión de clases de yoga con enfoque en performance y experiencia de usuario.

## Características Principales

- **Gestión de Clases**: Crear, listar y administrar clases de yoga
- **Sistema de Reservas**: Reservas en tiempo real con control de capacidad
- **Cache Optimizado**: Redis para mejorar tiempos de respuesta
- **Rate Limiting**: Protección contra abuso del API
- **Monitoreo**: Métricas en tiempo real y dashboard
- **Performance**: Optimizado para alta concurrencia

## Instalación

```bash
pip install -r requirements.txt

uvicorn main:app --reload