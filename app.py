import os

from flask import Flask, jsonify, request, render_template
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor

from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # Permite que o frontend acesse a API via CORS

# Função para conectar ao banco de dados PostgreSQL
def get_db_connection():
    try:
        conn = psycopg2.connect(
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"))
        return conn
    except OperationalError as e:
        print("Erro ao conectar ao banco de dados:", e)
        return None  # Retorna None se a conexão falhar

# Rota para renderizar o index.html
@app.route('/')
def home():
    return render_template('index.html')

# Rota para buscar os dados da tabela articulacao_controle_lotes com filtro de município
@app.route('/articulacao', methods=['GET'])
def get_lotes():
    municipio = request.args.get('municipio')  # Obtemos o parâmetro de município da query string

    conn = get_db_connection()
    
    if conn is None:
        return jsonify({"error": "Erro ao conectar ao banco de dados."}), 500  # Retorna um erro 500 se a conexão falhar
    
    cur = conn.cursor()

    # Cria a consulta SQL para obter totais
    query_totais = """
        SELECT 
            COALESCE(SUM(area_km2), 0) AS total_areas,
            COALESCE(SUM(CASE WHEN status IS NULL OR status != 2 THEN area_km2 ELSE 0 END), 0) AS area_a_fazer,
            COALESCE(SUM(CASE WHEN status = 2 THEN area_km2 ELSE 0 END), 0) AS total_revisada
        FROM geoprocessing.articulacao_controle_lotes
    """
    
    # Adiciona filtro para município, se fornecido
    if municipio:
        query_totais += " WHERE municipio = %s"
        cur.execute(query_totais, (municipio,))
    else:
        cur.execute(query_totais)

    # Obtém os totais
    totais = cur.fetchone()
    total_areas = totais[0]
    total_revisadas = totais[2]
    area_a_fazer = totais[1]
    percentage_revised = (total_revisadas / total_areas * 100) if total_areas > 0 else 0

    # Cria a consulta SQL para obter os dados dos revisores
    query_revisores = """
        SELECT 
            revisor,
            COALESCE(SUM(CASE WHEN status = 2 THEN area_km2 ELSE 0 END), 0) AS total_revisada
        FROM geoprocessing.articulacao_controle_lotes
    """

    # Adiciona filtro para município, se fornecido
    if municipio:
        query_revisores += " WHERE municipio = %s"
    query_revisores += " GROUP BY revisor;"

    # Executa a consulta para os revisores
    if municipio:
        cur.execute(query_revisores, (municipio,))
    else:
        cur.execute(query_revisores)

    revisores_data = cur.fetchall()

    revisores = []
    for revisor in revisores_data:
        revisor_nome = revisor[0]  # Nome do revisor
        areas_revisadas = revisor[1]
        percentage_revised_revisor = (areas_revisadas / total_areas * 100) if total_areas > 0 else 0

        # Adiciona o revisor com a quantidade de áreas revisadas e a porcentagem, mas ignora se o revisor for NULL
        if revisor_nome is not None:
            revisores.append({
                'revisor': revisor_nome,
                'areas_revisadas': areas_revisadas,
                'percentage_revised': percentage_revised_revisor
            })

    # Fecha a conexão
    cur.close()
    conn.close()

    return jsonify({
        'totalAreas': total_areas,
        'totalRevisedAreas': total_revisadas,
        'areaAFazer': area_a_fazer,
        'percentageRevised': percentage_revised,
        'revisores': revisores
    })

# Rota para buscar todos os municípios únicos
@app.route('/municipios', methods=['GET'])
def get_municipios():
    conn = get_db_connection()
    
    if conn is None:
        return jsonify({"error": "Erro ao conectar ao banco de dados."}), 500  # Retorna um erro 500 se a conexão falhar
    
    cur = conn.cursor()

    # Query para obter os municípios únicos
    query = """
        SELECT DISTINCT(municipio) FROM geoprocessing.articulacao_controle_lotes;
    """
    
    cur.execute(query)
    rows = cur.fetchall()

    # Extrair municípios da consulta
    municipios = [row[0] for row in rows]

    cur.close()
    conn.close()

    # Retornar os dados como JSON
    return jsonify(municipios)

@app.route('/lotes', methods=['GET'])
def get_lotes_por_dia():
    municipio = request.args.get('municipio')  # Obtém o parâmetro de município da query string
    print(f"Município recebido: {municipio}")  # Log para verificar o valor de município

    conn = get_db_connection()

    if conn is None:
        return jsonify({"error": "Erro ao conectar ao banco de dados."}), 500  # Retorna um erro 500 se a conexão falhar

    cur = conn.cursor()

    try:
        # Cria a consulta SQL para obter a quantidade de lotes revisados por dia
        query_lotes_dia = """
            SELECT 
                data_revisao::date AS data,
                m.nm_mun,
                COUNT(*) AS lotes_revisados
            FROM geoprocessing.lotes_ceara l
            INNER JOIN limits.municipios m
            ON m.cd_mun = l.cd_mun
            WHERE status = 1 
        """
        
        # Consulta com filtro de município
        if municipio:
            query_lotes_dia += " AND m.nm_mun = %s"
            cur.execute(query_lotes_dia + " GROUP BY data_revisao::date, m.nm_mun ORDER BY data_revisao::date;", (municipio,))

        # Consulta sem filtro de município
        else:
            cur.execute(query_lotes_dia + " GROUP BY data_revisao::date, m.nm_mun ORDER BY data_revisao::date;")

        lotes_dia = cur.fetchall()
        print(f"Resultados da query: {lotes_dia}")  # Log para verificar os resultados

        data_series = []
        for lote in lotes_dia:
            data_series.append({
                'data': lote[0].strftime('%Y-%m-%d'),
                'lotes_revisados': lote[2]  # Corrigido para usar o terceiro item da tupla
            })

    except Exception as e:
        print(f"Erro durante a execução da consulta: {e}")  # Log do erro
        return jsonify({"error": f"Erro durante a execução da consulta {e}" }), 500
    finally:
        cur.close()
        conn.close()

    return jsonify(data_series)

@app.route('/limites-municipios', methods=['GET'])
def get_limites_municipios():
    conn = get_db_connection()

    if conn is None:
        return jsonify({"error": "Erro ao conectar ao banco de dados."}), 500

    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Etapa 1: Consulta das estatísticas por município (sem geometria)
        query_estatisticas = """
        SELECT 
            ac.municipio,
            COALESCE(SUM(CASE WHEN ac.status = 2 THEN ac.area_km2 ELSE 0 END), 0) / COALESCE(SUM(ac.area_km2), 1) * 100 AS porcentagem_revisada
        FROM geoprocessing.articulacao_controle_lotes ac
        GROUP BY ac.municipio;
        """
        cur.execute(query_estatisticas)
        estatisticas = cur.fetchall()

        # Cria um dicionário para facilitar a busca das porcentagens por município
        estatisticas_dict = {row['municipio']: row['porcentagem_revisada'] for row in estatisticas}

        # Etapa 2: Consulta da geometria dos municípios com maior simplificação
        query_geom = """
        SELECT 
            m.nm_mun AS municipio,
            ST_AsGeoJSON(ST_Transform(ST_Simplify(m.geom, 0.5), 4326)) AS geom
        FROM limits.municipios m;
        """
        cur.execute(query_geom)
        geometrias = cur.fetchall()

        # Construir o GeoJSON com a porcentagem revisada
        geojson = {
            "type": "FeatureCollection",
            "features": []
        }

        for row in geometrias:
            municipio = row['municipio']
            porcentagem_revisada = estatisticas_dict.get(municipio, 0)  # Valor padrão de 0 se não encontrado

            # Adiciona a cor de acordo com a porcentagem revisada
            if porcentagem_revisada == 0:
                cor = "#808080"  # Cinza se não iniciado
            elif porcentagem_revisada <= 10:
                cor = "#FF0000"  # Vermelho (0-10%)
            elif porcentagem_revisada <= 20:
                cor = "#FF4000"  # Gradiente de vermelho para laranja (10-20%)
            elif porcentagem_revisada <= 30:
                cor = "#FF8000"  # Laranja (20-30%)
            elif porcentagem_revisada <= 40:
                cor = "#FFBF00"  # Amarelo alaranjado (30-40%)
            elif porcentagem_revisada <= 50:
                cor = "#FFFF00"  # Amarelo (40-50%)
            elif porcentagem_revisada <= 60:
                cor = "#BFFF00"  # Verde claro (50-60%)
            elif porcentagem_revisada <= 70:
                cor = "#80FF00"  # Verde (60-70%)
            elif porcentagem_revisada <= 80:
                cor = "#40FF00"  # Verde mais escuro (70-80%)
            elif porcentagem_revisada <= 90:
                cor = "#00FF00"  # Verde mais forte (80-90%)
            elif porcentagem_revisada <= 99:
                cor = "#00FF80"  # Verde escuro (90-99%)
            else:
                cor = "#17ad19"

            # Montar a feature GeoJSON
            feature = {
                "type": "Feature",
                "geometry": json.loads(row["geom"]),  # Converte a geometria de texto para objeto JSON
                "properties": {
                    "nome": municipio,
                    "porcentagem_revisada": porcentagem_revisada,
                    "cor": cor
                }
            }
            geojson["features"].append(feature)

        cur.close()
        conn.close()

        return jsonify(geojson)

    except Exception as e:
        print(f"Erro durante a execução da consulta: {e}")
        return jsonify({"error": f"Erro durante a execução da consulta {e}"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9001)
