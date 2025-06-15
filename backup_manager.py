import os
import shutil
import sqlite3
import json
from datetime import datetime
import zipfile

class BackupManager:
    def __init__(self, db_path="igreja_reconhecimento.db"):
        self.db_path = db_path
        self.backup_dir = "backups"
        
        # Criar diretório de backup se não existir
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def criar_backup_completo(self):
        """Cria backup completo do sistema"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_completo_{timestamp}"
            backup_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Backup do banco de dados
                if os.path.exists(self.db_path):
                    zipf.write(self.db_path, "igreja_reconhecimento.db")
                
                # Backup dos arquivos Python
                arquivos_sistema = [
                    "database.py",
                    "reconhecimento_facial.py", 
                    "gerenciador.py",
                    "backup_manager.py",
                    "iniciar_sistema.py"
                ]
                
                for arquivo in arquivos_sistema:
                    if os.path.exists(arquivo):
                        zipf.write(arquivo, arquivo)
                
                # Criar arquivo de metadados
                metadata = {
                    "data_backup": datetime.now().isoformat(),
                    "versao_sistema": "1.0",
                    "arquivos_incluidos": arquivos_sistema
                }
                
                zipf.writestr("metadata.json", json.dumps(metadata, indent=2))
            
            print(f"Backup completo criado: {backup_path}")
            return backup_path
            
        except Exception as e:
            print(f"Erro ao criar backup: {e}")
            return None
    
    def criar_backup_dados(self):
        """Cria backup apenas dos dados (banco de dados)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_dados_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_name)
            
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                print(f"Backup dos dados criado: {backup_path}")
                return backup_path
            else:
                print("Banco de dados não encontrado!")
                return None
                
        except Exception as e:
            print(f"Erro ao criar backup dos dados: {e}")
            return None
    
    def exportar_pessoas_csv(self):
        """Exporta lista de pessoas para CSV"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(self.backup_dir, f"pessoas_{timestamp}.csv")
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT nome, idade, sexo, etnia, telefone, data_cadastro, ativo
                FROM pessoas_conhecidas
                ORDER BY nome
            ''')
            
            pessoas = cursor.fetchall()
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write("Nome,Idade,Sexo,Etnia,Telefone,Data_Cadastro,Ativo\n")
                for pessoa in pessoas:
                    linha = ','.join([str(campo) if campo is not None else '' for campo in pessoa])
                    f.write(linha + '\n')
            
            conn.close()
            print(f"Lista de pessoas exportada: {csv_path}")
            return csv_path
            
        except Exception as e:
            print(f"Erro ao exportar pessoas: {e}")
            return None
    
    def exportar_relatorio_presencas_csv(self, data_inicio=None, data_fim=None):
        """Exporta relatório de presenças para CSV"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(self.backup_dir, f"presencas_{timestamp}.csv")
            
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
            registros = cursor.fetchall()
            
            with open(csv_path, 'w', encoding='utf-8') as f:
                f.write("Data_Presenca,Identificacao,Tipo_Pessoa,Confianca\n")
                for registro in registros:
                    linha = ','.join([str(campo) if campo is not None else '' for campo in registro])
                    f.write(linha + '\n')
            
            conn.close()
            print(f"Relatório de presenças exportado: {csv_path}")
            return csv_path
            
        except Exception as e:
            print(f"Erro ao exportar relatório: {e}")
            return None
    
    def listar_backups(self):
        """Lista todos os backups disponíveis"""
        try:
            backups = []
            
            if os.path.exists(self.backup_dir):
                for arquivo in os.listdir(self.backup_dir):
                    if arquivo.startswith('backup_'):
                        caminho_completo = os.path.join(self.backup_dir, arquivo)
                        stat = os.stat(caminho_completo)
                        data_modificacao = datetime.fromtimestamp(stat.st_mtime)
                        tamanho = stat.st_size
                        
                        backups.append({
                            'nome': arquivo,
                            'caminho': caminho_completo,
                            'data': data_modificacao,
                            'tamanho': tamanho
                        })
            
            # Ordenar por data (mais recente primeiro)
            backups.sort(key=lambda x: x['data'], reverse=True)
            return backups
            
        except Exception as e:
            print(f"Erro ao listar backups: {e}")
            return []
    
    def restaurar_backup(self, backup_path):
        """Restaura um backup"""
        try:
            if not os.path.exists(backup_path):
                print("Arquivo de backup não encontrado!")
                return False
            
            # Fazer backup do banco atual antes de restaurar
            if os.path.exists(self.db_path):
                backup_atual = f"{self.db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy2(self.db_path, backup_atual)
                print(f"Backup do banco atual salvo em: {backup_atual}")
            
            if backup_path.endswith('.zip'):
                # Restaurar backup completo
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    zipf.extractall('.')
                print("Backup completo restaurado!")
            elif backup_path.endswith('.db'):
                # Restaurar apenas banco de dados
                shutil.copy2(backup_path, self.db_path)
                print("Banco de dados restaurado!")
            else:
                print("Formato de backup não reconhecido!")
                return False
            
            return True
            
        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            return False
    
    def limpar_backups_antigos(self, dias=30):
        """Remove backups mais antigos que X dias"""
        try:
            if not os.path.exists(self.backup_dir):
                return
            
            data_limite = datetime.now() - timedelta(days=dias)
            removidos = 0
            
            for arquivo in os.listdir(self.backup_dir):
                if arquivo.startswith('backup_'):
                    caminho_completo = os.path.join(self.backup_dir, arquivo)
                    stat = os.stat(caminho_completo)
                    data_modificacao = datetime.fromtimestamp(stat.st_mtime)
                    
                    if data_modificacao < data_limite:
                        os.remove(caminho_completo)
                        removidos += 1
                        print(f"Backup removido: {arquivo}")
            
            print(f"Total de backups antigos removidos: {removidos}")
            
        except Exception as e:
            print(f"Erro ao limpar backups: {e}")

