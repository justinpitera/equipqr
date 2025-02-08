import { notify } from "$lib/helpers/notify";
import { Utils } from "$lib/service-worker/utils.sw";

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
				// console.error("[ServiceWorker] Failed to register:", err);
				notify("[ServiceWorker]", `Failed to register service worker: ${err}`, "error", 1000, true);
				reject(err);
			}
		});
	});

let deferredPrompt: any | null = null;
export async function registerServiceWorker() {
	try {
		await registerSw("sw.js", /* 12 hours */ 1000 * 60 * 60 * 12);
	} catch (e) {}
	// if (DEBUG_MODE) return;
	window.addEventListener('beforeinstallprompt', (e) => {
		deferredPrompt = e; // e.preventDefault();
		return false;
	});
	let showOnce = true;
	window.addEventListener('click', async () => {
		if (!showOnce) return;
		if (deferredPrompt) {
			deferredPrompt.prompt();
			await deferredPrompt.userChoice; // const choiceResult = console.log(`User choice: ${choiceResult.outcome}`);
			deferredPrompt = null;
			showOnce = false;
		}
	});
	window.addEventListener('appinstalled', () => {
		console.log('App was installed successfully');
	});
}
