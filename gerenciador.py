import os
import sys
from datetime import datetime, timedelta
from database import DatabaseManager
from reconhecimento_facial import FaceRecognitionSystem
import pickle

class GerenciadorSistema:
    def __init__(self):
        self.db = DatabaseManager()
        self.sistema_reconhecimento = None
    
    def menu_principal(self):
        """Exibe o menu principal do sistema"""
        while True:
            print("\n" + "="*60)
            print("    SISTEMA DE RECONHECIMENTO FACIAL - IGREJA")
            print("="*60)
            print("1. Iniciar Reconhecimento Facial")
            print("2. Gerenciar Pessoas Conhecidas")
            print("3. Gerenciar Pessoas Desconhecidas")
            print("4. Relatórios de Presença")
            print("5. Configurações do Sistema")
            print("6. Backup e Restauração")
            print("0. Sair")
            print("-"*60)
            
            try:
                opcao = input("Escolha uma opção: ").strip()
                
                if opcao == "1":
                    self.iniciar_reconhecimento()
                elif opcao == "2":
                    self.menu_pessoas_conhecidas()
                elif opcao == "3":
                    self.menu_pessoas_desconhecidas()
                elif opcao == "4":
                    self.menu_relatorios()
                elif opcao == "5":
                    self.menu_configuracoes()
                elif opcao == "6":
                    self.menu_backup()
                elif opcao == "0":
                    print("Saindo do sistema...")
                    break
                else:
                    print("Opção inválida!")
                    
            except KeyboardInterrupt:
                print("\nSaindo do sistema...")
                break
            except Exception as e:
                print(f"Erro: {e}")
    
    def iniciar_reconhecimento(self):
        """Inicia o sistema de reconhecimento facial"""
        print("\nInicializando sistema de reconhecimento...")
        try:
            if not self.sistema_reconhecimento:
                self.sistema_reconhecimento = FaceRecognitionSystem()
            
            camera_index = input("Índice da câmera (0 para padrão): ").strip()
            camera_index = int(camera_index) if camera_index.isdigit() else 0
            
            self.sistema_reconhecimento.iniciar_reconhecimento(camera_index)
            
        except Exception as e:
            print(f"Erro ao iniciar reconhecimento: {e}")
            input("Pressione Enter para continuar...")
    
    def menu_pessoas_conhecidas(self):
        """Menu para gerenciar pessoas conhecidas"""
        while True:
            print("\n" + "-"*40)
            print("    GERENCIAR PESSOAS CONHECIDAS")
            print("-"*40)
            print("1. Listar Pessoas")
            print("2. Adicionar Nova Pessoa")
            print("3. Editar Pessoa")
            print("4. Desativar Pessoa")
            print("5. Reativar Pessoa")
            print("0. Voltar")
            print("-"*40)
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.listar_pessoas_conhecidas()
            elif opcao == "2":
                self.adicionar_pessoa_conhecida()
            elif opcao == "3":
                self.editar_pessoa_conhecida()
            elif opcao == "4":
                self.desativar_pessoa()
            elif opcao == "5":
                self.reativar_pessoa()
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
    
    def listar_pessoas_conhecidas(self):
        """Lista todas as pessoas conhecidas"""
        try:
            pessoas = self.db.obter_pessoas_conhecidas()
            
            if not pessoas:
                print("\nNenhuma pessoa cadastrada.")
                return
            
            print(f"\n{'ID':<5} {'Nome':<25} {'Idade':<6} {'Sexo':<6} {'Telefone':<15}")
            print("-"*60)
            
            for pessoa in pessoas:
                pessoa_id, nome, idade, sexo, etnia, telefone, _ = pessoa
                print(f"{pessoa_id:<5} {nome:<25} {idade or 'N/A':<6} {sexo or 'N/A':<6} {telefone or 'N/A':<15}")
            
        except Exception as e:
            print(f"Erro ao listar pessoas: {e}")
        
        input("\nPressione Enter para continuar...")
    
    def adicionar_pessoa_conhecida(self):
        """Adiciona uma nova pessoa conhecida"""
        print("\n--- ADICIONAR NOVA PESSOA ---")
        
        try:
            nome = input("Nome completo: ").strip()
            if not nome:
                print("Nome é obrigatório!")
                return
            
            idade = input("Idade (opcional): ").strip()
            idade = int(idade) if idade.isdigit() else None
            
            sexo = input("Sexo (M/F/Outro, opcional): ").strip().upper()
            sexo = sexo if sexo in ['M', 'F', 'OUTRO'] else None
            
            etnia = input("Etnia (opcional): ").strip()
            etnia = etnia if etnia else None
            
            telefone = input("Telefone (opcional): ").strip()
            telefone = telefone if telefone else None
            
            print("\nOpções de captura:")
            print("1. Capturar da webcam")
            print("2. Cancelar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                if not self.sistema_reconhecimento:
                    self.sistema_reconhecimento = FaceRecognitionSystem()
                
                sucesso = self.sistema_reconhecimento.adicionar_pessoa_do_video(
                    nome, idade, sexo, etnia, telefone
                )
                
                if sucesso:
                    print(f"\nPessoa {nome} adicionada com sucesso!")
                else:
                    print("\nFalha ao adicionar pessoa.")
            else:
                print("Operação cancelada.")
                
        except Exception as e:
            print(f"Erro ao adicionar pessoa: {e}")
        
        input("Pressione Enter para continuar...")
    
    def menu_pessoas_desconhecidas(self):
        """Menu para gerenciar pessoas desconhecidas"""
        while True:
            print("\n" + "-"*40)
            print("    GERENCIAR PESSOAS DESCONHECIDAS")
            print("-"*40)
            print("1. Listar Pessoas Desconhecidas")
            print("2. Identificar Pessoa Desconhecida")
            print("3. Marcar como Duplicata")
            print("4. Limpar Pessoas Processadas")
            print("0. Voltar")
            print("-"*40)
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.listar_pessoas_desconhecidas()
            elif opcao == "2":
                self.identificar_pessoa_desconhecida()
            elif opcao == "3":
                self.marcar_duplicata()
            elif opcao == "4":
                self.limpar_processadas()
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
    
    def listar_pessoas_desconhecidas(self):
        """Lista pessoas desconhecidas não processadas"""
        try:
            pessoas = self.db.obter_pessoas_desconhecidas()
            
            if not pessoas:
                print("\nNenhuma pessoa desconhecida pendente.")
                return
            
            print(f"\n{'ID':<5} {'Código':<12} {'Primeira':<12} {'Última':<12} {'Total':<6}")
            print("-"*50)
            
            for pessoa in pessoas:
                pessoa_id, codigo, primeira, ultima, total = pessoa[:5]
                print(f"{pessoa_id:<5} {codigo:<12} {primeira[:10]:<12} {ultima[:10]:<12} {total:<6}")
            
        except Exception as e:
            print(f"Erro ao listar pessoas desconhecidas: {e}")
        
        input("\nPressione Enter para continuar...")
    
    def identificar_pessoa_desconhecida(self):
        """Identifica uma pessoa desconhecida"""
        try:
            pessoas = self.db.obter_pessoas_desconhecidas()
            
            if not pessoas:
                print("\nNenhuma pessoa desconhecida pendente.")
                return
            
            print("\nPessoas desconhecidas:")
            for i, pessoa in enumerate(pessoas):
                pessoa_id, codigo, primeira, ultima, total = pessoa[:5]
                print(f"{i+1}. {codigo} (detectada {total} vezes)")
            
            escolha = input("\nEscolha o número da pessoa (0 para cancelar): ").strip()
            
            if not escolha.isdigit() or int(escolha) == 0:
                return
            
            idx = int(escolha) - 1
            if idx < 0 or idx >= len(pessoas):
                print("Escolha inválida!")
                return
            
            pessoa_selecionada = pessoas[idx]
            pessoa_id = pessoa_selecionada[0]
            codigo = pessoa_selecionada[1]
            
            print(f"\nIdentificando pessoa {codigo}:")
            print("1. Adicionar como nova pessoa conhecida")
            print("2. Marcar como duplicata de pessoa existente")
            print("3. Cancelar")
            
            opcao = input("Escolha: ").strip()
            
            if opcao == "1":
                # Adicionar como nova pessoa
                nome = input("Nome completo: ").strip()
                if not nome:
                    print("Nome é obrigatório!")
                    return
                
                idade = input("Idade (opcional): ").strip()
                idade = int(idade) if idade.isdigit() else None
                
                sexo = input("Sexo (M/F/Outro, opcional): ").strip().upper()
                sexo = sexo if sexo in ['M', 'F', 'OUTRO'] else None
                
                etnia = input("Etnia (opcional): ").strip()
                etnia = etnia if etnia else None
                
                telefone = input("Telefone (opcional): ").strip()
                telefone = telefone if telefone else None
                
                # Usar o encoding da pessoa desconhecida
                encoding_blob = pessoa_selecionada[2]  # encoding está na posição 2
                
                novo_id = self.db.adicionar_pessoa_conhecida(
                    nome, idade, sexo, etnia, telefone, encoding_blob
                )
                
                self.db.marcar_desconhecida_processada(pessoa_id)
                
                print(f"Pessoa {nome} adicionada com ID {novo_id}!")
                
            elif opcao == "2":
                # Marcar como duplicata
                self.db.marcar_desconhecida_processada(pessoa_id)
                print("Pessoa marcada como duplicata.")
            
        except Exception as e:
            print(f"Erro ao identificar pessoa: {e}")
        
        input("Pressione Enter para continuar...")
    
    def menu_relatorios(self):
        """Menu de relatórios"""
        while True:
            print("\n" + "-"*40)
            print("    RELATÓRIOS DE PRESENÇA")
            print("-"*40)
            print("1. Relatório de Hoje")
            print("2. Relatório da Semana")
            print("3. Relatório do Mês")
            print("4. Relatório Personalizado")
            print("5. Estatísticas Gerais")
            print("0. Voltar")
            print("-"*40)
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.relatorio_hoje()
            elif opcao == "2":
                self.relatorio_semana()
            elif opcao == "3":
                self.relatorio_mes()
            elif opcao == "4":
                self.relatorio_personalizado()
            elif opcao == "5":
                self.estatisticas_gerais()
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
    
    def relatorio_hoje(self):
        """Relatório de presenças de hoje"""
        hoje = datetime.now().strftime('%Y-%m-%d')
        self.gerar_relatorio(hoje, hoje, "HOJE")
    
    def relatorio_semana(self):
        """Relatório da semana atual"""
        hoje = datetime.now()
        inicio_semana = hoje - timedelta(days=hoje.weekday())
        inicio = inicio_semana.strftime('%Y-%m-%d')
        fim = hoje.strftime('%Y-%m-%d')
        self.gerar_relatorio(inicio, fim, "SEMANA ATUAL")
    
    def relatorio_mes(self):
        """Relatório do mês atual"""
        hoje = datetime.now()
        inicio = hoje.replace(day=1).strftime('%Y-%m-%d')
        fim = hoje.strftime('%Y-%m-%d')
        self.gerar_relatorio(inicio, fim, "MÊS ATUAL")
    
    def gerar_relatorio(self, data_inicio, data_fim, titulo):
        """Gera relatório de presenças"""
        try:
            registros = self.db.obter_relatorio_presencas(data_inicio, data_fim)
            
            print(f"\n{'='*60}")
            print(f"    RELATÓRIO DE PRESENÇAS - {titulo}")
            print(f"    Período: {data_inicio} a {data_fim}")
            print(f"{'='*60}")
            
            if not registros:
                print("Nenhum registro encontrado no período.")
                return
            
            print(f"{'Data/Hora':<20} {'Nome/Código':<25} {'Tipo':<12} {'Confiança':<10}")
            print("-"*70)
            
            conhecidas = 0
            desconhecidas = 0
            
            for registro in registros:
                data_presenca, identificacao, tipo_pessoa, confianca = registro
                data_formatada = data_presenca[:16]  # YYYY-MM-DD HH:MM
                confianca_str = f"{confianca:.2f}" if confianca else "N/A"
                
                print(f"{data_formatada:<20} {identificacao:<25} {tipo_pessoa:<12} {confianca_str:<10}")
                
                if tipo_pessoa == 'conhecida':
                    conhecidas += 1
                else:
                    desconhecidas += 1
            
            print("-"*70)
            print(f"Total: {len(registros)} registros")
            print(f"Pessoas conhecidas: {conhecidas}")
            print(f"Pessoas desconhecidas: {desconhecidas}")
            
        except Exception as e:
            print(f"Erro ao gerar relatório: {e}")
        
        input("\nPressione Enter para continuar...")
    
    def menu_configuracoes(self):
        """Menu de configurações"""
        while True:
            print("\n" + "-"*40)
            print("    CONFIGURAÇÕES DO SISTEMA")
            print("-"*40)
            print("1. Ajustar Tolerância de Reconhecimento")
            print("2. Ajustar Intervalo de Detecção")
            print("3. Ver Configurações Atuais")
            print("0. Voltar")
            print("-"*40)
            
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == "1":
                self.ajustar_tolerancia()
            elif opcao == "2":
                self.ajustar_intervalo()
            elif opcao == "3":
                self.ver_configuracoes()
            elif opcao == "0":
                break
            else:
                print("Opção inválida!")
    
    def ver_configuracoes(self):
        """Mostra configurações atuais"""
        try:
            tolerancia = self.db.obter_configuracao('tolerancia_reconhecimento')
            intervalo = self.db.obter_configuracao('intervalo_deteccao')
            
            print(f"\nConfigurações atuais:")
            print(f"Tolerância de reconhecimento: {tolerancia}")
            print(f"Intervalo de detecção: {intervalo} segundos")
            
        except Exception as e:
            print(f"Erro ao obter configurações: {e}")
        
        input("\nPressione Enter para continuar...")

def main():
    """Função principal"""
    try:
        gerenciador = GerenciadorSistema()
        gerenciador.menu_principal()
    except Exception as e:
        print(f"Erro fatal: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()


    def menu_backup(self):
        """Menu de backup e restauração"""
        try:
            from backup_manager import menu_backup
            menu_backup()
        except ImportError:
            print("Módulo de backup não encontrado!")
            input("Pressione Enter para continuar...")

