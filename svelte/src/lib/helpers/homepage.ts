import { writable, type Writable } from "svelte/store";

class HomePageStore {
    constructor(
        public isLoggedIn: Writable<boolean> = writable(false),
        public isSettingsHidden: Writable<boolean> = writable(true),
        public isAuthDrawerHidden: Writable<boolean> = writable(true),
        public isIssuesHistoryHidden: Writable<boolean> = writable(true),
        public startQRScanner: Writable<boolean> = writable(false),
        public darkMode: Writable<boolean> = writable(false),
        public notificationsEnabled: Writable<boolean> = writable(true),
        public selectedLanguage: Writable<string> = writable("en"),
        public debugMode: Writable<boolean> = writable(false),
        public qrScannerSound: Writable<boolean> = writable(true),
    ) { }
}

export const homePageStore = new HomePageStore();
