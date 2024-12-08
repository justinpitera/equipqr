import { DEBUG_MODE } from "$lib/config";
import { notify } from "$lib/helpers/notify";
import { Utils } from "$lib/helpers/utils.service";

const registerSw = (
	scriptUrl: string,
	updateCheckInterval: number,
): Promise<boolean> =>
	new Promise((resolve, reject) => {
		const swContainer = window.navigator.serviceWorker;
		if (!swContainer) return resolve(false);
		const utils = Utils.getInstance();
		utils.onLoad(async () => {
			try {
				await swContainer.register(scriptUrl);
				setInterval(() => {
					swContainer.ready.then((reg) => reg.update());
				}, updateCheckInterval);
				resolve(true);
			} catch (err) {
				console.error("[ServiceWorker] Failed to register:", err);
				notify("[ServiceWorker]", `Failed to register service worker: ${err}`, "error");
				reject(err);
			}
		});
	});

let deferredPrompt: any | null = null;
let attempts: number = 0;
export async function registerServiceWorker() {
	await registerSw("sw.js", /* 12 hours */ 1000 * 60 * 60 * 12);
	if (DEBUG_MODE) return;
	window.addEventListener('beforeinstallprompt', (e) => {
		deferredPrompt = e; // e.preventDefault();
		return false;
	});
	window.addEventListener('click', async () => {
		if (deferredPrompt) {
			if (attempts === 2) return;
			attempts += 1;
			deferredPrompt.prompt();
			await deferredPrompt.userChoice; // const choiceResult = console.log(`User choice: ${choiceResult.outcome}`);
			deferredPrompt = null;
		}
	});
	window.addEventListener('appinstalled', () => {
		alert('App was installed');
	});
}
