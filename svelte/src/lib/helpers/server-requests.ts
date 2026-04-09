import { BACKEND_URL } from "$lib/config";
import { notify } from "$lib/helpers/notify";
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
	EditIssueRequest,
	EditIssueResponse,
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
	UploadFieldImage,
	FieldImageRequest,
	FieldImageResponse,
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
			notify("Service Degraded", `Status: ${response.status}`, "warning", 6000, true);
		}
	} catch (e) {
		console.error(
			"%cError fetching status",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Cannot reach server", `${e}`, "error", 6000, true);
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
			"%cError fetching GSE list",
			"color: red; font-size: 18px; font-weight: bold;",
			e,
		);
		notify("Error fetching GSE list", `Failed to load equipment: ${e}`, "error");
	}
	return undefined;
}

export function getTenantSlug(): string {
	if (typeof window === 'undefined') return '';
	const parts = window.location.hostname.split('.');
	// e.g. acme.localhost → ['acme', 'localhost']  — first part is the tenant
	if (parts.length >= 2 && parts[0] !== 'www' && parts[0] !== '') {
		return parts[0];
	}
	return '';
}

export async function login(email: string): Promise<{ message: string; tenant_name?: string } | undefined> {
	try {
		const controller = new AbortController();
		const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
		const requestData = new LoginRequest();
		requestData.email = email;
		requestData.tenant_slug = getTenantSlug();
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
		return { message: data.message || "", tenant_name: data.tenant_name };
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

export async function uploadGSEImage(imageFile: File, gseId: string): Promise<boolean> {
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort('Request timed out after 30s'), 30000);
        
        const arrayBuffer = await imageFile.arrayBuffer();
        const imageBytes = new Uint8Array(arrayBuffer);
        
        const request = new UploadFieldImage({
            image: imageBytes,
            gse_id: gseId
        });

        const response = await fetch(`${BACKEND_URL}/api/gse/image/upload`, {
            method: 'POST',
            body: request.serializeBinary(),
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/protobuf'
            }
        });
        
        clearTimeout(timeout);
        return response.ok;
    } catch (e) {
        console.error("Error uploading GSE image:", e);
        notify("Error", "Failed to upload GSE image", "error");
        return false;
    }
}

export async function retrieveGSEImage(gseId: string): Promise<string | null> {
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
        
        const request = new FieldImageRequest({
            gse_id: gseId
        });

        const response = await fetch(`${BACKEND_URL}/api/gse/image/retrieve`, {
            method: 'POST',
            body: request.serializeBinary(),
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/protobuf'
            }
        });
        
        clearTimeout(timeout);

        if (!response.ok) return null;

        const responseData = await response.arrayBuffer();
        const responseBytes = new Uint8Array(responseData);
        const data = FieldImageResponse.deserialize(responseBytes);
        
        if (!data.image || data.image.length === 0) return null;
        
        const blob = new Blob([data.image], { type: 'image/jpeg' });
        return URL.createObjectURL(blob);
    } catch (e) {
        console.error("Error retrieving GSE image:", e);
        return null;
    }
}

export async function editIssue(issue_id: string, progress?: string, estimated_time?: string): Promise<boolean> {
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
        
        const requestData = new EditIssueRequest({
            issue_id,
            progress,
            estimated_time
        });

        const response = await fetch(`${BACKEND_URL}/api/gse/issues/edit`, {
            method: 'POST',
            body: requestData.serializeBinary(),
            signal: controller.signal,
            headers: {
                'Content-Type': 'application/protobuf'
            }
        });
        
        clearTimeout(timeout);
        
        if (!response.ok) {
            throw new Error(response.statusText);
        }

        const responseData = await response.arrayBuffer();
        const responseBytes = new Uint8Array(responseData);
        const data = EditIssueResponse.deserialize(responseBytes);
        
        if (debug_routes) console.log("editIssue", data);
        return true;
    } catch (e) {
        console.error("Error editing issue:", e);
        notify("Error", `Failed to edit issue: ${e}`, "error");
        return false;
    }
}

/**
 * Fetches the tenant logo from the backend (which proxies Minio).
 * Returns a blob URL string on success, or null if no logo is set.
 */
export async function getTenantLogo(): Promise<string | null> {
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
        const response = await fetch(`${BACKEND_URL}/api/tenant/logo`, {
            method: 'GET',
            signal: controller.signal,
        });
        clearTimeout(timeout);
        if (!response.ok) return null;
        const blob = await response.blob();
        return URL.createObjectURL(blob);
    } catch {
        return null;
    }
}

