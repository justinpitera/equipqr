export type LanguageKeys = "en" | "da" | "no" | "sv"; // Language codes
export type TranslationKeys =
  | "authHeader"
  | "languageLabel"
  | "emailLabel"
  | "usernameLabel"
  | "passwordLabel"
  | "emailPlaceholder"
  | "usernamePlaceholder"
  | "passwordPlaceholder"
  | "submitButton"
  | "toggleToEmail"
  | "toggleToCredentials"
  | "emailError"
  | "credentialsError"
  | "emailSuccess"
  | "loginSuccess"; // Translation keys

export type Translations = Record<LanguageKeys, Record<TranslationKeys, string>>;

export const translations: Translations = {
  en: {
    authHeader: "Authentication",
    languageLabel: "Language",
    emailLabel: "Email",
    usernameLabel: "Username",
    passwordLabel: "Password",
    emailPlaceholder: "Enter your email",
    usernamePlaceholder: "Enter your username",
    passwordPlaceholder: "Enter your password",
    submitButton: "Submit",
    toggleToEmail: "Switch to Email Login",
    toggleToCredentials: "Switch to Credentials Login",
    emailError: "Please enter a valid email address.",
    credentialsError: "Please provide both username and password.",
    emailSuccess: "Email sent to {email}",
    loginSuccess: "Login successful!",
  },
  da: {
    authHeader: "Godkendelse",
    languageLabel: "Sprog",
    emailLabel: "E-mail",
    usernameLabel: "Brugernavn",
    passwordLabel: "Adgangskode",
    emailPlaceholder: "Indtast din e-mail",
    usernamePlaceholder: "Indtast dit brugernavn",
    passwordPlaceholder: "Indtast din adgangskode",
    submitButton: "Indsend",
    toggleToEmail: "Skift til e-mail-login",
    toggleToCredentials: "Skift til bruger-login",
    emailError: "Indtast en gyldig e-mailadresse.",
    credentialsError: "Angiv både brugernavn og adgangskode.",
    emailSuccess: "E-mail sendt til {email}",
    loginSuccess: "Login lykkedes!",
  },
  no: {
    authHeader: "Autentisering",
    languageLabel: "Språk",
    emailLabel: "E-post",
    usernameLabel: "Brukernavn",
    passwordLabel: "Passord",
    emailPlaceholder: "Skriv inn e-posten din",
    usernamePlaceholder: "Skriv inn brukernavnet ditt",
    passwordPlaceholder: "Skriv inn passordet ditt",
    submitButton: "Send inn",
    toggleToEmail: "Bytt til e-postinnlogging",
    toggleToCredentials: "Bytt til brukernavninnlogging",
    emailError: "Vennligst skriv inn en gyldig e-postadresse.",
    credentialsError: "Vennligst oppgi både brukernavn og passord.",
    emailSuccess: "E-post sendt til {email}",
    loginSuccess: "Innlogging vellykket!",
  },
  sv: {
    authHeader: "Autentisering",
    languageLabel: "Språk",
    emailLabel: "E-post",
    usernameLabel: "Användarnamn",
    passwordLabel: "Lösenord",
    emailPlaceholder: "Ange din e-postadress",
    usernamePlaceholder: "Ange ditt användarnamn",
    passwordPlaceholder: "Ange ditt lösenord",
    submitButton: "Skicka",
    toggleToEmail: "Byt till e-postinloggning",
    toggleToCredentials: "Byt till användarnamninloggning",
    emailError: "Vänligen ange en giltig e-postadress.",
    credentialsError: "Vänligen ange både användarnamn och lösenord.",
    emailSuccess: "E-post skickad till {email}",
    loginSuccess: "Inloggning lyckades!",
  },
};
