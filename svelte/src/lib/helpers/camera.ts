import jsQR from "jsqr";
import { notify } from "$lib/helpers/notify";
import { getGSEDetails } from "./server-requests";
import { DEBUG_MODE } from "$lib/config";
import store from '$lib/store';
import { t } from "$lib/locales";
let videoTrack: MediaStreamTrack | null = null;
let videoElement: HTMLVideoElement | null = null;
let torchInfo: ITorchInfo = { hasCamera: false, hasTorch: false };
let torch_state = "Uninitialized";

let isAutoOpenIssueDetails: boolean = typeof window !== "undefined" ? localStorage?.getItem("autoOpenIssueDetails") === "true" : false;
store.isAutoOpenIssueDetails.subscribe((value) => {
	isAutoOpenIssueDetails = value;
});

let showPopup: boolean = false;
store.showPopup.subscribe((value) => {
	showPopup = value;
});

let showLoader: boolean = false;
store.showLoader.subscribe((value) => {
	showLoader = value;
});

let isAutoOpenMostRecentIssue: boolean = typeof window !== "undefined" ? localStorage?.getItem("autoOpenMostRecentIssue") === "true" : false;
store.isAutoOpenMostRecentIssue.subscribe((value) => {
	isAutoOpenMostRecentIssue = value;
});

const QUALITY_CONSTRAINTS = { width: { ideal: 1920 }, height: { ideal: 1080 }, frameRate: { ideal: 30, min: 15 } };

/** Opens the best available rear camera as fast as possible. Returns stream+track. */
const openDefaultCamera = async (): Promise<{ stream: MediaStream; track: MediaStreamTrack } | null> => {
	try {
		const stream = await navigator.mediaDevices.getUserMedia({
			video: { facingMode: { ideal: "environment" }, ...QUALITY_CONSTRAINTS }
		});
		const track = stream.getVideoTracks()[0];
		console.log("[camera] Opened rear camera:", track.label, track.getSettings());
		return { stream, track };
	} catch {
		try {
			const stream = await navigator.mediaDevices.getUserMedia({ video: true });
			const track = stream.getVideoTracks()[0];
			console.log("[camera] Opened fallback camera (no facingMode constraint):", track.label, track.getSettings());
			return { stream, track };
		} catch (err) {
			console.error("[camera] Could not access any camera:", err);
			return null;
		}
	}
};

/**
 * Probes whether a track supports torch by trying applyConstraints.
 * getCapabilities().torch is unreliable on many Android devices — it may
 * return false/undefined even when torch IS supported.  Applying torch:false
 * is a no-op that succeeds silently if torch is available, and throws an
 * OverconstrainedError if it is not.
 */
const hasTorchCapability = async (track: MediaStreamTrack): Promise<boolean> => {
	const caps = track.getCapabilities() as ExtendedMediaTrackCapabilities;
	if (caps.torch === true) return true;
	// Fall back to applyConstraints probe for devices that don't report torch in getCapabilities().
	try {
		await track.applyConstraints({ advanced: [{ torch: false } as ExtendedMediaTrackConstraintSet] });
		console.log("[camera] Torch probe succeeded (applyConstraints) for:", track.label);
		return true;
	} catch {
		return false;
	}
};

/**
 * Enumerates all video inputs and returns the first stream whose track
 * supports torch — excluding the already-open defaultDeviceId.
 * Probes are run in parallel; null results are ignored.
 */
const findTorchCamera = (videoInputs: MediaDeviceInfo[], excludeDeviceId: string | undefined): Promise<ITorchInfo | null> => {
	const candidates = videoInputs.filter(d => d.deviceId !== excludeDeviceId);
	if (!candidates.length) return Promise.resolve(null);
	console.log("[camera] Probing", candidates.length, "candidate camera(s) for torch capability...");

	return new Promise<ITorchInfo | null>(resolve => {
		let remaining = candidates.length;
		const done = () => { if (--remaining === 0) { console.log("[camera] No torch camera found among candidates."); resolve(null); } };

		for (const device of candidates) {
			navigator.mediaDevices
				.getUserMedia({ video: { deviceId: { exact: device.deviceId }, ...QUALITY_CONSTRAINTS } })
				.then(async stream => {
					const track = stream.getVideoTracks()[0];
					if (await hasTorchCapability(track)) {
						console.log("[camera] Torch camera found:", track.label, track.getSettings());
						resolve({ hasCamera: true, hasTorch: true, track, stream });
					} else {
						stream.getTracks().forEach(t => t.stop());
						done();
					}
				})
				.catch(done);
		}
	});
};

