import { notify } from "$lib/helpers/notify";

export async function getAppVersion() {
	try {
		const request = await fetch("https://preview.pitera.co:7878/api/health/status");
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

export async function getGSEDetails(gse_id: string): Promise<GSEDetails | undefined> {
	try {
		const request = await fetch("https://preview.pitera.co:7878/api/gse/details", {
			method: 'POST',
			body: JSON.stringify({
				gse_id
			})
		});
		const response = await request.json();
		return response as GSEDetails;
	} catch (e) {
		console.error(
			"%cError fetching GSE Details",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Error fetching GSE Details", `Failed to get vehicle information: ${e}`, "error");
	}
	return undefined
}

export async function submitIssue(formData: FormData) {
    try {
      const response = await fetch("https://preview.pitera.co:7878/api/gse/issues/submit", {
        method: "POST",
        body: formData,
      });

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