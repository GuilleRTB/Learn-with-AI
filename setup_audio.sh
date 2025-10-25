#!/bin/bash

# Script d'installation des dépendances audio pour LearnwithAI
echo "🎤 Installation des dépendances audio pour LearnwithAI..."

# Couleurs pour l'affichage
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

echo "========================================"
echo "🎤 Configuration Audio pour LearnwithAI"
echo "========================================"

# Détecter l'OS
OS="$(uname -s)"
case "${OS}" in
    Linux*)     MACHINE=Linux;;
    Darwin*)    MACHINE=Mac;;
    CYGWIN*)    MACHINE=Windows;;
    MINGW*)     MACHINE=Windows;;
    *)          MACHINE="UNKNOWN:${OS}"
esac

print_info "Système détecté: $MACHINE"

# Installation selon l'OS
case $MACHINE in
    Linux)
        print_info "Installation des dépendances système Linux..."
        
        # Détecter la distribution
        if [ -f /etc/debian_version ]; then
            print_info "Distribution Debian/Ubuntu détectée"
            sudo apt-get update
            sudo apt-get install -y portaudio19-dev python3-pyaudio
        elif [ -f /etc/redhat-release ]; then
            print_info "Distribution RedHat/CentOS/Fedora détectée"
            sudo yum install -y portaudio-devel
        elif [ -f /etc/arch-release ]; then
            print_info "Distribution Arch Linux détectée"
            sudo pacman -S portaudio
        else
            print_warning "Distribution Linux non reconnue"
            print_info "Veuillez installer manuellement portaudio-dev"
        fi
        ;;
    Mac)
        print_info "Installation des dépendances macOS..."
        if command -v brew &> /dev/null; then
            brew install portaudio
            print_status "PortAudio installé via Homebrew"
        else
            print_warning "Homebrew non trouvé. Installez PortAudio manuellement"
            print_info "https://formulae.brew.sh/formula/portaudio"
        fi
        ;;
    Windows)
        print_info "Windows détecté - PyAudio s'installera automatiquement"
        ;;
    *)
        print_error "Système non supporté: $MACHINE"
        exit 1
        ;;
esac

# Installation des packages Python
print_info "Installation des packages Python audio..."

# Vérifier si pip est disponible
if ! command -v pip &> /dev/null; then
    print_error "pip non trouvé. Installez Python et pip d'abord."
    exit 1
fi

# Installer PyAudio
print_info "Installation de PyAudio..."
pip install pyaudio

if [ $? -eq 0 ]; then
    print_status "PyAudio installé avec succès"
else
    print_error "Échec de l'installation de PyAudio"
    print_info "Solutions possibles:"
    echo "  1. Installez les dépendances système manquantes"
    echo "  2. Sur Windows: pip install pipwin && pipwin install pyaudio"
    echo "  3. Utilisez conda: conda install pyaudio"
    exit 1
fi

# Installer les autres dépendances audio
print_info "Installation des dépendances supplémentaires..."
pip install wave

# Test de l'installation
print_info "Test de l'installation..."
python3 -c "
import pyaudio
import wave
print('✅ PyAudio et Wave importés avec succès')
p = pyaudio.PyAudio()
print(f'📱 Dispositifs audio disponibles: {p.get_device_count()}')
p.terminate()
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_status "🎉 Installation audio terminée avec succès!"
    echo ""
    print_info "Testez les fonctionnalités audio:"
    echo "  python3 test_audio_service.py"
    echo ""
    print_info "Lancez l'application:"
    echo "  python -m briefcase dev"
else
    print_error "Test échoué. Vérifiez l'installation."
fi

echo ""
print_info "💡 Informations utiles:"
echo "• Documentation PyAudio: https://pypi.org/project/PyAudio/"
echo "• Problèmes courants: https://github.com/spatialaudio/python-sounddevice/blob/master/INSTALL.rst"
echo "• Alternative: python-sounddevice (plus simple à installer)"

print_status "Configuration audio terminée!"