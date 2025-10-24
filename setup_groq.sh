#!/bin/bash

# Script de configuration Groq AI pour LearnwithAI
echo "🚀 Configuration de Groq AI pour LearnwithAI..."

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

# Vérifier si Groq est installé
check_groq() {
    python3 -c "import groq" 2>/dev/null
    return $?
}

echo "========================================"
echo "🤖 Configuration Groq AI pour LearnwithAI"
echo "========================================"

# Vérification de l'installation Groq
print_info "Vérification de Groq..."
if check_groq; then
    print_status "Groq est déjà installé"
else
    print_warning "Installation de Groq..."
    pip install groq
    if check_groq; then
        print_status "Groq installé avec succès"
    else
        print_error "Échec de l'installation de Groq"
        exit 1
    fi
fi

# Configuration du fichier .env
echo ""
print_info "Configuration du fichier .env..."

if [ ! -f ".env" ]; then
    cp .env.example .env
    print_status "Fichier .env créé"
else
    print_warning "Fichier .env existant trouvé"
fi

# Vérifier si une clé API est déjà configurée
if grep -q "your_groq_api_key_here" .env; then
    echo ""
    print_warning "🔑 Configuration de la clé API Groq requise"
    echo ""
    echo "Pour obtenir votre clé API gratuite Groq:"
    echo "1. Allez sur: ${BLUE}https://console.groq.com/${NC}"
    echo "2. Créez un compte ou connectez-vous"
    echo "3. Générez une nouvelle clé API"
    echo "4. Copiez la clé et collez-la ci-dessous"
    echo ""
    
    read -p "Entrez votre clé API Groq (ou appuyez sur Entrée pour configurer plus tard): " api_key
    
    if [ ! -z "$api_key" ]; then
        # Remplacer la clé dans le fichier .env
        sed -i "s/GROQ_API_KEY=your_groq_api_key_here/GROQ_API_KEY=$api_key/" .env
        print_status "Clé API configurée"
    else
        print_warning "Clé API non configurée. Vous devrez la configurer manuellement dans .env"
    fi
else
    print_status "Clé API déjà configurée"
fi

# Sélection du modèle
echo ""
print_info "🤖 Sélection du modèle Groq..."
echo ""
echo "Modèles disponibles:"
echo "1. llama-3.1-8b-instant     (Recommandé - Rapide et équilibré)"
echo "2. llama-3.1-70b-versatile  (Plus performant mais plus lent)"
echo "3. llama3-8b-8192           (Rapide, bonne qualité)"
echo "4. llama3-70b-8192          (Haute qualité)"
echo "5. mixtral-8x7b-32768       (Excellent raisonnement)"
echo "6. gemma-7b-it              (Modèle Google)"

read -p "Choisissez un modèle (1-6) [défaut: 1]: " model_choice

case $model_choice in
    2) selected_model="llama-3.1-70b-versatile" ;;
    3) selected_model="llama3-8b-8192" ;;
    4) selected_model="llama3-70b-8192" ;;
    5) selected_model="mixtral-8x7b-32768" ;;
    6) selected_model="gemma-7b-it" ;;
    *) selected_model="llama-3.1-8b-instant" ;;
esac

# Mettre à jour le modèle dans .env
sed -i "s/GROQ_MODEL=.*/GROQ_MODEL=$selected_model/" .env
print_status "Modèle configuré: $selected_model"

# Test de la configuration
echo ""
print_info "🧪 Test de la configuration..."

# Vérifier si la clé API est configurée
if grep -q "your_groq_api_key_here" .env; then
    print_warning "Test ignoré - clé API non configurée"
    echo ""
    print_info "📋 Configuration terminée!"
    echo ""
    echo "Prochaines étapes:"
    echo "1. Éditez le fichier .env et ajoutez votre clé API Groq"
    echo "2. Testez avec: python test_ai_service.py"
    echo "3. Lancez l'application: python -m briefcase dev"
else
    print_info "Test de connexion Groq..."
    python3 test_ai_service.py > /tmp/groq_test.log 2>&1
    
    if [ $? -eq 0 ]; then
        print_status "Test réussi! Groq AI fonctionne parfaitement"
        echo ""
        print_status "🎉 Configuration terminée avec succès!"
        echo ""
        echo "Votre assistant IA est prêt:"
        echo "• Modèle: $selected_model"
        echo "• API: Groq (ultra-rapide)"
        echo "• Coût: Gratuit jusqu'à 100 requêtes/jour"
        echo ""
        echo "🚀 Lancez votre application:"
        echo "   python -m briefcase dev"
    else
        print_error "Test échoué. Vérifiez votre clé API"
        echo "Logs d'erreur:"
        cat /tmp/groq_test.log
    fi
fi

echo ""
print_info "💡 Informations utiles:"
echo "• Console Groq: https://console.groq.com/"
echo "• Documentation: https://console.groq.com/docs"
echo "• Modèles disponibles: https://console.groq.com/docs/models"
echo "• Limites gratuites: 100 requêtes/jour par modèle"

# Nettoyage
rm -f /tmp/groq_test.log

echo ""
print_status "Configuration Groq terminée!"