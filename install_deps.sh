#!/bin/bash

# Script d'installation des dépendances pour LearnwithAI
echo "🚀 Installation des dépendances pour LearnwithAI..."

# Installer les dépendances Python
echo "📦 Installation des packages Python..."
pip install llama-index openai python-dotenv

# Créer le fichier .env s'il n'existe pas
if [ ! -f ".env" ]; then
    echo "📝 Création du fichier .env..."
    cp .env.example .env
    echo "✅ Fichier .env créé. N'oubliez pas d'ajouter votre clé API OpenAI !"
else
    echo "ℹ️ Le fichier .env existe déjà"
fi

echo "✅ Installation terminée !"
echo ""
echo "📋 Prochaines étapes :"
echo "1. Ouvrez le fichier .env et ajoutez votre clé API OpenAI"
echo "2. Testez l'application avec: python -m briefcase dev"
echo ""
echo "🔑 Pour obtenir une clé API OpenAI :"
echo "   1. Allez sur https://platform.openai.com/api-keys"
echo "   2. Créez un nouveau compte ou connectez-vous"
echo "   3. Créez une nouvelle clé API"
echo "   4. Copiez la clé dans le fichier .env"