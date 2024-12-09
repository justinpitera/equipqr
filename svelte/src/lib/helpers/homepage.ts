import { defaultLang, type LanguageKeys } from "$lib/locales";
import { writable, type Writable } from "svelte/store";
import { getCookie } from "./cookies";

class HomePageStore {
    constructor(
        public isLoggedIn: Writable<boolean> = writable(typeof window !== 'undefined' ? getCookie('auth') === 'true' : false), // UI Only - Fetch requests will fail anyways without http-only cookie
        public isSettingsHidden: Writable<boolean> = writable(true),
        public isAuthDrawerHidden: Writable<boolean> = writable(true),
        public isIssuesHistoryHidden: Writable<boolean> = writable(true),
        public isPastIssuesForSpecificIDHidden: Writable<boolean> = writable(true),
        public startQRScanner: Writable<boolean> = writable(false),
        public notificationsEnabled: Writable<boolean> = writable(typeof window !== 'undefined' ? localStorage.getItem('notificationsEnabled') !== 'false' : true),
        public selectedLanguage: Writable<LanguageKeys> = writable((typeof window !== 'undefined' ? (localStorage.getItem('savedLang') || defaultLang) : defaultLang) as LanguageKeys),
        public userRole: Writable<string> = writable("employee"),
        public debugMode: Writable<boolean> = writable(false),
        public qrScannerSound: Writable<boolean> = writable(true),
    ) { }
}

export const homePageStore = new HomePageStore();
