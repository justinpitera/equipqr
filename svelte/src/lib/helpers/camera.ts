import jsQR from "jsqr";
import type { Point } from "jsqr/dist/locator";
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

let startQRScanner: boolean = false;
store.startQRScanner.subscribe((value) => {
	startQRScanner = value;
});

let showLoader: boolean = false;
store.showLoader.subscribe((value) => {
	showLoader = value;
});

let isAutoOpenMostRecentIssue: boolean = typeof window !== "undefined" ? localStorage?.getItem("autoOpenMostRecentIssue") === "true" : false;
store.isAutoOpenMostRecentIssue.subscribe((value) => {
	isAutoOpenMostRecentIssue = value;
});

const getCameraWithTorchInfo = async (customDevice?: string): Promise<ITorchInfo> => {
	const devices = await navigator.mediaDevices.enumerateDevices();
	console.log("Available devices:", devices);
	const videoInputs = devices.filter((device) => device.kind === "videoinput");
	console.log("Available cameras:", videoInputs);
	store.cameraDevicesList.set(videoInputs);
	if (videoInputs && videoInputs.length > 0) {
		const test_stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: true });
		test_stream.getTracks().forEach(t => {
			t.stop();
			test_stream.removeTrack(t);
		});
	} else {
		console.warn("camera is unavailable!");
		return { hasCamera: false, hasTorch: false, track: undefined, stream: undefined };
	}
	let lastStream: MediaStream | undefined = undefined;
	let lastTrack: MediaStreamTrack | undefined = undefined;
	let lastDevice: MediaDeviceInfo | undefined = undefined;
	const collectedTracks: {
		device_id: string;
		track: MediaStreamTrack;
	}[] = [];
	for (const device of videoInputs) {
		try {
			// if (device.label.toLowerCase().indexOf('back') >= 0)
			if (!customDevice && device.label.toLowerCase().indexOf('front') >= 0) continue;
			// notify(
			// 	"QR Code Scanner",
			// 	`Checking Device: ${device.label} - ${device.deviceId} - ${JSON.stringify(device)}`,
			// 	"info",
			// );
			// if (lastStream) {
			// 	lastStream.getTracks().forEach(t => {
			// 		t.stop();
			// 		lastStream?.removeTrack(t);
			// 	});
			// }
			console.log("loading device:", device.deviceId, device)
			const stream = await navigator.mediaDevices.getUserMedia({
				video: {
					facingMode: "environment",
					deviceId: { exact: device.deviceId },
					// width: { ideal: 4096 },
					// height: { ideal: 2160 },
					// frameRate: { ideal: 60 }
				},
				// audio: true
			});
			const track = stream.getVideoTracks()[0];
			// notify(
			// 	"QR Code Scanner",
			// 	`Checking track: ${track}`,
			// 	"info",
			// 	3000,
			// 	true
			// );
			const capabilities = track.getCapabilities() as ExtendedMediaTrackCapabilities;
			console.log(`Capabilities for ${device.label}:`, capabilities);
			lastStream = stream;
			lastTrack = track;
			lastDevice = device;
			if (capabilities.torch) {
				const videoSource = document.getElementById('videoSource') as HTMLSelectElement;
				if (videoSource) videoSource.value = device.deviceId;
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
			// notify(
			// 	"QR Code Scanner",
			// 	`Could not start camera: ${error}`,
			// 	"info",
			// 	3000,
			// 	true
			// );
			continue; // `Error accessing camera ${device.label}: ${error}`
		}
	}
	for (const collectedTrack of collectedTracks) {
		if (lastDevice?.deviceId !== collectedTrack.device_id) collectedTrack.track.stop();
	}
	torch_state = "Disabled";
	store.flashlightOn.set(false);
	store.flashlightDisabled.set(true);
	console.warn("No camera with torch capability found.");
	const videoSource = document.getElementById('videoSource') as HTMLSelectElement;
	if (videoSource && lastDevice) videoSource.value = lastDevice.deviceId;
	return { hasCamera: videoInputs.length > 0, hasTorch: false, track: lastTrack, stream: lastStream };
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

export async function loadQRScanner(forceDebug?: string, isCheckOnly?: boolean, customDevice?: string) {
	if (showLoader || startQRScanner) {
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
		const custom_gse_id = forceDebug || (await scanQRCode(customDevice)); // Scanning...
		console.log("Found QR Code:", custom_gse_id)
		if (!DEBUG_MODE) requestAnimationFrame(destroyScanner); // After
		console.log("Checking...")
		if (custom_gse_id) {
			console.log("Code Valid!", custom_gse_id)
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
		console.error("loadQRScanner error", e)
	}
	store.showLoader.set(false);
}

export async function destroyScanner() {
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
		loadingMessage.textContent = "🎥 " + t("Loading Camera...");
	}
}

async function scanQRCode(customDevice?: string): Promise<string | null> {
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
		getCameraWithTorchInfo(customDevice).then((cameraWithTorch) => {
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
						isTorchLoading = true
						try {
							if (!torchInfo.track) return;
							const on = torch_state === "Off";
							await torchInfo.track.applyConstraints({
								advanced: [{ torch: on } as ExtendedMediaTrackConstraintSet],
							});
							torch_state = on ? "On" : "Off";
							store.flashlightOn.set(on);
							notify(
								"QR Code Scanner",
								`Flashlight turned ${on ? "on" : "off"}.`,
								"info",
							);
						} catch (e) {
							notify("QR Code Scanner", `Error toggling flashlight: ${e}`, "error");
						}
						isTorchLoading = false;
					};
					torch_state = "Off";
				} else {
					const torchButton = document.getElementById("toggleFlashlight");
					torchButton?.classList.add('hidden');
					torch_state = "Disabled";
				}
				if (!cameraWithTorch.stream || !cameraWithTorch.track) return notify("QR Code Scanner", "Could not find an available camera device!", "error");
				if (customDevice) {
					console.log("Using custom device:", customDevice);
					navigator.mediaDevices.getUserMedia({
						video: {
							deviceId: { exact: customDevice }
						}
					}).then(stream => {
						if (!videoElement) return console.error("Missing Video Element");
						videoElement.srcObject = stream;
						videoElement.playsInline = true;
						videoElement.play();
						videoTrack = stream.getVideoTracks()[0];
						requestAnimationFrame(qrScanner);
					}).catch(error => {
						if (!videoElement) return console.error("Missing Video Element");
						if (!cameraWithTorch.stream) return console.error("Missing Video Element Stream");
						if (!cameraWithTorch.track) return console.error("Missing Video Element Track");
						console.error("Error accessing custom device:", error);
						// Fallback to default camera
						videoElement.srcObject = cameraWithTorch.stream;
						videoElement.playsInline = true;
						videoElement.play();
						videoTrack = cameraWithTorch.track;
						requestAnimationFrame(qrScanner);
					});
				} else {
					videoElement.srcObject = cameraWithTorch.stream;
					videoElement.playsInline = true;
					videoElement.play();
					videoTrack = cameraWithTorch.track;
					requestAnimationFrame(qrScanner);
				}
			} catch (error) {
				const torchButton = document.getElementById("toggleFlashlight");
				torchButton?.classList.add('hidden');
				torch_state = "Disabled";
				console.error((error as Error).message)
			}
		});
		let cancelThisQRScanner = false;
		function qrScanner() {
			if (cancelThisQRScanner) return;
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
			requestAnimationFrame(qrScanner);
		}
	});
}