const getCameraWithTorchInfo = async (): Promise<ITorchInfo> => {
	const devices = await navigator.mediaDevices.enumerateDevices();
	const videoInputs = devices.filter((device) => device.kind === "videoinput");
	console.log("[camera] Detected", videoInputs.length, "video input(s):", videoInputs.map(d => d.label || d.deviceId));
	store.cameraDevicesList.set(videoInputs);
	if (!videoInputs.length) {
		console.warn("[camera] No video inputs available — camera is unavailable!");
		return { hasCamera: false, hasTorch: false, track: undefined, stream: undefined };
	}

	const defaultCam = await openDefaultCamera();
	if (!defaultCam) return { hasCamera: false, hasTorch: false };

	const { stream: defaultStream, track: defaultTrack } = defaultCam;
	const defaultCaps = defaultTrack.getCapabilities() as ExtendedMediaTrackCapabilities;
	console.log("[camera] Default camera capabilities — torch (getCapabilities):", !!defaultCaps.torch, "| zoom:", defaultCaps.zoom ?? "unsupported");

	// Fast path: default camera already has torch (checked via both getCapabilities and applyConstraints probe).
	if (await hasTorchCapability(defaultTrack)) {
		console.log("[camera] Default camera has torch — no background search needed.");
		return { hasCamera: true, hasTorch: true, track: defaultTrack, stream: defaultStream };
	}

	console.log("[camera] Default camera lacks torch — launching background search across other cameras.");
	return { hasCamera: true, hasTorch: false, track: defaultTrack, stream: defaultStream,
		_torchSearchPromise: findTorchCamera(videoInputs, defaultTrack.getSettings().deviceId),
		_defaultStream: defaultStream,
	} as ITorchInfo;
};

// export async function switchCamera(deviceId: string) {
// 	await destroyScanner();
// 	console.log("Waiting for camera to terminate...");
// 	while(showLoader || startQRScanner) {
// 		await new Promise(resolve => setTimeout(resolve, 100)); // Wait 100ms between checks
// 	}
// 	console.log("Reloaded camera...");
// 	await loadQRScanner(undefined, false, deviceId);
// }

// ── Continuous overlay scanner state ─────────────────────────────────────────
let overlayLoopActive = false;
const OVERLAY_TTL_MS = 2000; // remove card after 2 s without seeing the code
const overlayFetchInFlight = new Set<string>();
// Module-level reference so setFrozen can re-kick the loop without a closure
let overlayFrame: ((ts: DOMHighResTimeStamp) => void) | null = null;

/** Start the continuous overlay scanner (Walmart VisPick style).
 *  Keeps the camera running, detects QR codes every frame, and for each new
 *  code fetches GSE details once.  Clicking a card in the UI triggers the
 *  normal report flow instead of it opening automatically. */
export async function loadOverlayScanner() {
	if (overlayLoopActive) return;
	if (showLoader) return;
	store.qrOverlayItems.set([]);
	store.showLoader.set(true);
	try {
		store.startQRScanner.set(true);
		if (!DEBUG_MODE) await destroyScanner();
		overlayLoopActive = true;
		await startOverlayScanLoop();
	} catch (e) {
		console.error("loadOverlayScanner error", e);
	}
	store.showLoader.set(false);
}

/** Returns the camera's optical zoom range, or null if unsupported. */
export function getZoomCapabilities(): { min: number; max: number; step: number } | null {
	if (!videoTrack) return null;
	const caps = videoTrack.getCapabilities() as ExtendedMediaTrackCapabilities;
	if (!caps.zoom) return null;
	return { min: caps.zoom.min ?? 1, max: caps.zoom.max ?? 10, step: caps.zoom.step ?? 0.1 };
}

