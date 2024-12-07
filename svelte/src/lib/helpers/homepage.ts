import { writable, type Writable } from "svelte/store";

class HomePageStore {
    constructor(
        public isLoggedIn: Writable<boolean> = writable(false),
        public isSettingsHidden: Writable<boolean> = writable(true),
        public isAuthDrawerHidden: Writable<boolean> = writable(true),
        public startQRScanner: Writable<boolean> = writable(false),
    ) { }
}

export const homePageStore = new HomePageStore();
