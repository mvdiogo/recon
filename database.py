import sqlite3
import os
from datetime import datetime
import uuid

class DatabaseManager:
    def __init__(self, db_path="igreja_reconhecimento.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com as tabelas necessárias"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabela de pessoas conhecidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pessoas_conhecidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                idade INTEGER,
                sexo TEXT,
                etnia TEXT,
                telefone TEXT,
                encoding BLOB NOT NULL,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabela de pessoas desconhecidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pessoas_desconhecidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo_temp TEXT UNIQUE NOT NULL,
                encoding BLOB NOT NULL,
                primeira_deteccao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ultima_deteccao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_deteccoes INTEGER DEFAULT 1,
                processado BOOLEAN DEFAULT 0
            )
        ''')
        
        # Tabela de registros de presença
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS registros_presenca (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pessoa_id INTEGER,
                data_presenca TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tipo_pessoa TEXT CHECK(tipo_pessoa IN ('conhecida', 'desconhecida')),
                confianca REAL,
                FOREIGN KEY (pessoa_id) REFERENCES pessoas_conhecidas (id)
            )
        ''')
        
        # Tabela de configurações do sistema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS configuracoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chave TEXT UNIQUE NOT NULL,
                valor TEXT NOT NULL,
                descricao TEXT
            )
        ''')
        
        # Inserir configurações padrão
        cursor.execute('''
            INSERT OR IGNORE INTO configuracoes (chave, valor, descricao) 
            VALUES ('tolerancia_reconhecimento', '0.6', 'Tolerância para reconhecimento facial (0.0 a 1.0)')
        ''')
        
        cursor.execute('''
            INSERT OR IGNORE INTO configuracoes (chave, valor, descricao) 
            VALUES ('intervalo_deteccao', '5', 'Intervalo mínimo entre detecções da mesma pessoa (segundos)')
        ''')
        
        conn.commit()
        conn.close()
        print("Banco de dados inicializado com sucesso!")
    
    def adicionar_pessoa_conhecida(self, nome, idade, sexo, etnia, telefone, encoding):
        """Adiciona uma nova pessoa conhecida ao banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pessoas_conhecidas (nome, idade, sexo, etnia, telefone, encoding)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (nome, idade, sexo, etnia, telefone, encoding))
        
        pessoa_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pessoa_id
    
    def adicionar_pessoa_desconhecida(self, encoding):
        """Adiciona uma nova pessoa desconhecida ao banco de dados"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        codigo_temp = f"TEMP_{uuid.uuid4().hex[:8].upper()}"
        
        cursor.execute('''
            INSERT INTO pessoas_desconhecidas (codigo_temp, encoding)
            VALUES (?, ?)
        ''', (codigo_temp, encoding))
        
        pessoa_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return pessoa_id, codigo_temp
    
    def registrar_presenca(self, pessoa_id, tipo_pessoa, confianca):
        """Registra a presença de uma pessoa"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO registros_presenca (pessoa_id, tipo_pessoa, confianca)
            VALUES (?, ?, ?)
        ''', (pessoa_id, tipo_pessoa, confianca))
        
        conn.commit()
        conn.close()
    
    def obter_pessoas_conhecidas(self):
        """Retorna todas as pessoas conhecidas ativas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, nome, idade, sexo, etnia, telefone, encoding
            FROM pessoas_conhecidas 
            WHERE ativo = 1
        ''')
        
        pessoas = cursor.fetchall()
        conn.close()
        return pessoas
    
    def obter_pessoas_desconhecidas(self):
        """Retorna todas as pessoas desconhecidas não processadas"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, codigo_temp, encoding, primeira_deteccao, ultima_deteccao, total_deteccoes
            FROM pessoas_desconhecidas 
            WHERE processado = 0
            ORDER BY total_deteccoes DESC, ultima_deteccao DESC
        ''')
        
        pessoas = cursor.fetchall()
        conn.close()
        return pessoas
    
    def atualizar_deteccao_desconhecida(self, pessoa_id):
        """Atualiza a última detecção de uma pessoa desconhecida"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE pessoas_desconhecidas 
            SET ultima_deteccao = CURRENT_TIMESTAMP, 
                total_deteccoes = total_deteccoes + 1
            WHERE id = ?
        ''', (pessoa_id,))
        
        conn.commit()
        conn.close()
    
    def marcar_desconhecida_processada(self, pessoa_id):
        """Marca uma pessoa desconhecida como processada"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE pessoas_desconhecidas 
            SET processado = 1
            WHERE id = ?
        ''', (pessoa_id,))
        
        conn.commit()
        conn.close()
    
    def obter_configuracao(self, chave):
        """Obtém uma configuração do sistema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT valor FROM configuracoes WHERE chave = ?', (chave,))
        resultado = cursor.fetchone()
        conn.close()
        
        return resultado[0] if resultado else None
    
    def obter_relatorio_presencas(self, data_inicio=None, data_fim=None):
        """Gera relatório de presenças"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = '''
            SELECT 
                rp.data_presenca,
                CASE 
                    WHEN rp.tipo_pessoa = 'conhecida' THEN pc.nome
                    ELSE pd.codigo_temp
                END as identificacao,
                rp.tipo_pessoa,
                rp.confianca
            FROM registros_presenca rp
            LEFT JOIN pessoas_conhecidas pc ON rp.pessoa_id = pc.id AND rp.tipo_pessoa = 'conhecida'
            LEFT JOIN pessoas_desconhecidas pd ON rp.pessoa_id = pd.id AND rp.tipo_pessoa = 'desconhecida'
        '''
        
        params = []
        if data_inicio and data_fim:
            query += ' WHERE DATE(rp.data_presenca) BETWEEN ? AND ?'
            params = [data_inicio, data_fim]
        
        query += ' ORDER BY rp.data_presenca DESC'
        
        cursor.execute(query, params)
        resultados = cursor.fetchall()
        conn.close()
        
        return resultados