/** Apply optical zoom level via the MediaStreamTrack constraint API. */
export function setZoom(zoom: number): void {
	if (!videoTrack) return;
	videoTrack.applyConstraints({
		advanced: [{ zoom } as ExtendedMediaTrackConstraintSet],
	}).catch(() => {});
}

/** Freeze or unfreeze the camera feed.  When frozen the video element is
 *  paused and the scan loop stops updating overlay positions, so all cards
 *  remain perfectly still over a static frame. */
export function setFrozen(frozen: boolean): void {
	if (!videoElement) return;
	if (frozen) {
		videoElement.pause();
		overlayLoopActive = false;
	} else {
		videoElement.play();
		if (!overlayLoopActive && overlayFrame) {
			overlayLoopActive = true;
			requestAnimationFrame(overlayFrame);
		}
	}
}

export function stopOverlayScanner() {
	overlayLoopActive = false;
	overlayFrame = null;
	store.qrOverlayItems.set([]);
	overlayFetchInFlight.clear();
	requestAnimationFrame(destroyScanner);
}

/** Selects an overlay item: populates the normal report flow and hides the
 *  overlay so the user can fill in the report.  Does NOT auto-open drawers. */
export async function selectOverlayItem(gse_id: string) {
	store.qrCodeData.set(gse_id);
	store.showPopup.set(true);
	document.getElementById("qrScanner")?.classList.add("hidden");

	let current: QROverlayItem[] = [];
	store.qrOverlayItems.subscribe(v => { current = v; })();
	const cached = current.find(i => i.gse_id === gse_id);

	let gseDetails: GSEDetails | null = cached?.gseDetails ?? null;
	if (!gseDetails) {
		gseDetails = (await getGSEDetails(gse_id)) ?? null;
	}
	if (gseDetails?.gse_id) {
		store.detectedGSE.set(gseDetails);
		if (gseDetails.error && gseDetails.details) {
			notify(gseDetails.error, gseDetails.details, "error");
		} else {
			// User clicked - open detail drawer (same as isCheckOnly)
			store.hideGSEDetail.set(false);
			if (gseDetails.most_recent_issue) store.isRecentIssueDrawerHidden.set(false);
		}
	} else {
		notify("Error", t("Could not find any information for") + ' ' + gse_id, "error", 5000, true);
		store.detectedGSE.set(null);
		store.closeReportHidden.set(false);
	}
}

