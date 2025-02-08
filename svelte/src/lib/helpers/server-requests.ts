import { BACKEND_URL } from "$lib/config";
import { notify } from "$lib/helpers/notify";
import { t } from "$lib/locales";
import { requests } from '$lib/prototypes/requests/v1/requests';
const {
	// /api/health/status
	// HealthStatusRequest,
	HealthStatusResponse,
	// /api/gse/details
	GSEDetailsRequest,
	GSEDetailsResponse,
	// /api/gse/issues/submit
	SubmitIssueRequest,
	SubmitIssueResponse,
	// /api/gse/issues/fetch
	FetchIssuesRequest,
	FetchIssuesResponse,
	// /api/auth
	LoginRequest,
	LoginResponse,
	// /api/issues/delete
	DeleteIssuesRequest,
	DeleteIssuesResponse,
	// /api/auth/logout
	// LogoutRequest,
	LogoutResponse,
	// /api/locations/fetch
	FetchGatesRequest,
	FetchGatesResponse,
	// /api/gse/all
	ListGSEReponse,
	// Other Types:
	// Issue,
	// Attachment,
	// Gate,
} = requests.v1;

const debug_routes = false;

export async function getAppVersion() {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 3s'), 3000);
		const request = await fetch(`${BACKEND_URL}/api/health/status`, {
			signal: controller.signal,
		});
		clearTimeout(timeout);
		const responseData = await request.arrayBuffer();
		const responseBytes = new Uint8Array(responseData);
		const response = HealthStatusResponse.deserialize(responseBytes);
		if (debug_routes) console.log("getAppVersion", response)
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
			t("Aviation Failure Reporting"),
			`${t('Version:')} ${response.version}\n${t('Status:')} ${t(response.status)}`,
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
		notify(t("Error fetching status"), `${t('Failed to get app version:')} ${t(`${e}`)}`, "error",
			5000,
			true);
	}
}

export async function getGSEDetails(gse_id: string): Promise<GSEDetails | undefined> {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const requestData = new GSEDetailsRequest()
		requestData.gse_id = gse_id;
		const request = await fetch(`${BACKEND_URL}/api/gse/details`, {
			method: 'POST',
			body: requestData.serializeBinary(),
			signal: controller.signal,
			headers: {
				'Content-Type': 'application/protobuf'
			}
		});
		clearTimeout(timeout);
		const responseData = await request.arrayBuffer();
		const responseBytes = new Uint8Array(responseData);
		const response = GSEDetailsResponse.deserialize(responseBytes);
		// if (debug_routes)
		console.log("getGSEDetails", response.toObject()) //  {"f":{},"D":-1,"u":["AHU 00001","H01","Airplane heater unit (AHU)","GSH-1","Polar","AAP","3. Okay",null,"N/A",null,null,null,null,null,0,"success"],"G":1.7976931348623157e+308,"a":{}} asd
		// return response;
		return response.toObject() as GSEDetails;
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

export async function submitIssue(formData: FormData, loadingFunctionBefore: () => void, loadingFunctionAfter: () => void): Promise<{
	id?: string;
} | undefined> {
	loadingFunctionBefore();
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 240s'), 240000);
		const gseId = formData.get("gse_id")?.toString() || undefined;
		const workerId = formData.get("worker_id")?.toString() || undefined;
		const issueDescription = formData.get("issue_description")?.toString() || undefined;
		const isOperable = formData.get("is_operable")?.toString() || undefined;
		const gateType = formData.get("gate_type")?.toString() || undefined;
		const gateName = formData.get("gate_name")?.toString() || undefined;
		const attachments: Uint8Array[] = [];
		const fileAttachments = formData.getAll("attachments");
		for (const attachment of fileAttachments) {
			if (attachment instanceof File) {
				const arrayBuffer = await attachment.arrayBuffer();
				attachments.push(new Uint8Array(arrayBuffer));
			}
		}
		const request = new SubmitIssueRequest({
			gse_id: gseId,
			worker_id: workerId,
			issue_description: issueDescription,
			is_operable: isOperable,
			attachments: attachments,
			gate_type: gateType,
			gate_name: gateName,
		});
		const requestBytes = request.serializeBinary();
		console.log(request.toObject())
		const response = await fetch(`${BACKEND_URL}/api/gse/issues/submit`, {
			method: "POST",
			body: requestBytes,
			signal: controller.signal,
			headers: {
				'Content-Type': 'application/protobuf'
			}
		});
		clearTimeout(timeout);
		if (response.ok) {
			const responseData = await response.arrayBuffer();
			const responseBytes = new Uint8Array(responseData);
			const data = SubmitIssueResponse.deserialize(responseBytes);
			if (debug_routes) console.log("submitIssue", data)
			loadingFunctionAfter();
			return data;
		} else {
			console.error("Error submitting the issue:", response.statusText);
		}
	} catch (error) {
		console.error("An error occurred:", error);
	}
	loadingFunctionAfter();
	return undefined;
}

