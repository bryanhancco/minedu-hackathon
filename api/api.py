from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from bd.dto import (
    EstudianteCreate, RespuestaCreate, TemaBasico, TemaDetallado,
    PreguntaResponse, RespuestaEstudianteResponse, EstudianteCreateResponse,
    TipoPreguntaEnum, GradoEnum, PersonajeResponse, InvestigadorResponse
)
from bd.bd_supabase import supabase
from datetime import datetime

app = FastAPI(title="MINEDU RAG API", description="API para sistema educativo MINEDU", version="1.0.0")

@app.get("/getTodosTemas", response_model=List[TemaBasico])
async def get_todos_temas(grado: GradoEnum):
    """
    Obtiene todos los temas de un grado específico
    """
    try:
        response = supabase.table("tema").select("nombre, descripcion, imagen").eq("grado", grado.value).execute()
        
        if not response.data:
            return []
        
        temas = []
        for tema in response.data:
            temas.append(TemaBasico(
                tema=tema["nombre"],
                descripcion=tema["descripcion"],
                imagen=tema["imagen"]
            ))
        
        return temas
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/getTemaEspecifico", response_model=TemaDetallado)
async def get_tema_especifico(grado: GradoEnum, id_tema: int):
    """
    Obtiene un tema específico con sus personajes e investigadores
    """
    try:
        # Obtener tema
        tema_response = supabase.table("tema").select("nombre, descripcion, imagen").eq("grado", grado.value).eq("id", id_tema).execute()
        
        if not tema_response.data:
            raise HTTPException(status_code=404, detail="Tema no encontrado")
        
        tema_data = tema_response.data[0]
        
        # Obtener personajes
        personajes_response = supabase.table("personaje").select("nombre, descripcion, imagen").eq("id_tema", id_tema).execute()
        personajes = {}
        if personajes_response.data:
            for i, personaje in enumerate(personajes_response.data, 1):
                personajes[i] = PersonajeResponse(
                    nombre=personaje["nombre"],
                    descripcion=personaje["descripcion"],
                    imagen=personaje["imagen"]
                )
        
        # Obtener investigadores
        investigadores_response = supabase.table("investigador").select("nombres, sexo, descripcion, es_provincia, enlace_renacyt, area, imagen").eq("id_tema", id_tema).execute()
        investigadores = {}
        if investigadores_response.data:
            for i, investigador in enumerate(investigadores_response.data, 1):
                investigadores[i] = InvestigadorResponse(
                    nombres=investigador["nombres"],
                    sexo=investigador["sexo"],
                    descripcion=investigador["descripcion"],
                    es_provincia=investigador["es_provincia"],
                    enlace_renacyt=investigador["enlace_renacyt"],
                    area=investigador["area"],
                    imagen=investigador["imagen"]
                )
        
        return TemaDetallado(
            tema=tema_data["nombre"],
            descripcion=tema_data["descripcion"],
            imagen=tema_data["imagen"],
            personajes=personajes,
            investigadores=investigadores
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/getAllPreguntas", response_model=List[PreguntaResponse])
async def get_all_preguntas(tipo: TipoPreguntaEnum, id_tipo: str, id_estudiante: int):
    """
    Obtiene todas las preguntas de un tipo específico con estado basado en si el estudiante las respondió correctamente
    """
    try:
        # Obtener todas las preguntas del tipo especificado
        preguntas_response = supabase.table("pregunta").select("id, pregunta, alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_correcta").eq("tipo", tipo.value).eq("id_tipo", id_tipo).execute()
        
        if not preguntas_response.data:
            return []
        
        preguntas = []
        for pregunta in preguntas_response.data:
            # Verificar si el estudiante respondió correctamente esta pregunta AL MENOS UNA VEZ
            # (puede haber múltiples respuestas incorrectas, pero si al menos una es correcta, estado = True)
            respuesta_correcta = supabase.table("respuesta").select("id").eq("id_pregunta", pregunta["id"]).eq("id_estudiante", id_estudiante).eq("resultado", True).execute()
            
            # El estado es True si existe al menos una respuesta correcta para esta pregunta
            # Sin importar cuántas respuestas incorrectas haya tenido antes
            estado_respondida_correctamente = len(respuesta_correcta.data) > 0
            
            preguntas.append(PreguntaResponse(
                pregunta=pregunta["pregunta"],
                alternativa_a=pregunta["alternativa_a"],
                alternativa_b=pregunta["alternativa_b"],
                alternativa_c=pregunta["alternativa_c"],
                alternativa_d=pregunta["alternativa_d"],
                alternativa_correcta=pregunta["alternativa_correcta"],
                estado=estado_respondida_correctamente
            ))
        
        return preguntas
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/getPreguntasPaginado", response_model=List[PreguntaResponse])
async def get_preguntas_paginado(tipo: TipoPreguntaEnum, id_tipo: str, paginado: int = Query(..., ge=1), id_estudiante: int = Query(...)):
    """
    Obtiene preguntas paginadas de un tipo específico con estado basado en si el estudiante las respondió correctamente
    """
    try:
        # Configurar paginación (10 preguntas por página)
        page_size = 10
        offset = (paginado - 1) * page_size
        
        # Obtener preguntas paginadas del tipo especificado
        preguntas_response = supabase.table("pregunta").select("id, pregunta, alternativa_a, alternativa_b, alternativa_c, alternativa_d, alternativa_correcta").eq("tipo", tipo.value).eq("id_tipo", id_tipo).range(offset, offset + page_size - 1).execute()
        
        if not preguntas_response.data:
            return []
        
        preguntas = []
        for pregunta in preguntas_response.data:
            # Verificar si el estudiante respondió correctamente esta pregunta AL MENOS UNA VEZ
            # (puede haber múltiples respuestas incorrectas, pero si al menos una es correcta, estado = True)
            respuesta_correcta = supabase.table("respuesta").select("id").eq("id_pregunta", pregunta["id"]).eq("id_estudiante", id_estudiante).eq("resultado", True).execute()
            
            # El estado es True si existe al menos una respuesta correcta para esta pregunta
            # Sin importar cuántas respuestas incorrectas haya tenido antes
            estado_respondida_correctamente = len(respuesta_correcta.data) > 0
            
            preguntas.append(PreguntaResponse(
                pregunta=pregunta["pregunta"],
                alternativa_a=pregunta["alternativa_a"],
                alternativa_b=pregunta["alternativa_b"],
                alternativa_c=pregunta["alternativa_c"],
                alternativa_d=pregunta["alternativa_d"],
                alternativa_correcta=pregunta["alternativa_correcta"],
                estado=estado_respondida_correctamente
            ))
        
        return preguntas
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/getAllRespuestas", response_model=List[RespuestaEstudianteResponse])
async def get_all_respuestas(id_estudiante: int):
    """
    Obtiene todas las respuestas de un estudiante específico
    """
    try:
        # Hacer join entre Respuesta y Pregunta para obtener el texto de la pregunta
        response = supabase.table("respuesta").select("id_pregunta, resultado, tiempo_inicio_pregunta, tiempo_envio_respuesta, Pregunta(pregunta)").eq("id_estudiante", id_estudiante).execute()
        
        if not response.data:
            return []
        
        respuestas = []
        for respuesta in response.data:
            # Calcular duración en segundos
            inicio = datetime.fromisoformat(respuesta["tiempo_inicio_pregunta"].replace('Z', '+00:00'))
            envio = datetime.fromisoformat(respuesta["tiempo_envio_respuesta"].replace('Z', '+00:00'))
            duracion = int((envio - inicio).total_seconds())
            
            respuestas.append(RespuestaEstudianteResponse(
                id_pregunta=respuesta["id_pregunta"],
                pregunta=respuesta["Pregunta"]["pregunta"],
                resultado=respuesta["resultado"],
                duracion=duracion
            ))
        
        return respuestas
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.post("/enviarRespuesta")
async def enviar_respuesta(respuesta: RespuestaCreate):
    """
    Envía una respuesta de un estudiante
    """
    try:
        response = supabase.table("respuesta").insert({
            "id_pregunta": respuesta.id_pregunta,
            "id_estudiante": respuesta.id_estudiante,
            "resultado": respuesta.resultado,
            "tiempo_inicio_pregunta": respuesta.tiempo_inicio_pregunta.isoformat(),
            "tiempo_envio_respuesta": respuesta.tiempo_envio_respuesta.isoformat()
        }).execute()
        
        if response.data:
            return JSONResponse(content={"message": "Respuesta enviada exitosamente"}, status_code=201)
        else:
            raise HTTPException(status_code=400, detail="Error al enviar la respuesta")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.post("/registrarEstudiante", response_model=EstudianteCreateResponse)
async def registrar_estudiante(estudiante: EstudianteCreate):
    """
    Registra un nuevo estudiante
    """
    try:
        response = supabase.table("estudiante").insert({
            "nombre": estudiante.nombre,
            "sexo": estudiante.sexo.value,
            "grado": estudiante.grado.value
        }).execute()
        
        if response.data:
            nuevo_id = response.data[0]["id"]
            return EstudianteCreateResponse(id=nuevo_id)
        else:
            raise HTTPException(status_code=400, detail="Error al registrar el estudiante")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/")
async def root():
    """
    Endpoint de salud de la API
    """
    return {"message": "MINEDU RAG API funcionando correctamente"}

@app.get("/health")
async def health_check():
    """
    Endpoint de diagnóstico para verificar la conexión a la base de datos
    """
    try:
        # Intentar una consulta simple para verificar la conexión
        response = supabase.table("tema").select("count", count="exact").execute()
        
        return {
            "status": "OK",
            "database": "Connected",
            "tables_accessible": True,
            "message": "Conexión a Supabase exitosa"
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "database": "Failed",
            "tables_accessible": False,
            "error": str(e),
            "message": "Error de conexión a Supabase"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
