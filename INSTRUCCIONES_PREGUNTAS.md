# Instrucciones para Generación de Preguntas

## 📝 Archivos Modificados

### 1. `execute_rag.py` - RAG Dinámico
- ✅ Ahora acepta queries dinámicamente
- ✅ Función `execute_rag_for_query(query)` para uso programático
- ✅ Puede ejecutarse desde línea de comandos o importarse

### 2. `generate_base_questions.py` - Generación Masiva
- ✅ Genera preguntas para todos los 48 temas de Ciencia y Tecnología
- ✅ Procesa 6 grados (1º a 6º) con 8 temas cada uno
- ✅ Genera 5 preguntas por tema (total: 240 preguntas)
- ✅ Crea archivo SQL con INSERTs para la tabla Pregunta

## 🚀 Cómo Usar

### Opción 1: Ejecutar RAG para una query específica
```bash
# Desde línea de comandos
python execute_rag.py "Ciencia y Tecnología - Primer Grado - Reconocemos las plantas como seres vivos - 3 preguntas"

# Sin argumentos (usa query por defecto)
python execute_rag.py
```

### Opción 2: Generar todas las preguntas masivamente
```bash
python generate_base_questions.py
```

## 📊 Estructura de IDs

Los `id_tipo` se asignan secuencialmente del 1 al 48:

### Primer Grado (IDs 1-8)
1. Reconocemos las plantas como seres vivos
2. Compartimos lo que sabemos sobre los animales
3. Aprendemos sobre los alimentos y la función de nutrición
4. Reconocemos los objetos como materia y experimentamos sus estados y mezclas
5. Comprendemos que el sol es fuente de luz y calor
6. Descubrimos que las fuerzas están presentes en las personas y en los animales
7. Exploramos nuestro planeta Tierra
8. Conocemos las funciones de relación y de reproducción

### Segundo Grado (IDs 9-16)
9. Estudiamos las plantas y sus partes
10. Conocemos los animales, su hábitat y su ciclo de vida
... (continúa secuencialmente)

### ... hasta Sexto Grado (IDs 41-48)

## 📄 Archivo SQL Generado

El script `generate_base_questions.py` creará:
- **Archivo**: `bd/preguntas_generated.sql`
- **Contenido**: INSERTs para la tabla Pregunta
- **Formato**: 
```sql
INSERT INTO Pregunta (tipo, id_tipo, pregunta, alternativa_A, alternativa_B, alternativa_C, alternativa_D, alternativa_correcta) VALUES (
    'Tema',
    '1',
    'Pregunta específica sobre plantas...',
    'Alternativa A',
    'Alternativa B', 
    'Alternativa C',
    'Alternativa D',
    2
);
```

## ⚙️ Configuración Requerida

Antes de ejecutar, asegúrate de tener:

1. **Variables de entorno** configuradas:
```bash
GOOGLE_API_KEY=tu_google_api_key
```

2. **ChromaDB** inicializado:
```bash
# Ejecutar primero
python rag/process_data.py
```

3. **Dependencias** instaladas:
```bash
pip install -r requirements.txt
```

## 🎯 Características del Sistema

### `execute_rag.py`
- ✅ **Entrada dinámica**: Acepta cualquier query en formato estándar
- ✅ **Selección automática**: Elige la colección ChromaDB correcta según área y grado
- ✅ **Formato JSON**: Respuesta estructurada lista para base de datos
- ✅ **Manejo de errores**: Validación y reportes detallados

### `generate_base_questions.py`
- ✅ **Procesamiento masivo**: 48 temas x 5 preguntas = 240 preguntas
- ✅ **Mapeo automático**: IDs secuenciales del 1 al 48
- ✅ **Limpieza de datos**: Escapado de caracteres especiales para SQL
- ✅ **Reporte de progreso**: Feedback en tiempo real del procesamiento
- ✅ **Manejo de errores**: Continúa procesando aunque falle un tema

## 📈 Estimación de Tiempo

- **Una query individual**: ~10-30 segundos
- **Generación completa (48 temas)**: ~20-40 minutos
- **Depende de**: Velocidad de Google Gemini API

## 🔄 Flujo de Trabajo Recomendado

1. **Configurar entorno**:
```bash
# Variables de entorno en .env
GOOGLE_API_KEY=tu_key
```

2. **Procesar PDFs**:
```bash
python rag/process_data.py
```

3. **Generar preguntas**:
```bash
python rag/generate_base_questions.py
```

4. **Ejecutar SQL**:
```bash
# En Supabase SQL Editor
-- Ejecutar contenido de bd/preguntas_generated.sql
```

5. **Verificar API**:
```bash
python run_api.py
# Probar endpoints de preguntas
```
