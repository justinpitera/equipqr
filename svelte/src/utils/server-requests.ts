import { notify } from "./notify";

export async function getAppVersion() {
	try {
		const request = await fetch("/api/health/status");
		const response = await request.json();
		console.log(
			"%cAviation Management Panel",
			"font-size: 28px; color: #1e90ff; font-weight: bold; text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.2);",
		);
		if (response.version)
			console.log(
				`%cVersion: %c${response.version}`,
				"font-size: 20px; color: wheat; font-weight: bold;",
				"font-size: 20px; color: #32cd32; font-weight: bold;",
			);
		if (response.status === "healthy") {
			console.log(
				`%cStatus: ${response.status}`,
				"color: green; font-size: 18px; font-weight: bold;",
			);
		} else {
			console.log(
				`%cStatus: ${response.status}`,
				"color: red; font-size: 18px; font-weight: bold;",
			);
		}
		notify(
			"Aviation Management Panel",
			`Version: ${response.version}\nStatus: ${response.status}`,
			response.status === "healthy" ? "success" : "error",
		);
	} catch (e) {
		console.error(
			"%cError fetching status",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Error fetching status", `Failed to get app version: ${e}`, "error");
	}
}
