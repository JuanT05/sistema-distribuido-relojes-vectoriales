# Sistema Distribuido con Relojes Vectoriales

Proyecto desarrollado en Python para simular un sistema distribuido compuesto por tres nodos independientes que utilizan relojes vectoriales para representar relaciones de causalidad y concurrencia entre eventos.

## Descripción

El sistema está compuesto por tres nodos independientes que se ejecutan mediante APIs REST.

Cada nodo mantiene su propio reloj vectorial y puede:

* Generar eventos locales.
* Consultar su estado.
* Enviar mensajes a otros nodos.
* Recibir mensajes de otros nodos.
* Actualizar su reloj vectorial mediante el máximo componente a componente.
* Registrar la evolución de los relojes antes y después de cada evento.

La comunicación entre los nodos se realiza mediante HTTP utilizando mensajes en formato JSON.

## Tecnologías utilizadas

* Python
* FastAPI
* Uvicorn
* Requests
* HTTP
* JSON
* Relojes vectoriales

## Arquitectura

El sistema está compuesto por tres nodos:

| Nodo   | Puerto | Dirección               |
| ------ | -----: | ----------------------- |
| Nodo 1 |   8001 | `http://127.0.0.1:8001` |
| Nodo 2 |   8002 | `http://127.0.0.1:8002` |
| Nodo 3 |   8003 | `http://127.0.0.1:8003` |

Cada posición del reloj vectorial representa un nodo:

```text
[ N1, N2, N3 ]
```

Por ejemplo:

```text
[2, 1, 0]
```

significa que el nodo conoce dos eventos de Nodo 1, un evento de Nodo 2 y ningún evento de Nodo 3.

## Funcionamiento del reloj vectorial

### Evento local

Cuando ocurre un evento local, el nodo incrementa su propia posición del reloj.

Ejemplo:

```text
Antes:    [0, 0, 0]
Después:  [1, 0, 0]
```

### Envío de mensajes

Antes de enviar un mensaje, el nodo incrementa su reloj y envía el vector actualizado junto con el mensaje.

Ejemplo:

```text
Nodo 1:

Antes:    [2, 0, 0]
Después:  [3, 0, 0]
```

### Recepción de mensajes

Cuando un nodo recibe un mensaje, compara su reloj con el reloj recibido utilizando el máximo componente a componente.

Ejemplo:

```text
Reloj actual:      [0, 1, 0]
Reloj recibido:    [3, 0, 0]

Máximo:            [3, 1, 0]

Incremento Nodo 2:
                   [3, 2, 0]
```

## Endpoints principales

### Consultar estado

```http
GET /estado
```

Permite consultar el reloj vectorial y los eventos registrados por el nodo.

### Generar evento local

```http
POST /evento
```

Genera un evento local e incrementa la posición correspondiente del reloj.

### Enviar mensaje

```http
POST /enviar/{destination}
```

Permite enviar un mensaje desde un nodo hacia otro nodo.

Ejemplo:

```text
POST /enviar/2
```

### Recibir mensaje

```http
POST /recibir
```

Endpoint utilizado para recibir mensajes enviados por otros nodos.

### Consultar eventos

```http
GET /eventos
```

Permite consultar el registro de eventos y la evolución del reloj vectorial.

## Instalación

Clonar el repositorio:

```bash
git clone URL_DEL_REPOSITORIO
```

Entrar en la carpeta:

```bash
cd sistema_distribuido
```

Crear un entorno virtual:

```bash
python -m venv venv
```

Activar el entorno virtual en Windows:

```powershell
venv\Scripts\activate
```

Instalar las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

El sistema requiere ejecutar los tres nodos de forma simultánea.

### Nodo 1

```bash
python nodo.py 1 8001
```

### Nodo 2

```bash
python nodo.py 2 8002
```

### Nodo 3

```bash
python nodo.py 3 8003
```

Cada nodo estará disponible en su respectivo puerto.

## Documentación de la API

FastAPI genera automáticamente una interfaz Swagger para probar los endpoints.

Nodo 1:

```text
http://127.0.0.1:8001/docs
```

Nodo 2:

```text
http://127.0.0.1:8002/docs
```

Nodo 3:

```text
http://127.0.0.1:8003/docs
```

## Causalidad y concurrencia

Los relojes vectoriales permiten determinar la relación entre diferentes eventos.

Si un reloj `A` es menor o igual que un reloj `B` en todos sus componentes y existe al menos un componente estrictamente menor, entonces:

```text
A → B
```

Existe una relación causal entre los eventos.

Si ninguno de los relojes precede al otro, los eventos son concurrentes:

```text
A || B
```

## Registro de eventos

El sistema registra para cada evento:

* Nodo donde ocurrió.
* Tipo de evento.
* Descripción.
* Reloj antes del evento.
* Reloj después del evento.
* Marca de tiempo.

Esto permite analizar la evolución de los relojes vectoriales durante la simulación.

## Estructura del proyecto

```text
sistema_distribuido/
│
├── .gitignore
├── README.md
├── nodo.py
└── requirements.txt
```

La carpeta `venv/` no se incluye en el repositorio porque el entorno virtual se crea localmente en cada computador.

## Autor

Proyecto académico desarrollado para la asignatura de Sistemas Distribuidos.
