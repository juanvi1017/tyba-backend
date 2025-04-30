# Tyba Backend - Django REST Framework

Este proyecto es una API REST desarrollada con Django REST Framework y Docker. Incluye autenticación, configuración inicial y comandos personalizados.

## 🐳 Requisitos

- Docker
- Docker Compose

## 🚀 Instalación y ejecución

Sigue estos pasos para ejecutar el proyecto en local usando Docker:

---

### 1. Clonar el repositorio


- git clone https://github.com/juanvi1017/tyba-backend.git
- cd tu_repositorio (tyba-backend)

### 2. Archivos env
Asegúrate de tener un archivo .envs/.env con las variables necesarias. Un ejemplo mínimo puede ser:

SECRET_KEY='super-secret-key'
DJANGO_DEBUG='True'
API_KEY_GOOGLE='super-secret-key'

### 3. Construir la imagen de Docker y levantar el contenedor

docker-compose -f .\docker-compose.yml up --build

### 4. Ejecutar migraciones
Al levantar el contenedor mostrara lo siguiente al finalizar  "Dependency on app with no migrations: %s" % key[0]"

1. Para solucionar ese mensaje corremos migraciones, abrimos una nueva terminal y nos dirigimos al repositorio del proyecto y ejecutamos los siguientes comandos en el siguiente orden cada uno:
- docker compose exec app python manage.py makemigrations
- docker compose exec app python manage.py migrate
- docker compose exec app python manage.py initial_configurations
- docker compose exec app python manage.py initial_process


### 5. Crear usuario administrador por defecto
1. donde el usuario es admin y la clave es 123456789PH#
- docker compose exec app python manage.py create_user_admin admin 123456789PH#

### 6. Por ultimo reiniciamos nuestro contenedor

- docker compose restart app

o puedes detenerlo y volverlo a subir con
- docker-compose -f .\docker-compose.yml up
=============================================

Listo ya hemos terminado con la configuracion inicial y puedes utilizar el servicio 

🛠 Estructura del proyecto
.
├── backend-tyba/           # Código fuente del proyecto Django
├── compose/                # Archivos de configuración Docker
├── .envs/.env              # Variables de entorno
├── docker-compose.yml      # Composición de servicios Docker
└── README.md               # Documentación del proyecto

🧪 Acceso al servidor de desarrollo
http://localhost:8000/



BASE DE DATOS

SQLite es generada de forma automatica por Django


### 7. TEST 

1. Para correr los test despues de terminar la configuración y reiniciar el contenedor utilizar el siguiente comando.

- docker compose exec app python manage.py test

2. Los test estan en la carpeta user_auth -> tests.py
