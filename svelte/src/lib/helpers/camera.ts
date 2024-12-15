import jsQR from "jsqr";
import type { Point } from "jsqr/dist/locator";
import { notify } from "$lib/helpers/notify";
import { writable, type Writable } from "svelte/store";
import { getGSEDetails } from "./server-requests";
import { detailsDrawerStore } from "./details";
import { homePageStore } from "./homepage";
import { DEBUG_MODE } from "$lib/config";
import { cancelReportStore } from "./cancel-report";
import { t_global } from "$lib/locales";
let videoTrack: MediaStreamTrack | null = null;
let videoElement: HTMLVideoElement | null = null;
let torchInfo: ITorchInfo = { hasCamera: false, hasTorch: false };
let torch_state = "Uninitialized";

class QRScannerStore {
	constructor(
		public showLoader: Writable<boolean> = writable(false),
		public flashlightOn: Writable<boolean> = writable(false),
		public flashlightDisabled: Writable<boolean> = writable(false),
		public qrCodeData: Writable<string | null> = writable(null),
		public showPopup: Writable<boolean> = writable(false),
		public detectedGSE: Writable<GSEDetails | null> = writable(null),
		public isAutoOpenIssueDetails: Writable<boolean> = writable(typeof window !== "undefined" ? localStorage?.getItem("autoOpenIssueDetails") === "true" : false),
		public isAutoOpenMostRecentIssue: Writable<boolean> = writable(typeof window !== "undefined" ? localStorage?.getItem("autoOpenMostRecentIssue") === "true" : false),
	) { }
}

export const qrScannerStore = new QRScannerStore();

let isAutoOpenIssueDetails: boolean = typeof window !== "undefined" ? localStorage?.getItem("autoOpenIssueDetails") === "true" : false;
qrScannerStore.isAutoOpenIssueDetails.subscribe((value) => {
	isAutoOpenIssueDetails = value;
});

let isAutoOpenMostRecentIssue: boolean = typeof window !== "undefined" ? localStorage?.getItem("autoOpenMostRecentIssue") === "true" : false;
qrScannerStore.isAutoOpenMostRecentIssue.subscribe((value) => {
	isAutoOpenMostRecentIssue = value;
});

const getCameraWithTorchInfo = async (): Promise<ITorchInfo> => {
	await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
	const devices = await navigator.mediaDevices.enumerateDevices();
	console.log("Available devices:", devices);
	const videoInputs = devices.filter((device) => device.kind === "videoinput");
	console.log("Available cameras:", videoInputs);
	let lastStream: MediaStream | undefined = undefined;
	let lastTrack: MediaStreamTrack | undefined = undefined;
	let lastDevice: MediaDeviceInfo | undefined = undefined;
	const collectedTracks: {
		device_id: string;
		track: MediaStreamTrack;
	}[] = [];
	for (const device of videoInputs) {
		try {
			// notify(
			// 	"QR Code Scanner",
			// 	`Checking Device: ${device.label} - ${device.deviceId}`,
			// 	"info",
			// );
			const stream = await navigator.mediaDevices.getUserMedia({
				video: { facingMode: "environment", deviceId: { exact: device.deviceId } },
			});
			const track = stream.getVideoTracks()[0];
			const capabilities = track.getCapabilities() as ExtendedMediaTrackCapabilities;
			console.log(`Capabilities for ${device.label}:`, capabilities);
			lastStream = stream;
			lastTrack = track;
			lastDevice = device;
			if (capabilities.torch) {
				for (const collectedTrack of collectedTracks) {
					collectedTrack.track.stop();
				}
				return { hasCamera: true, hasTorch: true, track, stream };
			}
			collectedTracks.push({
				device_id: device.deviceId,
				track,
			});
		} catch (error) {
			continue; // `Error accessing camera ${device.label}: ${error}`
		}
	}
	for (const collectedTrack of collectedTracks) {
		if (lastDevice?.deviceId !== collectedTrack.device_id) collectedTrack.track.stop();
	}
	torch_state = "Disabled";
	qrScannerStore.flashlightOn.set(false);
	qrScannerStore.flashlightDisabled.set(true);
	console.warn("No camera with torch capability found.");
	return { hasCamera: videoInputs.length > 0, hasTorch: false, track: lastTrack, stream: lastStream };
};

