import translate from 'translate-google';
import readlineSync from 'readline-sync';
import fs from 'node:fs';
import path from 'node:path';

const defaultLang = 'en';
const languages = [
  { code: "en", label: "English" },
  { code: "da", label: "Dansk" },
  { code: "no", label: "Norsk" },
  { code: "sv", label: "Svenska" },
];

// Path to the locales.json file
const localesPath = path.join('src', 'lib', 'locales.json');

// Read the existing locales.json file (if it exists)
let translations = {};
if (fs.existsSync(localesPath)) {
  translations = JSON.parse(fs.readFileSync(localesPath, 'utf-8'));
} else {
  console.log("locales.json file not found, initializing new structure.");
  translations = {
    en: {},
    da: {},
    no: {},
    sv: {},
  };
}

const main = async () => {
  const inputText = readlineSync.question('Enter the text to translate: ');

  for (const lang of languages) {
    if (lang.code === defaultLang) {
        translations[lang.code][inputText] = inputText;
        continue;
    }
    const translatedText = await translate(inputText, { from: defaultLang, to: lang.code });
    if (translatedText) {
      if (!translations[lang.code]) {
        translations[lang.code] = {};
      }
      translations[lang.code][inputText] = translatedText;
      console.log(`Translated to ${lang.label}: ${translatedText}`);
    } else {
      console.log(`Failed to translate to ${lang.label}`);
    }
  }

  // Save updated translations back to locales.json
  fs.writeFileSync(localesPath, JSON.stringify(translations, null, 2), 'utf-8');
  console.log('\nTranslations have been saved to src/lib/locales.json');
};

main();
