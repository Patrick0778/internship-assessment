"""
translate.py - A simple script to translate between English and common Ugandan languages.
"""

def main():
    # Available languages
    languages = ["English", "Luganda", "Runyankole", "Ateso", "Lugbara", "Acholi"]
    
    # Translation dictionary - simplified with common phrases
    # Format: {source_language: {target_language: {phrase: translation}}}
    translations = {
        "English": {
            "Luganda": {
                "Hello": "Oli otya",
                "How are you?": "Oli otya?",
                "Good morning": "Wasuze otya",
                "Thank you": "Weebale",
                "Goodbye": "Weraba",
                "What is your name?": "Amanya go gwe ani?",
                "My name is": "Amanya gange",
                "I love you": "Nkwagala",
                "I am fine": "Ndi bulungi",
                "Welcome": "Tukusanyukidde"
            },
            "Runyankole": {
                "Hello": "Agandi",
                "How are you?": "Oli ota?",
                "Good morning": "Oraire ota",
                "Thank you": "Webale",
                "Goodbye": "Urabeho",
                "What is your name?": "Nibaiita oha?",
                "My name is": "Nibanyeta",
                "I love you": "Ninkukunda",
                "I am fine": "Ndi kurungi",
                "Welcome": "Tukushemereirwe"
            },
            "Ateso": {
                "Hello": "Yoga",
                "How are you?": "Ijok bo?",
                "Good morning": "Ejok akwar",
                "Thank you": "Eyalama",
                "Goodbye": "Awaio",
                "What is your name?": "Arai ekon bo?",
                "My name is": "Ekon ka",
                "I love you": "Amina jo",
                "I am fine": "Ajok",
                "Welcome": "Aiyalamikin"
            },
            "Lugbara": {
                "Hello": "Kzi",
                "How are you?": "Mi nga ya?",
                "Good morning": "Muke cua",
                "Thank you": "Awa'difo",
                "Goodbye": "Rua pee",
                "What is your name?": "Mi ru ngoni?",
                "My name is": "Ma ru",
                "I love you": "Ma mi nze",
                "I am fine": "Ma ovu woro",
                "Welcome": "Mu amvu"
            },
            "Acholi": {
                "Hello": "Kopango",
                "How are you?": "Itye nining?",
                "Good morning": "Iribedo maber",
                "Thank you": "Apwoyo",
                "Goodbye": "Orfoyo",
                "What is your name?": "Nyingi anga?",
                "My name is": "Nyinga en",
                "I love you": "Amari",
                "I am fine": "Atye maber",
                "Welcome": "Ibekwano"
            }
        }
    }
    
    # Populate reverse translations for each language pair
    for src_lang in list(translations.keys()):
        for tgt_lang in list(translations[src_lang].keys()):
            if tgt_lang not in translations:
                translations[tgt_lang] = {}
            
            if src_lang not in translations[tgt_lang]:
                translations[tgt_lang][src_lang] = {}
                
            # Add the reverse translations
            for phrase, translation in translations[src_lang][tgt_lang].items():
                translations[tgt_lang][src_lang][translation] = phrase
    
    # User interaction
    print("Welcome to the Ugandan Language Translator!")
    
    while True:
        print("\nPlease choose the source language: (one of English, Luganda, Runyankole, Ateso, Lugbara or Acholi)")
        source_language = input().strip().title()
        
        if source_language not in languages:
            print(f"Invalid language. Please choose one of: {', '.join(languages)}")
            continue
        
        print("\nPlease choose the target language: (one of English, Luganda, Runyankole, Ateso, Lugbara or Acholi):")
        target_language = input().strip().title()
        
        if target_language not in languages:
            print(f"Invalid language. Please choose one of: {', '.join(languages)}")
            continue
            
        if source_language == target_language:
            print("Source and target languages cannot be the same.")
            continue
            
        print("\nEnter the text to translate:")
        text_to_translate = input().strip()
        
        # Check if direct translation is available
        if (source_language in translations and 
            target_language in translations[source_language] and 
            text_to_translate in translations[source_language][target_language]):
            print(f"\n{translations[source_language][target_language][text_to_translate]}")
        else:
            # Check if we can find a case-insensitive match
            found = False
            if source_language in translations and target_language in translations[source_language]:
                for phrase in translations[source_language][target_language]:
                    if phrase.lower() == text_to_translate.lower():
                        print(f"\n{translations[source_language][target_language][phrase]}")
                        found = True
                        break
            
            if not found:
                print("\nSorry, translation not available for this text.")
        
        print("\nWould you like to translate something else? (yes/no)")
        if input().lower().strip() not in ["yes", "y"]:
            print("Thank you for using the Ugandan Language Translator. Goodbye!")
            break

if __name__ == "__main__":
    main()