#!/usr/bin/env python3
"""
Sistema de Reconhecimento Facial para Igreja
Inicializador Principal
"""

import os
import sys
import subprocess

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    dependencias = [
        'cv2', 'mediapipe', 'numpy', 'sklearn', 'sqlite3'
    ]
    
    faltando = []
    
    for dep in dependencias:
        try:
            if dep == 'cv2':
                import cv2
            elif dep == 'mediapipe':
                import mediapipe
            elif dep == 'numpy':
                import numpy
            elif dep == 'sklearn':
                import sklearn
            elif dep == 'sqlite3':
                import sqlite3
        except ImportError:
            faltando.append(dep)
    
    return faltando

def instalar_dependencias():
    """Instala dependências faltantes"""
    print("Instalando dependências...")
    
    comandos = [
        "pip3 install opencv-python",
        "pip3 install mediapipe",
        "pip3 install numpy",
        "pip3 install scikit-learn"
    ]
    
    for comando in comandos:
        print(f"Executando: {comando}")
        try:
            subprocess.run(comando.split(), check=True)
        except subprocess.CalledProcessError as e:
            print(f"Erro ao instalar: {e}")
            return False
    
    return True

def menu_inicial():
    """Menu inicial do sistema"""
    print("\n" + "="*70)
    print("    SISTEMA DE RECONHECIMENTO FACIAL PARA IGREJA")
    print("    Versão 1.0")
    print("="*70)
    print()
    print("Este sistema permite:")
    print("• Reconhecimento facial em tempo real via webcam")
    print("• Registro automático de presenças")
    print("• Gerenciamento de pessoas conhecidas e desconhecidas")
    print("• Relatórios de presença detalhados")
    print("• Backup e restauração de dados")
    print()
    print("Requisitos:")
    print("• Webcam conectada")
    print("• Python 3.7+ com dependências instaladas")
    print("• Boa iluminação para melhor reconhecimento")
    print()
    
    while True:
        print("-"*70)
        print("OPÇÕES DE INICIALIZAÇÃO:")
        print("1. Iniciar Sistema Completo (Recomendado)")
        print("2. Apenas Reconhecimento Facial")
        print("3. Apenas Gerenciamento")
        print("4. Verificar Dependências")
        print("5. Instalar Dependências")
        print("6. Ajuda e Instruções")
        print("0. Sair")
        print("-"*70)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            iniciar_sistema_completo()
        elif opcao == "2":
            iniciar_reconhecimento()
        elif opcao == "3":
            iniciar_gerenciamento()
        elif opcao == "4":
            verificar_sistema()
        elif opcao == "5":
            if instalar_dependencias():
                print("Dependências instaladas com sucesso!")
            else:
                print("Erro na instalação das dependências.")
        elif opcao == "6":
            mostrar_ajuda()
        elif opcao == "0":
            print("Saindo...")
            break
        else:
            print("Opção inválida!")
        
        input("\nPressione Enter para continuar...")

def iniciar_sistema_completo():
    """Inicia o sistema completo"""
    try:
        from gerenciador import main
        main()
    except ImportError as e:
        print(f"Erro ao importar módulos: {e}")
        print("Verifique se todos os arquivos estão no diretório correto.")
    except Exception as e:
        print(f"Erro ao iniciar sistema: {e}")

def iniciar_reconhecimento():
    """Inicia apenas o reconhecimento facial"""
    try:
        from reconhecimento_facial import FaceRecognitionSystem
        sistema = FaceRecognitionSystem()
        sistema.iniciar_reconhecimento()
    except ImportError as e:
        print(f"Erro ao importar módulos: {e}")
    except Exception as e:
        print(f"Erro ao iniciar reconhecimento: {e}")

def iniciar_gerenciamento():
    """Inicia apenas o gerenciamento"""
    try:
        from gerenciador import GerenciadorSistema
        gerenciador = GerenciadorSistema()
        gerenciador.menu_principal()
    except ImportError as e:
        print(f"Erro ao importar módulos: {e}")
    except Exception as e:
        print(f"Erro ao iniciar gerenciamento: {e}")

