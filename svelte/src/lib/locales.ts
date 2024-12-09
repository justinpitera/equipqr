import locales from '$lib/locales.json'
import { defaultLang } from './config';
import { homePageStore } from './helpers/homepage';

export type LanguageKeys = "en" | "da" | "no" | "sv";
export const languages = [
  { code: "en", label: "English" },
  { code: "da", label: "Dansk" },
  { code: "no", label: "Norsk" },
  { code: "sv", label: "Svenska" },
];
export type Translations = Record<LanguageKeys, Record<string, string>>;

let selectedLanguage: LanguageKeys = (typeof window !== 'undefined' ? (localStorage.getItem('savedLang') || defaultLang) : defaultLang) as LanguageKeys;
homePageStore.selectedLanguage.subscribe((value) => {
	selectedLanguage = value;
});

export function t_global(key: string): string {
	const langTranslations = translations[selectedLanguage];
	langChecker(key);
	return langTranslations?.[key] || key;
}

export function langChecker(value: string) {
  if (!translations[defaultLang][value]) {
    console.warn(
      `%cWARNING: Missing translation for\n%c${value}%c\nin language '${defaultLang}'`,
      'color: white; background-color: #f59e0b; padding: 3px 6px; border-radius: 3px;',
      'color: #f59e0b; font-weight: bold;',
      'color: white; background-color: #f59e0b; padding: 3px 6px; border-radius: 3px;'
    );
    console.warn(
      `%cINFO: 'bun translate' is now available!`,
      'color: white; background-color: #34d399; padding: 3px 6px; border-radius: 3px;',
    );
    console.warn(
      `%cAuto-translate your text and save it directly to your JSON file.`,
      'color: #34d399; font-weight: bold;',
    );
    console.warn(
      `%cIf a translation is missing, simply enter the text, and 'bun translate' will handle the translation and store it for future use.`,
      'color: #34d399;',
    );
  }
}

export const translations: Translations = locales;
