const axios = require('axios');
const readlineSync = require('readline-sync');
const fs = require('fs');  // Importing the filesystem module to save data

const languages = [
  { code: "en", label: "English" },
  { code: "da", label: "Dansk" },
  { code: "no", label: "Norsk" },
  { code: "sv", label: "Svenska" },
];

const translations = {
  en: {},
  da: {},
  no: {},
  sv: {},
};

const API_URL = "https://libretranslate.com/translate"; // LibreTranslate API

async function translateText(text, targetLang) {
  try {
    const response = await axios.post(API_URL, null, {
      params: {
        q: text,
        source: 'en', // Assuming the input is in English
        target: targetLang,
      },
    });
    return response.data.translatedText;
  } catch (error) {
    console.error(`Error translating to ${targetLang}:`, error.message);
    return null;
  }
}

async function main() {
  const inputText = readlineSync.question('Enter the text to translate: ');

  for (const lang of languages) {
    const translatedText = await translateText(inputText, lang.code);
    if (translatedText) {
      translations[lang.code][inputText] = translatedText;
      console.log(`Translated to ${lang.label}: ${translatedText}`);
    } else {
      console.log(`Failed to translate to ${lang.label}`);
    }
  }

  // Save translations to example.json file
  fs.writeFileSync('example.json', JSON.stringify(translations, null, 2), 'utf-8');
  console.log('\nTranslations have been saved to example.json');
}

main();
