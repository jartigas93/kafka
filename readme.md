# Como ejecutar el entorno con Docker

## 1. Ejecutar Docker Compose

Desde la raíz del proyecto, abrí una terminal y ejecuta:

```sh
docker compose up -d
```

---

## 2. Construir la imagen de `api_aircraft_producer`

Ubícate en la carpeta donde está el `Dockerfile` de `api_aircraft_producer`:

```sh
cd api_aircraft_producer
```

Luego, construye la imagen (podes cambiar `my_aircraft_api` por el nombre que prefieras):

```sh
docker build -t my_aircraft_api .
```

---

## 3. Ejecutar el contenedor de `api_aircraft_producer`

Asegúrate de que los servicios necesarios (por ejemplo, Kafka) estén corriendo con Docker Compose.

Luego ejecuta el contenedor, conectándolo a la misma red que tus otros servicios:

```sh
docker run --rm --network=kafka_net my_aircraft_api
```

---

## 4. Variables de entorno

Asegúrate de que el archivo `.env` con las credenciales y configuración esté presente en la carpeta `api_aircraft_producer` antes de construir la imagen, o bien pásalas como variables al ejecutar el contenedor:

```sh
docker run --rm --network=kafka_net my_aircraft_api
```

---

## 5. Detener los servicios

Para detener todos los servicios de Docker Compose:

```sh
docker compose down
```