async function startOverlayScanLoop() {
	if (!navigator.mediaDevices?.getUserMedia) {
		notify("QR Code Scanner", "Could not find an available camera to use for scanning QR codes...", "error");
		overlayLoopActive = false;
		return;
	}

	videoElement = document.createElement("video");
	// Fill the container like a native camera app — no letterboxing, no distortion
	videoElement.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;';
	const videoStreams = document.getElementById("video_streams");
	if (videoStreams) {
		videoStreams.classList.add('hidden');
		videoStreams.append(videoElement);
		videoElement.addEventListener('loadeddata', () => {
			videoStreams.classList.remove('hidden');
		});
	}

	const loadingMessage = document.getElementById("loadingMessage");
	const cameraWithTorch = await getCameraWithTorchInfo();

	if (!videoElement) { overlayLoopActive = false; return; }

	if (!cameraWithTorch.stream || !cameraWithTorch.track) {
		notify("QR Code Scanner", "Could not find an available camera device!", "error");
		overlayLoopActive = false;
		return;
	}

	// Show video immediately using whatever camera opened (default stream).
	videoElement.srcObject = cameraWithTorch.stream;
	videoElement.playsInline = true;
	videoElement.play();
	videoTrack = cameraWithTorch.track;
	console.log("[camera] Overlay scanner video stream started — track:", videoTrack?.label, videoTrack?.getSettings());
	store.showLoader.set(false);

	const wireTorchButton = () => {
		const torchButton = document.getElementById("toggleFlashlight");
		torchButton?.classList.remove('hidden');
		let isTorchLoading = false;
		let debounceTorch = false;
		if (torchButton) torchButton.onclick = async () => {
			if (debounceTorch) { setTimeout(() => { debounceTorch = false; }, 300); return; }
			debounceTorch = true;
			if (isTorchLoading) return;
			isTorchLoading = true;
			try {
				if (!torchInfo.track) { console.warn("[camera] Torch button pressed but torchInfo.track is null"); return; }
				const on = torch_state === "Off";
				console.log("[camera] Toggling flashlight:", on ? "OFF → ON" : "ON → OFF", "| track:", torchInfo.track.label);
				await torchInfo.track.applyConstraints({ advanced: [{ torch: on } as ExtendedMediaTrackConstraintSet] });
				torch_state = on ? "On" : "Off";
				store.flashlightOn.set(on);
				console.log("[camera] Flashlight is now:", torch_state);
			} catch (e) {
				console.error("[camera] Error toggling flashlight:", e);
				notify("QR Code Scanner", `Error toggling flashlight: ${e}`, "error");
			}
			isTorchLoading = false;
			debounceTorch = false;
		};
		torch_state = "Off";
	};

	if (cameraWithTorch.hasTorch) {
		console.log("[camera] Overlay scanner: default camera has torch — wiring button immediately.");
		torchInfo = cameraWithTorch;
		torch_state = "Initializing";
		wireTorchButton();
	} else {
		console.log("[camera] Overlay scanner: no torch on default camera — hiding flashlight button.");
		torchInfo = cameraWithTorch;
		torch_state = "Disabled";
		document.getElementById("toggleFlashlight")?.classList.add('hidden');

		// If there's a background torch search in flight, hook it up when it resolves.
		const searchPromise = (cameraWithTorch as any)._torchSearchPromise as Promise<ITorchInfo | null> | undefined;
		const defaultStream = (cameraWithTorch as any)._defaultStream as MediaStream | undefined;
		if (searchPromise) {
			searchPromise.then(result => {
				if (!result || !overlayLoopActive || !videoElement) {
					// No torch found anywhere or scanner was closed — stay on default stream.
					console.log("[camera] Background torch search: no torch camera found (or scanner closed).");
					store.flashlightDisabled.set(true);
					store.flashlightOn.set(false);
					return;
				}
				// Switch video to the torch-capable camera seamlessly.
				console.log("[camera] Background torch search resolved — switching to torch camera:", result.track?.label);
				defaultStream?.getTracks().forEach(t => t.stop());
				videoElement.srcObject = result.stream!;
				videoTrack = result.track!;
				torchInfo = result;
				torch_state = "Initializing";
				wireTorchButton();
			});
		}
	}

	// Off-screen canvas used only for QR detection — kept small for speed.
	// QR codes decode fine at 640px wide; halving from 1080p saves ~75% pixels.
	const SCAN_W = 640;
	const scanCanvas = document.createElement('canvas');
	const scanCtx = scanCanvas.getContext('2d', { willReadFrequently: true })!;

	// Use native BarcodeDetector (Chrome/Android) when available — it finds all
	// codes in one shot.  Fall back to jsQR mask-and-rescan loop otherwise.
	type BarcodeFormat = 'qr_code';
	interface DetectedBarcode { rawValue: string; boundingBox: DOMRectReadOnly; cornerPoints: { x: number; y: number }[]; }
	interface BarcodeDetectorAPI { detect(source: CanvasImageSource | ImageData): Promise<DetectedBarcode[]>; }
	type BarcodeDetectorCtor = { new(opts: { formats: BarcodeFormat[] }): BarcodeDetectorAPI };
	const nativeDetector: BarcodeDetectorAPI | null = (() => {
		const BD = (typeof window !== 'undefined' && 'BarcodeDetector' in window)
			? (window as unknown as { BarcodeDetector: BarcodeDetectorCtor }).BarcodeDetector
			: null;
		return BD ? new BD({ formats: ['qr_code'] }) : null;
	})();

	function extractBounds(xs: number[], ys: number[], W: number, H: number) {
		const minX = Math.min(...xs) / W * 100;
		const minY = Math.min(...ys) / H * 100;
		const maxX = Math.max(...xs) / W * 100;
		const maxY = Math.max(...ys) / H * 100;
		return { minX, minY, maxX, maxY };
	}

	function scheduleDetailFetch(gse_id: string) {
		if (overlayFetchInFlight.has(gse_id)) return;
		overlayFetchInFlight.add(gse_id);
		getGSEDetails(gse_id).then(details => {
			store.qrOverlayItems.update(its => {
				const it = its.find(i => i.gse_id === gse_id);
				if (it) { it.gseDetails = details ?? null; it.loading = false; }
				overlayFetchInFlight.delete(gse_id);
				return [...its];
			});
		}).catch(() => {
			overlayFetchInFlight.delete(gse_id);
			store.qrOverlayItems.update(its => {
				const it = its.find(i => i.gse_id === gse_id);
				if (it) { it.loading = false; }
				return [...its];
			});
		});
	}

	function upsertOverlayItem(gse_id: string, minX: number, minY: number, maxX: number, maxY: number, now: number) {
		store.qrOverlayItems.update(items => {
			const existing = items.find(i => i.gse_id === gse_id);
			if (existing) {
				existing.x = minX; existing.y = minY;
				existing.width = maxX - minX; existing.height = maxY - minY;
				existing.lastSeen = now;
				return [...items];
			}
			scheduleDetailFetch(gse_id);
			return [...items, {
				gse_id, x: minX, y: minY,
				width: maxX - minX, height: maxY - minY,
				gseDetails: null, loading: true, lastSeen: now,
			} as QROverlayItem];
		});
	}

	// Throttle: only run the decode pass every ~80 ms (≈12fps is plenty for QR)
	let lastScanTs = 0;

	overlayFrame = function _overlayFrame(ts: DOMHighResTimeStamp) {
		if (!overlayLoopActive || !videoTrack || !videoTrack.enabled || !videoElement) return;
		requestAnimationFrame(_overlayFrame); // schedule next frame immediately for fluid video

		if (ts - lastScanTs < 80) return; // skip decode this frame, video still renders
		lastScanTs = ts;

		if (videoElement.readyState !== videoElement.HAVE_ENOUGH_DATA) {
			if (loadingMessage) { loadingMessage.hidden = false; loadingMessage.textContent = "⌛ Loading video..."; }
			return;
		}
		if (loadingMessage) loadingMessage.hidden = true;

		// Scale video down to SCAN_W for decode — preserves aspect ratio
		const scale = SCAN_W / videoElement.videoWidth;
		const W = SCAN_W;
		const H = Math.round(videoElement.videoHeight * scale);
		if (scanCanvas.width !== W) scanCanvas.width = W;
		if (scanCanvas.height !== H) scanCanvas.height = H;
		scanCtx.drawImage(videoElement, 0, 0, W, H);
		const now = Date.now();

		if (nativeDetector) {
			// ── BarcodeDetector path: detect directly from video element ─────
			nativeDetector.detect(videoElement).then(barcodes => {
				for (const bc of barcodes) {
					// BarcodeDetector returns coords relative to source dimensions
					const srcW = videoElement!.videoWidth;
					const srcH = videoElement!.videoHeight;
					const pts = bc.cornerPoints;
					const xs = pts.map(p => p.x);
					const ys = pts.map(p => p.y);
					const { minX, minY, maxX, maxY } = extractBounds(xs, ys, srcW, srcH);
					upsertOverlayItem(bc.rawValue, minX, minY, maxX, maxY, now);
				}
				store.qrOverlayItems.update(items => items.filter(i => now - i.lastSeen < OVERLAY_TTL_MS));
			}).catch(() => {});
		} else {
			// ── jsQR mask-and-rescan loop on downscaled canvas ───────────────
			const MAX_CODES = 10;
			for (let attempt = 0; attempt < MAX_CODES; attempt++) {
				const imageData = scanCtx.getImageData(0, 0, W, H);
				const code = jsQR(imageData.data, W, H, { inversionAttempts: "dontInvert" });
				if (!code) break;

				const loc = code.location;
				const xs = [loc.topLeftCorner.x, loc.topRightCorner.x, loc.bottomLeftCorner.x, loc.bottomRightCorner.x];
				const ys = [loc.topLeftCorner.y, loc.topRightCorner.y, loc.bottomLeftCorner.y, loc.bottomRightCorner.y];
				const rawMinX = Math.min(...xs), rawMinY = Math.min(...ys);
				const rawMaxX = Math.max(...xs), rawMaxY = Math.max(...ys);

				upsertOverlayItem(
					code.data,
					rawMinX / W * 100, rawMinY / H * 100,
					rawMaxX / W * 100, rawMaxY / H * 100,
					now
				);

				// Blank the found region so the next jsQR call finds a different code
				const pad = 10;
				scanCtx.fillStyle = '#000';
				scanCtx.fillRect(
					Math.max(0, rawMinX - pad), Math.max(0, rawMinY - pad),
					Math.min(W, rawMaxX - rawMinX + pad * 2),
					Math.min(H, rawMaxY - rawMinY + pad * 2)
				);
			}
			store.qrOverlayItems.update(items => items.filter(i => now - i.lastSeen < OVERLAY_TTL_MS));
		}
	}

	requestAnimationFrame(overlayFrame);
}