export async function loadQRScanner(forceDebug?: string) {
	qrScannerStore.showLoader.set(true);
	homePageStore.startQRScanner.set(true);
	if (!DEBUG_MODE) await destroyScanner();
	const custom_gse_id = forceDebug || (await scanQRCode());
	if (!DEBUG_MODE) requestAnimationFrame(destroyScanner);
	if (custom_gse_id) {
		// homePageStore.startQRScanner.set(false); // Goes back to homepage
		qrScannerStore.qrCodeData.set(custom_gse_id);
		qrScannerStore.showPopup.set(true);
		document.getElementById("qrScanner")?.classList.add("hidden");
		const gseDetails = await getGSEDetails(custom_gse_id);
		if (gseDetails?.gse_id) {
			qrScannerStore.detectedGSE.set(gseDetails);
			if (gseDetails.error && gseDetails.details) {
				notify(gseDetails.error, gseDetails.details, "error")
			} else {
				if (isAutoOpenIssueDetails) detailsDrawerStore.hideGSEDetail.set(false);
				if (isAutoOpenMostRecentIssue) homePageStore.isRecentIssueDrawerHidden.set(false);
			}
		} else {
			notify("Error", t_global("Could not find any information for") + ' ' + custom_gse_id, "error");
			qrScannerStore.detectedGSE.set(null);
			cancelReportStore.closeReportHidden.set(false);
		}
	} else {
		qrScannerStore.showPopup.set(false);
		qrScannerStore.detectedGSE.set(null);
		qrScannerStore.qrCodeData.set("Unable to read QR code.");
		const loadingMessage = document.getElementById("loadingMessage");
		if (loadingMessage) {
			loadingMessage.hidden = false;
			loadingMessage.textContent = '🎥 Unable to access video stream (please make sure you have a webcam';
		}
	}
	qrScannerStore.showLoader.set(false);
}

