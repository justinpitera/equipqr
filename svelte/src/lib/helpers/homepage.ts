import { type LanguageKeys } from "$lib/locales";
import { writable, type Writable } from "svelte/store";
import { getCookie } from "./cookies";
import { defaultLang } from "$lib/config";

class HomePageStore {
    constructor(
        public isLoggedIn: Writable<boolean> = writable(typeof window !== 'undefined' ? getCookie('auth') === 'true' : false), // UI Only - Fetch requests will fail anyways without http-only cookie
        public isSettingsHidden: Writable<boolean> = writable(true),
        public isAuthDrawerHidden: Writable<boolean> = writable(true),
        public isIssuesHistoryHidden: Writable<boolean> = writable(true),
        public isRecentIssueDrawerHidden: Writable<boolean> = writable(true),
        public hideTip: Writable<boolean> = writable(false),
        public isPastIssuesForSpecificIDHidden: Writable<boolean> = writable(true),
        public startQRScanner: Writable<boolean> = writable(false),
        public notificationsEnabled: Writable<boolean> = writable(typeof window !== 'undefined' ? localStorage.getItem('notificationsEnabled') !== 'false' : true),
        public darkModeEnabled: Writable<boolean> = writable(typeof window !== 'undefined' ? localStorage.getItem('darkModeEnabled') === 'true' : false),
        public selectedLanguage: Writable<LanguageKeys> = writable((typeof window !== 'undefined' ? (localStorage.getItem('savedLang') || defaultLang) : defaultLang) as LanguageKeys),
        public userRole: Writable<string> = writable(typeof window !== 'undefined' ? getCookie('role') : "employee"),
        public debugMode: Writable<boolean> = writable(false),
        public qrScannerSound: Writable<boolean> = writable(true),
    ) { }
}

export const homePageStore = new HomePageStore();
