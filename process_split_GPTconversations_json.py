import re
import os

# Configuración
json_file = 'tu_archivo.json'  # Cambia al nombre de tu JSON
output_dir = 'chunks'  # Carpeta para los chunks
os.makedirs(output_dir, exist_ok=True)
target_size_mb = 5  # Tamaño aproximado por chunk

# Parte 1: Extraer pares en memoria
regex = r'"role":\s*"user".*?"parts":\s*\[\s*"((?:.|\s)*?)"\s*\].*?"role":\s*"assistant".*?"parts":\s*\[\s*"((?:.|\s)*?)"\s*\]'
pairs = []  # Lista de strings con pares completos
with open(json_file, 'r', encoding='utf-8') as f:
    text = f.read()  # Lee todo; si falla por tamaño, divide el JSON manualmente
    for match in re.finditer(regex, text, re.DOTALL | re.IGNORECASE):
        user_prompt = match.group(1).strip()
        assistant_response = match.group(2).strip()
        if user_prompt and assistant_response:
            pair_text = f"User Prompt: {user_prompt}\nAssistant Response: {assistant_response}\n---"
            pairs.append(pair_text)

print(f'Extraídos {len(pairs)} pares en memoria.')

# Parte 2: Dividir los pares en memoria en chunks
current_chunk = []
current_size = 0
chunk_num = 1

for pair_text in pairs:
    pair_size = len(pair_text.encode('utf-8')) / (1024 * 1024)  # Tamaño en MB
    
    # Si agregar este par supera el target, guarda el chunk actual
    if current_size + pair_size > target_size_mb and current_chunk:
        chunk_file = os.path.join(output_dir, f'chunk_{chunk_num}.txt')
        with open(chunk_file, 'w', encoding='utf-8') as out:
            out.write('\n'.join(current_chunk) + '\n')
        print(f'Chunk {chunk_num} guardado (~{current_size:.2f} MB)')
        chunk_num += 1
        current_chunk = []
        current_size = 0
    
    # Agrega el par al chunk actual
    current_chunk.append(pair_text)
    current_size += pair_size

# Guarda el último chunk
if current_chunk:
    chunk_file = os.path.join(output_dir, f'chunk_{chunk_num}.txt')
    with open(chunk_file, 'w', encoding='utf-8') as out:
        out.write('\n'.join(current_chunk) + '\n')
    print(f'Chunk {chunk_num} guardado (~{current_size:.2f} MB)')

print('Proceso completado: Extracción y división directamente en la carpeta "chunks".')