export async function loadQRScanner(forceDebug?: string, isCheckOnly?: boolean) {
	if (showLoader) {
		console.warn("QR Scanner already running")
		return;
	}
	store.qrCodeData.set('');
	store.showLoader.set(true);
	try {
		store.startQRScanner.set(true);
		console.log("Waiting for old scanner to destroy..")
		if (!DEBUG_MODE) await destroyScanner(); // Before
		console.log("Scanning for QR Code...")
		const custom_gse_id = forceDebug || (await scanQRCode()); // Scanning...
		console.log("Found QR Code:", custom_gse_id)
		if (!DEBUG_MODE) requestAnimationFrame(destroyScanner); // After
		console.log("Checking...")
		if (custom_gse_id) {
			console.log("Code Valid!", custom_gse_id)
			// Vibrate on success - short pulse
			if ('vibrate' in navigator) {
				navigator.vibrate(100);
			}
			store.qrCodeData.set(custom_gse_id);
			console.log("isCheckOnly?", isCheckOnly, custom_gse_id)
			if (isCheckOnly) {
				store.startQRScanner.set(false); // Goes back to homepage
			} else {
				store.showPopup.set(true);
			}
			document.getElementById("qrScanner")?.classList.add("hidden");
			console.log("Waiting for GSE details for code:", custom_gse_id)
			const gseDetails = await getGSEDetails(custom_gse_id);
			console.log("gseDetails for code", custom_gse_id, gseDetails)
			if (gseDetails?.gse_id) {
				console.log("Found GSEID", gseDetails.gse_id, 'for code:', custom_gse_id)
				store.detectedGSE.set(gseDetails);
				console.log("Checking for errors:", gseDetails.error, gseDetails.details, 'for code:', custom_gse_id)
				if (gseDetails.error && gseDetails.details) {
					console.warn("Found errors!", 'for code:', custom_gse_id)
					notify(gseDetails.error, gseDetails.details, "error")
				} else {
					console.log("No errors found with the code:", custom_gse_id)
					if (isAutoOpenIssueDetails || isCheckOnly) store.hideGSEDetail.set(false);
					if (gseDetails.most_recent_issue && (isAutoOpenMostRecentIssue || isCheckOnly)) store.isRecentIssueDrawerHidden.set(false);
				}
				console.log("Open ui normally for code", custom_gse_id)
			} else {
				console.warn("Server error for code:", custom_gse_id)
				notify("Error", t("Could not find any information for") + ' ' + custom_gse_id, "error", 5000, true);
				store.detectedGSE.set(null);
				if (showPopup) store.closeReportHidden.set(false);
			}
		} else {
			console.log("Invalid code found!", custom_gse_id)
			// Vibrate error pattern - longer pulses
			if ('vibrate' in navigator) {
				navigator.vibrate([100, 100, 200]);
			}
			store.showPopup.set(false);
			store.detectedGSE.set(null);
			store.qrCodeData.set(t("Unable to read QR code."));
			const loadingMessage = document.getElementById("loadingMessage");
			console.log("loadingMessage", loadingMessage)
			if (loadingMessage) {
				loadingMessage.hidden = false;
				loadingMessage.textContent = '🎥 ' + t('Unable to access video stream (please make sure you have a webcam');
			}
		}
	} catch (e) {
		// Vibrate error pattern
		if ('vibrate' in navigator) {
			navigator.vibrate([100, 100, 200]);
		}
		console.error("loadQRScanner error", e)
	}
	store.showLoader.set(false);
}

