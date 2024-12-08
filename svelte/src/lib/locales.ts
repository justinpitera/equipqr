export const defaultLang = 'en';
export type LanguageKeys = "en" | "da" | "no" | "sv";
export const languages = [
  { code: "en", label: "English" },
  { code: "da", label: "Dansk" },
  { code: "no", label: "Norsk" },
  { code: "sv", label: "Svenska" },
];
export type Translations = Record<LanguageKeys, Record<string, string>>;

export function langChecker(value: string) {
  if (!translations[defaultLang][value]) {
    console.warn(
      `%cWARNING: Missing translation for\n'%c${value}%c'\nin language '${defaultLang}'.`,
      'color: white; background-color: #e53e3e; padding: 2px 5px; border-radius: 3px;',
      'color: #e53e3e; font-weight: bold;',
      'color: white; background-color: #e53e3e; padding: 2px 5px; border-radius: 3px;'
    );
  }
}

import locales from '$lib/locales.json'

export const translations: Translations = locales;
