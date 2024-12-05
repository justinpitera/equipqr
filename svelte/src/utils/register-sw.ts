import { Utils } from "./utils.service";

export const registerSw = (
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
				reject(err);
			}
		});
	});