export async function destroyScanner() {
	// Stop overlay loop if running
	overlayLoopActive = false;
	overlayFetchInFlight.clear();

	// Turn off the flashlight
	store.flashlightOn.set(false);

	// Stop the video track
	if (videoTrack) {
		videoTrack.stop();
		videoTrack = null;
	}

	// Cleanup the video element
	if (videoElement) {
		videoElement.pause();
		videoElement.src = ""; // Detach the stream
		videoElement.srcObject = null; // Detach the stream
		videoElement.remove(); // Remove from the DOM
		videoElement = null; // Nullify reference
	}

	// Stop all tracks in the torch stream (if any)
	if (torchInfo.stream) {
		torchInfo.stream.getTracks().forEach((track) => track.stop());
		torchInfo.stream = undefined;
	}

	const loadingMessage = document.getElementById("loadingMessage");
	if (loadingMessage) {
		loadingMessage.hidden = false;
		loadingMessage.textContent = "🎥 " + t("Loading Camera...");
	}
}

async function scanQRCode(): Promise<string | null> {
	return new Promise((resolve) => {
		if (
			!navigator.mediaDevices ||
			(navigator.mediaDevices && !navigator.mediaDevices.getUserMedia)
		) {
			notify(
				"QR Code Scanner",
				"Could not find an available camera to use for scanning QR codes...",
				"error",
			);
			resolve(null);
			return;
		}
		videoElement = document.createElement("video");
		videoElement.style.cssText = 'position:absolute;inset:0;width:100%;height:100%;object-fit:cover;';
		const videoStreams = document.getElementById("video_streams");
		if (videoStreams) {
			videoStreams.classList.add('hidden');
			videoStreams.append(videoElement);
			videoElement.addEventListener('loadeddata', () => {
				videoStreams.classList.remove('hidden');
			});
		}
		const loadingMessage = document.getElementById("loadingMessage");
		const outputContainer = document.getElementById("output");
		const outputMessage = document.getElementById("outputMessage");
		const outputData = document.getElementById("outputData");
		getCameraWithTorchInfo().then((cameraWithTorch) => {
			if (!videoElement)
				return notify(
					"QR Code Scanner",
					"Could not find videoElement",
					"error",
				);
			torch_state = "Initializing";
			try {
				torchInfo = cameraWithTorch;
				if (cameraWithTorch.hasTorch) {
					console.log("[camera] scanQRCode: camera has torch — wiring button.");
					const torchButton = document.getElementById("toggleFlashlight");
					torchButton?.classList.remove('hidden');
					// Torch Button Click Event:
					let isTorchLoading = false;
					let debounceTorch = false;
					if (torchButton) torchButton.onclick = async () => {
						if (debounceTorch) {
							setTimeout(() => {
								debounceTorch = false;
							}, 300);
							return;
						}
						debounceTorch = true;
						if (isTorchLoading) return;
						isTorchLoading = true;
						try {
							if (!torchInfo.track) { console.warn("[camera] Torch button pressed but torchInfo.track is null"); return; }
							const on = torch_state === "Off";
							console.log("[camera] Toggling flashlight:", on ? "OFF → ON" : "ON → OFF", "| track:", torchInfo.track.label);
							await torchInfo.track.applyConstraints({
								advanced: [{ torch: on } as ExtendedMediaTrackConstraintSet],
							});
							torch_state = on ? "On" : "Off";
							store.flashlightOn.set(on);
							console.log("[camera] Flashlight is now:", torch_state);
							notify(
								"QR Code Scanner",
								`Flashlight turned ${on ? "on" : "off"}.`,
								"info",
							);
						} catch (e) {
							console.error("[camera] Error toggling flashlight:", e);
							notify("QR Code Scanner", `Error toggling flashlight: ${e}`, "error");
						}
						isTorchLoading = false;
						debounceTorch = false;
					};
					torch_state = "Off";
				} else {
					console.log("[camera] scanQRCode: no torch capability — hiding flashlight button.");
					const torchButton = document.getElementById("toggleFlashlight");
					torchButton?.classList.add('hidden');
					torch_state = "Disabled";
				}
				if (!cameraWithTorch.stream || !cameraWithTorch.track) return notify("QR Code Scanner", "Could not find an available camera device!", "error");
				videoElement.srcObject = cameraWithTorch.stream;
				videoElement.playsInline = true;
				videoElement.play();
				videoTrack = cameraWithTorch.track;
				console.log("[camera] scanQRCode video stream started — track:", videoTrack?.label, videoTrack?.getSettings());
				requestAnimationFrame(qrScanner);
			} catch (error) {
				const torchButton = document.getElementById("toggleFlashlight");
				torchButton?.classList.add('hidden');
				torch_state = "Disabled";
				console.error((error as Error).message)
			}
		});
		let cancelThisQRScanner = false;
		function qrScanner() {
			if (cancelThisQRScanner || !videoTrack || !videoTrack.enabled || !videoElement || !loadingMessage || !outputContainer || !outputMessage || !outputData || !outputData.parentElement)
				return notify("QR Code Scanner", "Camera has been closed", "success");
			if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
				loadingMessage.hidden = true;
				outputContainer.hidden = false;
				const canvasElement = document.createElement('canvas');
				canvasElement.width = videoElement.videoWidth;
				canvasElement.height = videoElement.videoHeight;
				const canvas = canvasElement.getContext('2d');
				if (!canvas) return;
				canvas.drawImage(videoElement, 0, 0);
				const imageData = canvas.getImageData(
					0,
					0,
					canvasElement.width,
					canvasElement.height,
					{
						// @ts-ignore
						willReadFrequently: true
					}
				);
				canvasElement.remove();
				const code = jsQR(imageData.data, imageData.width, imageData.height, {
					inversionAttempts: "dontInvert",
				});
				if (code) {
					// drawLine(
					// 	code.location.topLeftCorner,
					// 	code.location.topRightCorner,
					// 	"#FF3B58",
					// );
					// drawLine(
					// 	code.location.topRightCorner,
					// 	code.location.bottomRightCorner,
					// 	"#FF3B58",
					// );
					// drawLine(
					// 	code.location.bottomRightCorner,
					// 	code.location.bottomLeftCorner,
					// 	"#FF3B58",
					// );
					// drawLine(
					// 	code.location.bottomLeftCorner,
					// 	code.location.topLeftCorner,
					// 	"#FF3B58",
					// );
					outputMessage.hidden = true;
					outputData.parentElement.hidden = false;
					outputData.innerText = code.data;
					console.log("code.data", code.data)
					if (torchInfo.hasTorch && torchInfo.track) {
						try {
							torchInfo.track.applyConstraints({
								advanced: [{ torch: false } as ExtendedMediaTrackConstraintSet],
							}).then(() => {
								torch_state = "Off";
								store.flashlightOn.set(false);
							});
						} catch (e) { }
					}
					resolve(code.data);
					cancelThisQRScanner = true;
					return;
				} else {
					outputMessage.hidden = false;
					outputData.parentElement.hidden = true;
				}
			} else {
				loadingMessage.innerText = "⌛ Loading video...";
			}
			setTimeout(() => {
				requestAnimationFrame(qrScanner);
			}, 300);
		}
	});
}
