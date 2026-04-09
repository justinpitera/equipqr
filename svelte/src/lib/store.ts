
import { writable, type Writable } from "svelte/store";
import type { LanguageKeys } from "./locales";
import { getCookie } from "./helpers/cookies";
import { defaultLang } from "./config";

class Store {
    constructor(
        public showLoader: Writable<boolean> = writable(false),
        public flashlightOn: Writable<boolean> = writable(false),
        public flashlightDisabled: Writable<boolean> = writable(false),
        public qrCodeData: Writable<string | null> = writable(null),
        public showPopup: Writable<boolean> = writable(false),
        public detectedGSE: Writable<GSEDetails | null> = writable(null),
        public isAutoOpenIssueDetails: Writable<boolean> = writable(typeof window !== "undefined" ? localStorage?.getItem("autoOpenIssueDetails") === "true" : false),
        public isAutoOpenMostRecentIssue: Writable<boolean> = writable(typeof window !== "undefined" ? localStorage?.getItem("autoOpenMostRecentIssue") === "true" : false),
        public hideGSEDetail: Writable<boolean> = writable(true),
        public mediaFiles: Writable<MediaFile[]> = writable([]),
        public fullscreenViewer: Writable<HTMLElement | null> = writable(null),
        public fullscreenImage: Writable<HTMLImageElement | null> = writable(null),
        public fullscreenVideo: Writable<HTMLVideoElement | null> = writable(null),
        public wiggleModeJustPressed: Writable<boolean> = writable(false),
        public isFullScreenMode: Writable<boolean> = writable(false),
        public wiggleModeEnabled: Writable<boolean> = writable(false),
        public isDragging: Writable<boolean> = writable(false),
        public closeReportHidden: Writable<boolean> = writable(true),
        public pressTimer: Writable<NodeJS.Timeout> = writable(),
        public isLoggedIn: Writable<boolean> = writable(typeof window !== 'undefined' ? getCookie('auth') === 'true' : false), // UI Only - Fetch requests will fail anyways without http-only cookie
        public isSettingsHidden: Writable<boolean> = writable(true),
        public isAuthDrawerHidden: Writable<boolean> = writable(true),
        public isIssuesHistoryHidden: Writable<boolean> = writable(true),
        public isRecentIssueDrawerHidden: Writable<boolean> = writable(true),
        public qrPrintDrawerHidden: Writable<boolean> = writable(true),
        public selectGSEIDDrawerHidden: Writable<boolean> = writable(true),
        public gseAction: Writable<Function | undefined> = writable(undefined),
        public addVehiclesDrawerHidden: Writable<boolean> = writable(true),
        public statisticsDrawerHidden: Writable<boolean> = writable(true),
        public cameraDevicesList: Writable<{
            deviceId: string;
            label: string;
            kind: string;
        }[]> = writable([]),
        public hideTip: Writable<boolean> = writable(false),
        public isPastIssuesForSpecificIDHidden: Writable<boolean> = writable(true),
        public startQRScanner: Writable<boolean> = writable(false),
        public notificationsEnabled: Writable<boolean> = writable(typeof window !== 'undefined' ? localStorage.getItem('notificationsEnabled') !== 'false' : true),
        public darkModeEnabled: Writable<boolean> = writable(typeof window !== 'undefined' ? localStorage.getItem('darkModeEnabled') === 'true' : false),
        public selectedLanguage: Writable<LanguageKeys> = writable((typeof window !== 'undefined' ? (localStorage.getItem('savedLang') || defaultLang) : defaultLang) as LanguageKeys),
        public userRole: Writable<string> = writable(typeof window !== 'undefined' ? getCookie('role') || "employee" : "employee"),
        public tenantSlug: Writable<string> = writable(typeof window !== 'undefined' ? getCookie('tenant_slug') || "" : ""),
        public tenantName: Writable<string> = writable(typeof window !== 'undefined' ? getCookie('tenant_name') || "" : ""),
        public debugMode: Writable<boolean> = writable(false),
        public qrScannerSound: Writable<boolean> = writable(true),
        public issues: Writable<HistoryIssue[]> = writable([]),
        public worker_id: Writable<string> = writable(''),
        public issue_description: Writable<string> = writable(''),
        public operable: Writable<string> = writable(''),
        public selected_gate_type: Writable<string> = writable(''),
        public selected_gate_name: Writable<string> = writable(''),
        public is_gate_type_dropdown_open: Writable<boolean> = writable(false),
        public showSuccessStamp: Writable<boolean> = writable(false),
        public gates: Writable<{ value: string; name: string }[]> = writable([]),
        public qrOverlayItems: Writable<QROverlayItem[]> = writable([]),
    ) { }
}

const store = new Store();

export default store;