export async function getIssues(page: number | undefined, issuesPerPage: number | undefined, loadingFunctionBefore: () => void, loadingFunctionAfter: () => void): Promise<{
	data: {
		id: string;
		gse_id: string;
		issue_description: string;
		estimated_time: string;
		reported_at: string;
		reported_by: string | undefined;
		progress: string;
		attachments: {
			id: string;
			file_type: string;
			uploaded_at: string;
		}[]
	}[],
	page: number,
	page_size: number;
	total: number;
} | undefined> {
	loadingFunctionBefore();
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 10s'), 10000);
		const requestData = new FetchIssuesRequest()
		requestData.page = page ?? 1;
		requestData.page_size = issuesPerPage ?? 10;
		const response = await fetch(`${BACKEND_URL}/api/gse/issues/fetch`, {
			method: "POST",
			body: requestData.serializeBinary(),
			signal: controller.signal,
			headers: {
				'Content-Type': 'application/protobuf'
			}
		});
		clearTimeout(timeout);
		if (response.ok) {
			const responseData = await response.arrayBuffer();
			const responseBytes = new Uint8Array(responseData);
			const data = FetchIssuesResponse.deserialize(responseBytes);
			if (debug_routes) console.log("getIssues", data)
			loadingFunctionAfter();
			return data;
		} else {
			console.error("Error submitting the issue:", response.statusText);
		}
	} catch (error) {
		console.error("An error occurred:", error);
	}
	loadingFunctionAfter();
	return undefined;
}

export async function getAllGSEs(): Promise<{ gse_id?: string[] } | undefined> {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const response = await fetch(`${BACKEND_URL}/api/gse/all`, {
			method: 'GET',
			signal: controller.signal
		});
		clearTimeout(timeout);
		if (!response.ok) throw new Error(response.statusText);
		const responseData = await response.arrayBuffer();
		const responseBytes = new Uint8Array(responseData);
		const data = ListGSEReponse.deserialize(responseBytes);
		if (debug_routes) console.log("getAllGSEs", data)
		return data
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

export async function login(email: string): Promise<{ message: string } | undefined> {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const requestData = new LoginRequest();
		requestData.email = email;
		const response = await fetch(`${BACKEND_URL}/api/auth`, {
			method: 'POST',
			body: requestData.serializeBinary(),
			signal: controller.signal,
			headers: {
				'Content-Type': 'application/protobuf'
			}
		});
		clearTimeout(timeout);
		if (!response.ok) throw new Error(response.statusText);
		const responseData = await response.arrayBuffer();
		const responseBytes = new Uint8Array(responseData);
		const data = LoginResponse.deserialize(responseBytes);
		if (debug_routes) console.log("login", data)
		return data;
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

export async function delete_issue(ids: string[]) {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const requestData = new DeleteIssuesRequest();
		requestData.ids = ids;
		const response = await fetch(`${BACKEND_URL}/api/issues/delete`, {
			method: 'POST',
			body: requestData.serializeBinary(),
			signal: controller.signal,
			headers: {
				'Content-Type': 'application/protobuf'
			}
		});
		clearTimeout(timeout);
		if (!response.ok) throw new Error(response.statusText);
		const responseData = await response.arrayBuffer();
		const responseBytes = new Uint8Array(responseData);
		const output = DeleteIssuesResponse.deserialize(responseBytes);
		if (debug_routes) console.log("delete_issue", output)
	} catch (e) {
		console.error(
			"%cError deleting issue",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Error deleting issue", `Failed to delete issue: ${e}`, "error");
	}
}

export async function logout(): Promise<{ token?: string, message?: string } | undefined> {
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
		if (!response.ok) throw new Error(response.statusText);
		const responseData = await response.arrayBuffer();
		const responseBytes = new Uint8Array(responseData);
		const output = LogoutResponse.deserialize(responseBytes);
		return output;
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

export async function get_gates(airport_icao_code: string) {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const requestData = new FetchGatesRequest();
		requestData.icao_code = airport_icao_code;
		const response = await fetch(`${BACKEND_URL}/api/locations/fetch`, {
			method: 'POST',
			body: requestData.serializeBinary(),
			signal: controller.signal,
			headers: {
				'Content-Type': 'application/protobuf'
			}
		});
		clearTimeout(timeout);
		if (!response.ok) throw new Error(response.statusText);
		const responseData = await response.arrayBuffer();
		const responseBytes = new Uint8Array(responseData);
		const output = FetchGatesResponse.deserialize(responseBytes);
		if (debug_routes) console.log("get_gates", output.gates)
		// for (const gate of output.gates) {
		// 	// console.log("gate", gate.id, gate.name)
		// }
	} catch (e) {
		console.error(
			"%cError retrieving gates",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Error retrieving gates", `Failed to retrieve gates: ${e}`, "error");
	}
}

get_gates('EKCH');
