#!/usr/bin/env python3
"""
Demonstração do Sistema de Reconhecimento Facial
Este arquivo mostra como usar o sistema programaticamente
"""

import sys
import os
from datetime import datetime, timedelta

# Adicionar o diretório atual ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from reconhecimento_facial import FaceRecognitionSystem

def demonstracao_basica():
    """Demonstração básica das funcionalidades"""
    print("=== DEMONSTRAÇÃO DO SISTEMA ===")
    
    # Inicializar banco de dados
    print("\n1. Inicializando banco de dados...")
    db = DatabaseManager()
    print("✓ Banco de dados inicializado")
    
    # Verificar pessoas cadastradas
    print("\n2. Verificando pessoas cadastradas...")
    pessoas = db.obter_pessoas_conhecidas()
    print(f"✓ {len(pessoas)} pessoas encontradas no banco")
    
    # Verificar pessoas desconhecidas
    print("\n3. Verificando pessoas desconhecidas...")
    desconhecidas = db.obter_pessoas_desconhecidas()
    print(f"✓ {len(desconhecidas)} pessoas desconhecidas pendentes")
    
    # Verificar registros de presença
    print("\n4. Verificando registros de presença...")
    hoje = datetime.now().strftime('%Y-%m-%d')
    registros = db.obter_relatorio_presencas(hoje, hoje)
    print(f"✓ {len(registros)} registros de presença hoje")
    
    # Mostrar configurações
    print("\n5. Configurações atuais:")
    tolerancia = db.obter_configuracao('tolerancia_reconhecimento')
    intervalo = db.obter_configuracao('intervalo_deteccao')
    print(f"✓ Tolerância: {tolerancia}")
    print(f"✓ Intervalo: {intervalo} segundos")
    
    return True

def demonstracao_reconhecimento():
    """Demonstração do sistema de reconhecimento"""
    print("\n=== DEMONSTRAÇÃO DE RECONHECIMENTO ===")
    
    try:
        # Inicializar sistema de reconhecimento
        print("\n1. Inicializando sistema de reconhecimento...")
        sistema = FaceRecognitionSystem()
        print("✓ Sistema inicializado com sucesso")
        
        print(f"✓ {len(sistema.pessoas_conhecidas)} pessoas carregadas")
        print(f"✓ Tolerância configurada: {sistema.tolerancia}")
        
        # Verificar se há webcam disponível
        print("\n2. Verificando webcam...")
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ Webcam disponível")
            cap.release()
        else:
            print("⚠ Webcam não disponível (normal em ambiente servidor)")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False

def demonstracao_relatorios():
    """Demonstração de relatórios"""
    print("\n=== DEMONSTRAÇÃO DE RELATÓRIOS ===")
    
    db = DatabaseManager()
    
    # Relatório da semana
    print("\n1. Relatório da semana atual...")
    hoje = datetime.now()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio = inicio_semana.strftime('%Y-%m-%d')
    fim = hoje.strftime('%Y-%m-%d')
    
    registros = db.obter_relatorio_presencas(inicio, fim)
    print(f"✓ {len(registros)} registros na semana")
    
    if registros:
        print("\nÚltimos 5 registros:")
        for i, registro in enumerate(registros[:5]):
            data, nome, tipo, confianca = registro
            print(f"  {i+1}. {data[:16]} - {nome} ({tipo})")
    
    # Estatísticas gerais
    print("\n2. Estatísticas gerais...")
    pessoas_conhecidas = len(db.obter_pessoas_conhecidas())
    pessoas_desconhecidas = len(db.obter_pessoas_desconhecidas())
    total_registros = len(db.obter_relatorio_presencas())
    
    print(f"✓ Pessoas conhecidas: {pessoas_conhecidas}")
    print(f"✓ Pessoas desconhecidas: {pessoas_desconhecidas}")
    print(f"✓ Total de registros: {total_registros}")
    
    return True

def demonstracao_backup():
    """Demonstração do sistema de backup"""
    print("\n=== DEMONSTRAÇÃO DE BACKUP ===")
    
    try:
        from backup_manager import BackupManager
        
        backup_manager = BackupManager()
        
        # Listar backups existentes
        print("\n1. Verificando backups existentes...")
        backups = backup_manager.listar_backups()
        print(f"✓ {len(backups)} backups encontrados")
        
        if backups:
            print("\nBackups disponíveis:")
            for backup in backups[:3]:  # Mostrar apenas os 3 mais recentes
                print(f"  - {backup['nome']} ({backup['data'].strftime('%Y-%m-%d %H:%M')})")
        
        # Criar backup de teste (apenas dados)
        print("\n2. Criando backup de demonstração...")
        backup_path = backup_manager.criar_backup_dados()
        if backup_path:
            print(f"✓ Backup criado: {backup_path}")
        else:
            print("⚠ Não foi possível criar backup")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro no backup: {e}")
        return False

def menu_demonstracao():
    """Menu interativo de demonstração"""
    while True:
        print("\n" + "="*50)
        print("    DEMONSTRAÇÃO DO SISTEMA")
        print("="*50)
        print("1. Demonstração Básica")
        print("2. Demonstração de Reconhecimento")
        print("3. Demonstração de Relatórios")
        print("4. Demonstração de Backup")
        print("5. Executar Todas as Demonstrações")
        print("0. Sair")
        print("-"*50)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            demonstracao_basica()
        elif opcao == "2":
            demonstracao_reconhecimento()
        elif opcao == "3":
            demonstracao_relatorios()
        elif opcao == "4":
            demonstracao_backup()
        elif opcao == "5":
            print("Executando todas as demonstrações...")
            demonstracao_basica()
            demonstracao_reconhecimento()
            demonstracao_relatorios()
            demonstracao_backup()
            print("\n✓ Todas as demonstrações concluídas!")
        elif opcao == "0":
            print("Saindo da demonstração...")
            break
        else:
            print("Opção inválida!")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    try:
        menu_demonstracao()
    except KeyboardInterrupt:
        print("\n\nDemonstração interrompida pelo usuário.")
    except Exception as e:
        print(f"\nErro na demonstração: {e}")
        input("Pressione Enter para sair...")