def verificar_sistema():
    """Verifica o sistema e dependências"""
    print("\nVerificando sistema...")
    
    # Verificar arquivos
    arquivos_necessarios = [
        'database.py',
        'reconhecimento_facial.py',
        'gerenciador.py',
        'backup_manager.py'
    ]
    
    print("\nArquivos do sistema:")
    for arquivo in arquivos_necessarios:
        if os.path.exists(arquivo):
            print(f"✓ {arquivo}")
        else:
            print(f"✗ {arquivo} - FALTANDO!")
    
    # Verificar dependências
    print("\nDependências Python:")
    faltando = verificar_dependencias()
    
    if not faltando:
        print("✓ Todas as dependências estão instaladas!")
    else:
        print("✗ Dependências faltando:")
        for dep in faltando:
            print(f"  - {dep}")
        print("\nUse a opção 5 para instalar as dependências.")
    
    # Verificar banco de dados
    print("\nBanco de dados:")
    if os.path.exists('igreja_reconhecimento.db'):
        print("✓ Banco de dados encontrado")
        try:
            import sqlite3
            conn = sqlite3.connect('igreja_reconhecimento.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM pessoas_conhecidas")
            total_pessoas = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM registros_presenca")
            total_registros = cursor.fetchone()[0]
            conn.close()
            
            print(f"  - Pessoas cadastradas: {total_pessoas}")
            print(f"  - Registros de presença: {total_registros}")
        except Exception as e:
            print(f"  - Erro ao acessar banco: {e}")
    else:
        print("! Banco de dados será criado na primeira execução")
    
    # Verificar câmera
    print("\nTeste de câmera:")
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ Câmera padrão acessível")
            cap.release()
        else:
            print("✗ Não foi possível acessar a câmera padrão")
    except Exception as e:
        print(f"✗ Erro ao testar câmera: {e}")

def mostrar_ajuda():
    """Mostra ajuda e instruções"""
    print("\n" + "="*70)
    print("    AJUDA E INSTRUÇÕES")
    print("="*70)
    
    print("""
PRIMEIROS PASSOS:
1. Execute a opção 4 para verificar se tudo está funcionando
2. Se houver dependências faltando, use a opção 5 para instalar
3. Inicie o sistema completo com a opção 1

COMO USAR O RECONHECIMENTO FACIAL:
1. Certifique-se de que a webcam está conectada e funcionando
2. Cadastre pessoas conhecidas antes de iniciar o reconhecimento
3. Posicione a câmera em local com boa iluminação
4. O sistema detectará rostos automaticamente
5. Pessoas conhecidas terão presença registrada
6. Pessoas desconhecidas serão salvas para identificação posterior

CADASTRO DE PESSOAS:
1. Use o menu "Gerenciar Pessoas Conhecidas"
2. Escolha "Adicionar Nova Pessoa"
3. Preencha os dados solicitados
4. Posicione o rosto na webcam quando solicitado
5. O sistema capturará múltiplas amostras do rosto

GERENCIAMENTO DE PESSOAS DESCONHECIDAS:
1. Acesse "Gerenciar Pessoas Desconhecidas"
2. Veja a lista de pessoas detectadas mas não identificadas
3. Identifique pessoas conhecidas ou marque como duplicatas
4. Isso melhora a precisão do sistema

RELATÓRIOS:
- Visualize presenças por período (hoje, semana, mês)
- Exporte dados para CSV
- Acompanhe estatísticas de uso

BACKUP E SEGURANÇA:
- Faça backups regulares dos dados
- Exporte listas de pessoas e relatórios
- Mantenha cópias de segurança em local seguro

DICAS PARA MELHOR RECONHECIMENTO:
- Use iluminação uniforme e adequada
- Evite sombras no rosto
- Mantenha a câmera estável
- Cadastre pessoas com diferentes expressões
- Ajuste a tolerância se necessário

SOLUÇÃO DE PROBLEMAS:
- Se o reconhecimento estiver impreciso, ajuste a tolerância
- Se houver muitas detecções, aumente o intervalo de detecção
- Verifique se a câmera está funcionando corretamente
- Certifique-se de que há boa iluminação
""")

def main():
    """Função principal"""
    try:
        menu_inicial()
    except KeyboardInterrupt:
        print("\n\nSistema interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro fatal: {e}")
        input("Pressione Enter para sair...")

if __name__ == "__main__":
    main()

