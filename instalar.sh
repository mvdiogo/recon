#!/bin/bash

# Script de Instalação - Sistema de Reconhecimento Facial para Igreja
# Para Ubuntu/Debian Linux

echo "=========================================="
echo "Sistema de Reconhecimento Facial - Igreja"
echo "Script de Instalação Automática"
echo "=========================================="

# Verificar se está rodando como root
if [ "$EUID" -eq 0 ]; then
    echo "AVISO: Não execute este script como root (sudo)"
    echo "Execute como usuário normal: ./instalar.sh"
    exit 1
fi

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não encontrado. Instalando..."
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# Verificar versão do Python
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.7"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "ERRO: Python 3.7+ é necessário. Versão atual: $PYTHON_VERSION"
    exit 1
fi

echo "Python $PYTHON_VERSION encontrado ✓"

# Instalar dependências do sistema
echo "Instalando dependências do sistema..."
sudo apt update
sudo apt install -y \
    python3-pip \
    python3-dev \
    cmake \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    pkg-config \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    libxvidcore-dev \
    libx264-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    gfortran \
    openexr \
    libatlas-base-dev \
    python3-numpy

if [ $? -ne 0 ]; then
    echo "ERRO: Falha na instalação das dependências do sistema"
    exit 1
fi

echo "Dependências do sistema instaladas ✓"

# Atualizar pip
echo "Atualizando pip..."
python3 -m pip install --upgrade pip

# Instalar dependências Python
echo "Instalando dependências Python..."
if [ -f "requirements.txt" ]; then
    python3 -m pip install -r requirements.txt
else
    echo "Arquivo requirements.txt não encontrado. Instalando dependências manualmente..."
    python3 -m pip install opencv-python mediapipe numpy scikit-learn pillow
fi

if [ $? -ne 0 ]; then
    echo "ERRO: Falha na instalação das dependências Python"
    echo "Tentando instalação alternativa..."
    python3 -m pip install --user opencv-python mediapipe numpy scikit-learn pillow
fi

# Verificar instalação
echo "Verificando instalação..."
python3 -c "
import cv2
import mediapipe
import numpy
import sklearn
print('Todas as dependências instaladas com sucesso!')
print(f'OpenCV: {cv2.__version__}')
print(f'MediaPipe: {mediapipe.__version__}')
print(f'NumPy: {numpy.__version__}')
print(f'Scikit-learn: {sklearn.__version__}')
"

if [ $? -ne 0 ]; then
    echo "ERRO: Verificação falhou. Algumas dependências podem não estar funcionando."
    exit 1
fi

# Tornar scripts executáveis
chmod +x iniciar_sistema.py

# Criar atalho na área de trabalho (opcional)
if [ -d "$HOME/Desktop" ]; then
    echo "Criando atalho na área de trabalho..."
    cat > "$HOME/Desktop/Sistema_Igreja.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Sistema Reconhecimento Facial - Igreja
Comment=Sistema de controle de presença por reconhecimento facial
Exec=python3 $(pwd)/iniciar_sistema.py
Icon=applications-multimedia
Path=$(pwd)
Terminal=true
Categories=Application;
EOF
    chmod +x "$HOME/Desktop/Sistema_Igreja.desktop"
fi

echo "=========================================="
echo "INSTALAÇÃO CONCLUÍDA COM SUCESSO!"
echo "=========================================="
echo ""
echo "Para iniciar o sistema, execute:"
echo "  python3 iniciar_sistema.py"
echo ""
echo "Ou use o atalho criado na área de trabalho."
echo ""
echo "IMPORTANTE:"
echo "- Certifique-se de ter uma webcam conectada"
echo "- Use boa iluminação para melhor reconhecimento"
echo "- Leia o arquivo README.md para instruções completas"
echo ""
echo "Primeira execução:"
echo "1. Execute o sistema"
echo "2. Cadastre algumas pessoas conhecidas"
echo "3. Inicie o reconhecimento facial"
echo ""
echo "Boa sorte!"