def menu_backup():
    """Menu interativo para backup e restauração"""
    backup_manager = BackupManager()
    
    while True:
        print("\n" + "-"*50)
        print("    BACKUP E RESTAURAÇÃO")
        print("-"*50)
        print("1. Criar Backup Completo")
        print("2. Criar Backup dos Dados")
        print("3. Exportar Lista de Pessoas (CSV)")
        print("4. Exportar Relatório de Presenças (CSV)")
        print("5. Listar Backups")
        print("6. Restaurar Backup")
        print("7. Limpar Backups Antigos")
        print("0. Voltar")
        print("-"*50)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            backup_manager.criar_backup_completo()
        elif opcao == "2":
            backup_manager.criar_backup_dados()
        elif opcao == "3":
            backup_manager.exportar_pessoas_csv()
        elif opcao == "4":
            data_inicio = input("Data início (YYYY-MM-DD, opcional): ").strip()
            data_fim = input("Data fim (YYYY-MM-DD, opcional): ").strip()
            data_inicio = data_inicio if data_inicio else None
            data_fim = data_fim if data_fim else None
            backup_manager.exportar_relatorio_presencas_csv(data_inicio, data_fim)
        elif opcao == "5":
            backups = backup_manager.listar_backups()
            if backups:
                print(f"\n{'Nome':<30} {'Data':<20} {'Tamanho (KB)':<12}")
                print("-"*65)
                for backup in backups:
                    tamanho_kb = backup['tamanho'] // 1024
                    print(f"{backup['nome']:<30} {backup['data'].strftime('%Y-%m-%d %H:%M'):<20} {tamanho_kb:<12}")
            else:
                print("\nNenhum backup encontrado.")
        elif opcao == "6":
            backups = backup_manager.listar_backups()
            if backups:
                print("\nBackups disponíveis:")
                for i, backup in enumerate(backups):
                    print(f"{i+1}. {backup['nome']} ({backup['data'].strftime('%Y-%m-%d %H:%M')})")
                
                escolha = input("\nEscolha o número do backup (0 para cancelar): ").strip()
                if escolha.isdigit() and int(escolha) > 0:
                    idx = int(escolha) - 1
                    if idx < len(backups):
                        confirmacao = input(f"Confirma restauração de '{backups[idx]['nome']}'? (s/N): ").strip().lower()
                        if confirmacao == 's':
                            backup_manager.restaurar_backup(backups[idx]['caminho'])
            else:
                print("\nNenhum backup encontrado.")
        elif opcao == "7":
            dias = input("Remover backups mais antigos que quantos dias? (padrão: 30): ").strip()
            dias = int(dias) if dias.isdigit() else 30
            confirmacao = input(f"Confirma remoção de backups com mais de {dias} dias? (s/N): ").strip().lower()
            if confirmacao == 's':
                backup_manager.limpar_backups_antigos(dias)
        elif opcao == "0":
            break
        else:
            print("Opção inválida!")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    menu_backup()

