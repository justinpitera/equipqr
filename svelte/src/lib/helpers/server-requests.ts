import { BACKEND_URL } from "$lib/config";
import { notify } from "$lib/helpers/notify";
import { t_global } from "$lib/locales";

export async function getAppVersion() {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 3s'), 3000);
		const request = await fetch(`${BACKEND_URL}/api/health/status`, {
            signal: controller.signal,
		});
        clearTimeout(timeout);
		const response = await request.json();
		console.log(
			"%cAviation Failure Reporting",
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
			t_global("Aviation Failure Reporting"),
			`${t_global('Version:')} ${response.version}\n${t_global('Status:')} ${response.status}`,
			response.status === "healthy" ? "success" : "error",
			5000,
			true
		);
	} catch (e) {
		console.error(
			"%cError fetching status",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify(t_global("Error fetching status"), `${t_global('Failed to get app version:')} ${e}`, "error",
			5000,
			true);
	}
}

export async function getGSEDetails(gse_id: string): Promise<GSEDetails | undefined> {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const request = await fetch(`${BACKEND_URL}/api/gse/details`, {
			method: 'POST',
			body: JSON.stringify({
				gse_id
			}),
            signal: controller.signal,
		});
        clearTimeout(timeout);
		const response = await request.json();
		return response as GSEDetails;
	} catch (e) {
		console.error(
			"%cError fetching GSE Details",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Error fetching GSE Details", `Failed to get information: ${e}`, "error");
	}
	return undefined
}

export async function submitIssue(formData: FormData) {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 240s'), 240000);
		const response = await fetch(`${BACKEND_URL}/api/gse/issues/submit`, {
			method: "POST",
			body: formData,
            signal: controller.signal,
		});
        clearTimeout(timeout);

		if (response.ok) {
			const data = await response.json();
			console.log("Status Code:", response.status);
			console.log("Response Data:", data);
		} else {
			console.error("Error submitting the issue:", response.statusText);
		}
	} catch (error) {
		console.error("An error occurred:", error);
	}
}

export async function setLanguage(language: string): Promise<{ token: string } | undefined> {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const response = await fetch(`${BACKEND_URL}/api/lang`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ language }),
			signal: controller.signal,
		});
		clearTimeout(timeout);
		if (!response.ok) throw new Error(response.statusText);
		return response.json();
	} catch (e) {
		console.error(
			"%cError setting language",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Error setting language", `Failed to set language: ${e}`, "error");
	}
	return undefined;
}

export async function login(email: string): Promise<{ token: string } | undefined> {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const response = await fetch(`${BACKEND_URL}/api/auth`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ email }),
			signal: controller.signal,
		});
		clearTimeout(timeout);
		if (!response.ok) throw new Error(response.statusText);
		return response.json();
	} catch (e) {
		console.error(
			"%cError logging in",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Error logging in", `Failed to log in: ${e}`, "error");
	}
	return undefined;
}

export async function logout(): Promise<{ token: string } | undefined> {
	try {
		document.cookie = "auth=; path=/; expires=Thu, 01 Jan 1970 00:00:00 UTC;";
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const response = await fetch(`${BACKEND_URL}/api/auth/logout`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			signal: controller.signal,
		});
		clearTimeout(timeout);
		if (!response.ok) throw new Error(`Failed to log out: ${response.statusText}`);
		return response.json();
	} catch (e) {
		console.error(
			"%cError logging out",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Error logging out", `Failed to log out: ${e}`, "error");
	}
	return undefined;
}
