# Usamos la imagen base de AWS para el runtime de Python de contenedores Lambda
FROM public.ecr.aws/lambda/python:3.10

# 1. Copia los requisitos e instala las dependencias
COPY lambdas/get_book_by_id/requirements.txt .
RUN pip install -r requirements.txt -t .

# 2. Copia toda la lógica compartida (shared/models, shared/db, shared/utils)
COPY shared/ /var/task/shared/

# 3. Copia el handler específico
# Para la imagen 'get_book_by_id':
COPY lambdas/get_book_by_id/handler.py .

# Establece el punto de entrada (handler.handler es el mismo para todos)
ENV PYTHONPATH "${LAMBDA_TASK_ROOT}:${LAMBDA_TASK_ROOT}/shared"

CMD [ "handler.handler" ]