get_gates('EKCH');

// ---------------------------------------------------------------------------
// Admin provisioning helpers
// ---------------------------------------------------------------------------

export async function adminCreateTenant(
    secret: string,
    name: string,
    slug: string,
): Promise<{ id: string; name: string; slug: string } | { error: string }> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort('Request timed out after 10s'), 10000);
    try {
        const response = await fetch(`${BACKEND_URL}/api/admin/tenant`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Secret': secret,
            },
            body: JSON.stringify({ name, slug }),
            signal: controller.signal,
        });
        clearTimeout(timeout);
        const data = await response.json();
        if (!response.ok) return { error: data.error ?? response.statusText };
        return data as { id: string; name: string; slug: string };
    } catch (e) {
        clearTimeout(timeout);
        return { error: String(e) };
    }
}

export async function adminInviteUser(
    secret: string,
    email: string,
    tenantSlug: string,
    position: string,
    languagePreference: string,
    sendInvite: boolean,
): Promise<{ id: string; email: string; tenant: string } | { error: string }> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort('Request timed out after 10s'), 10000);
    try {
        const response = await fetch(`${BACKEND_URL}/api/admin/tenant/invite`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-Secret': secret,
            },
            body: JSON.stringify({
                email,
                tenant_slug: tenantSlug,
                position,
                language_preference: languagePreference,
                send_invite: sendInvite,
            }),
            signal: controller.signal,
        });
        clearTimeout(timeout);
        const data = await response.json();
        if (!response.ok) return { error: data.error ?? response.statusText };
        return data as { id: string; email: string; tenant: string };
    } catch (e) {
        clearTimeout(timeout);
        return { error: String(e) };
    }
}

// ---------------------------------------------------------------------------
// Self-service tenant registration
// ---------------------------------------------------------------------------

export async function registerTenant(
    name: string,
    slug: string,
    email: string,
    language: string,
    logoFile?: File,
): Promise<{ tenant_slug: string; tenant_name: string; warning?: string } | { error: string }> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort('Request timed out after 15s'), 15000);
    try {
        const form = new FormData();
        form.append('name', name);
        form.append('slug', slug);
        form.append('email', email);
        form.append('language', language);
        if (logoFile) form.append('logo', logoFile);
        const response = await fetch(`${BACKEND_URL}/api/tenant/register`, {
            method: 'POST',
            body: form,
            signal: controller.signal,
        });
        clearTimeout(timeout);
        const data = await response.json();
        if (!response.ok) return { error: data.error ?? response.statusText };
        return data as { tenant_slug: string; tenant_name: string; warning?: string };
    } catch (e) {
        clearTimeout(timeout);
        return { error: String(e) };
    }
}

export async function uploadTenantLogo(file: File): Promise<{ object_name: string } | { error: string }> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort('Request timed out after 30s'), 30000);
    try {
        const form = new FormData();
        form.append('logo', file);
        const response = await fetch(`${BACKEND_URL}/api/tenant/logo`, {
            method: 'POST',
            body: form,
            signal: controller.signal,
        });
        clearTimeout(timeout);
        const data = await response.json();
        if (!response.ok) return { error: data.error ?? response.statusText };
        return data as { object_name: string };
    } catch (e) {
        clearTimeout(timeout);
        return { error: String(e) };
    }
}

export async function inviteTenantMember(
    email: string,
    position: string,
    languagePreference: string,
    sendInvite: boolean,
): Promise<{ id: string; email: string; warning?: string } | { error: string }> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort('Request timed out after 10s'), 10000);
    try {
        const response = await fetch(`${BACKEND_URL}/api/tenant/invite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email,
                position,
                language_preference: languagePreference,
                send_invite: sendInvite,
            }),
            signal: controller.signal,
        });
        clearTimeout(timeout);
        const data = await response.json();
        if (!response.ok) return { error: data.error ?? response.statusText };
        return data as { id: string; email: string; warning?: string };
    } catch (e) {
        clearTimeout(timeout);
        return { error: String(e) };
    }
}

export async function listTenants(): Promise<{ slug: string; name: string }[]> {
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort('Request timed out after 5s'), 5000);
        const response = await fetch(`${BACKEND_URL}/api/tenants`, { signal: controller.signal });
        clearTimeout(timeout);
        if (!response.ok) return [];
        return await response.json() as { slug: string; name: string }[];
    } catch {
        return [];
    }
}
