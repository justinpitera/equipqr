import { notify } from "$lib/helpers/notify";
import { Utils } from "$lib/helpers/utils.service";

const registerSw = (
	scriptUrl: string,
	updateCheckInterval: number,
): Promise<boolean> =>
	new Promise((resolve, reject) => {
		const swContainer = window.navigator.serviceWorker;
		if (!swContainer) return resolve(false);
		console.info("[ServiceWorker] Registering...");
		const utils = Utils.getInstance();
		utils.onLoad(async () => {
			try {
				await swContainer.register(scriptUrl);
				console.info("[ServiceWorker] Registered successfully.");
				setInterval(() => {
					console.info("[ServiceWorker] Checking for updates...");
					swContainer.ready.then((reg) => reg.update());
				}, updateCheckInterval);
				resolve(true);
			} catch (err) {
				console.error("[ServiceWorker] Failed to register:", err);
				notify("[ServiceWorker]", `Failed to register: ${err}`, "error");
				reject(err);
			}
		});
	});

export async function registerServiceWorker() {
	await registerSw("sw.js", /* 12 hours */ 1000 * 60 * 60 * 12);
}
