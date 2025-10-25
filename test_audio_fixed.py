#!/usr/bin/env python3
"""
Test script pour vérifier que le service audio fonctionne correctement
après la correction de la duplication
"""

import sys
import os
import time

# Ajouter le chemin src pour importer le module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_audio_service():
    """Test du service audio corrigé"""
    print("🎤 Test du service audio corrigé")
    print("=" * 50)
    
    try:
        # Importer le service audio depuis le bon endroit
        from learnwithai.services.audio_service import AudioService
        
        print("✅ Import du service audio réussi")
        
        # Initialiser le service
        audio_service = AudioService()
        print("✅ Initialisation du service réussie")
        
        # Vérifier les dispositifs disponibles
        devices = audio_service.get_available_devices()
        print(f"📱 Dispositifs audio disponibles: {len(devices)}")
        
        for device in devices:
            print(f"  - {device['name']} ({device['channels']} canaux, {device['sample_rate']} Hz)")
        
        # Vérifier le status
        status = audio_service.get_recording_status()
        print(f"📊 Status initial: {status}")
        
        # Test d'enregistrement court
        print("\n🔴 Test d'enregistrement (3 secondes)...")
        print("Parlez maintenant!")
        
        if audio_service.start_recording():
            print("✅ Enregistrement démarré")
            time.sleep(3)
            
            file_path = audio_service.stop_recording()
            if file_path:
                print(f"✅ Enregistrement sauvé: {file_path}")
                
                # Test de lecture
                print("▶️ Test de lecture...")
                if audio_service.play_audio(file_path):
                    print("✅ Lecture réussie")
                else:
                    print("❌ Erreur de lecture")
            else:
                print("❌ Erreur de sauvegarde")
        else:
            print("❌ Impossible de démarrer l'enregistrement")
        
        # Lister les enregistrements
        recordings = audio_service.list_recordings()
        print(f"\n📁 Enregistrements disponibles: {len(recordings)}")
        
        # Nettoyage
        audio_service.cleanup()
        print("\n🧹 Nettoyage terminé")
        
        print("\n🎉 Test terminé avec succès!")
        
    except ImportError as e:
        print(f"❌ Erreur d'import: {e}")
        print("Vérifiez que le service audio est dans le bon dossier")
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_audio_service()