export async function destroyScanner() {
	// Turn off the flashlight
	qrScannerStore.flashlightOn.set(false);

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

	// Hide and clear the canvas
	const canvasElement = document.getElementById("canvas") as HTMLCanvasElement;
	if (canvasElement) {
		canvasElement.hidden = true;
		const canvas = canvasElement.getContext("2d", { willReadFrequently: true });
		if (canvas) {
			canvas.clearRect(0, 0, canvasElement.width, canvasElement.height);
		}
	}

	const loadingMessage = document.getElementById("loadingMessage");
	if (loadingMessage) {
		loadingMessage.hidden = false;
		loadingMessage.textContent = "🎥 Loading Camera...";
	}

	const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
	stream.getTracks().forEach((track) => track.stop());
	const devices = await navigator.mediaDevices.enumerateDevices();
	const activeStreams = devices.filter((device) => device.kind === "videoinput");
	console.log("Active video streams:", activeStreams);
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
		const canvasElement = document.getElementById(
			"canvas",
		) as HTMLCanvasElement;
		const canvas = canvasElement.getContext("2d", {
			willReadFrequently: true,
		});
		if (canvas) canvas.willReadFrequently = true;
		const loadingMessage = document.getElementById("loadingMessage");
		const outputContainer = document.getElementById("output");
		const outputMessage = document.getElementById("outputMessage");
		const outputData = document.getElementById("outputData");
		function drawLine(
			begin: Point,
			end: Point,
			color: string | CanvasGradient | CanvasPattern,
		) {
			if (!canvas)
				return notify("QR Code Scanner", "Could not find canvas", "error");
			canvas.beginPath();
			canvas.moveTo(begin.x, begin.y);
			canvas.lineTo(end.x, end.y);
			canvas.lineWidth = 4;
			canvas.strokeStyle = color;
			canvas.stroke();
		}
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
					const torchButton = document.getElementById("toggleFlashlight");
					torchButton?.classList.remove('hidden');
					torchButton?.addEventListener("click", async () => {
						try {
							if (!torchInfo.track) return;
							const on = torch_state === "Off";
							await torchInfo.track.applyConstraints({
								advanced: [{ torch: on } as ExtendedMediaTrackConstraintSet],
							});
							torch_state = on ? "On" : "Off";
							qrScannerStore.flashlightOn.set(on);
							notify(
								"QR Code Scanner",
								`Flashlight turned ${on ? "on" : "off"}.`,
								"info",
							);
						} catch (e) {
							notify("QR Code Scanner", `Error toggling flashlight: ${e}`, "error");
						}
					});
					torch_state = "Off";
				} else {
					const torchButton = document.getElementById("toggleFlashlight");
					torchButton?.classList.add('hidden');
					torch_state = "Disabled";
				}
				if (!cameraWithTorch.stream || !cameraWithTorch.track) return notify("QR Code Scanner", "Could not find an available camera device!", "error");
				videoElement.srcObject = cameraWithTorch.stream;
				videoElement.playsInline = true;
				videoElement.play();
				videoTrack = cameraWithTorch.track;
				requestAnimationFrame(qrScanner);
			} catch (error) {
				const torchButton = document.getElementById("toggleFlashlight");
				torchButton?.classList.add('hidden');
				torch_state = "Disabled";
				console.error((error as Error).message)
			}
		});
		function qrScanner() {
			if (!videoTrack) return;
			if (!videoTrack.enabled) return;
			if (!videoElement)
				return notify(
					"QR Code Scanner",
					"Could not find videoElement",
					"error",
				);
			if (!loadingMessage)
				return notify(
					"QR Code Scanner",
					"Could not find loadingMessage",
					"error",
				);
			if (!outputContainer)
				return notify(
					"QR Code Scanner",
					"Could not find outputContainer",
					"error",
				);
			if (!canvas)
				return notify("QR Code Scanner", "Could not find canvas", "error");
			if (!outputMessage)
				return notify(
					"QR Code Scanner",
					"Could not find outputMessage",
					"error",
				);
			if (!outputData)
				return notify("QR Code Scanner", "Could not find outputData", "error");
			if (!outputData.parentElement)
				return notify(
					"QR Code Scanner",
					"Could not find outputData parent",
					"error",
				);
			if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
				loadingMessage.hidden = true;
				canvasElement.hidden = false;
				outputContainer.hidden = false;
				canvasElement.height = videoElement.videoHeight;
				canvasElement.width = videoElement.videoWidth;
				canvas.drawImage(
					videoElement,
					0,
					0,
					canvasElement.width,
					canvasElement.height,
				);
				canvas.willReadFrequently = true;
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
				const code = jsQR(imageData.data, imageData.width, imageData.height, {
					inversionAttempts: "dontInvert",
				});
				if (code) {
					drawLine(
						code.location.topLeftCorner,
						code.location.topRightCorner,
						"#FF3B58",
					);
					drawLine(
						code.location.topRightCorner,
						code.location.bottomRightCorner,
						"#FF3B58",
					);
					drawLine(
						code.location.bottomRightCorner,
						code.location.bottomLeftCorner,
						"#FF3B58",
					);
					drawLine(
						code.location.bottomLeftCorner,
						code.location.topLeftCorner,
						"#FF3B58",
					);
					outputMessage.hidden = true;
					outputData.parentElement.hidden = false;
					outputData.innerText = code.data;
					if (torchInfo.hasTorch && torchInfo.track) {
						try {
							torchInfo.track.applyConstraints({
								advanced: [{ torch: false } as ExtendedMediaTrackConstraintSet],
							}).then(() => {
								torch_state = "Off";
								qrScannerStore.flashlightOn.set(false);
							});
						} catch (e) { }
					}
					resolve(code.data);
				} else {
					outputMessage.hidden = false;
					outputData.parentElement.hidden = true;
				}
			} else {
				loadingMessage.innerText = "⌛ Loading video...";
			}
			requestAnimationFrame(qrScanner);
		}
	});
}
