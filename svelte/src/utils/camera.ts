import jsQR from "jsqr";
import type { Point } from "jsqr/dist/locator";
import { notify } from "./notify";
import { DEBUG_MODE } from "../config";
let videoTrack: MediaStreamTrack | null = null;
let videoElement: HTMLVideoElement | null = null;
let flashlightOn = false;

export function toggleScanner(enabled: boolean) {
	if (!videoTrack) {
		if (!DEBUG_MODE) notify("Error", "Could not find videoTrack", "error");
		return
	}
	videoTrack.enabled = enabled;
}

export function destroyScanner() {
	flashlightOn = false;
	const canvasElement = document.getElementById("canvas") as HTMLCanvasElement;
	if (canvasElement) {
		canvasElement.hidden = true;
		const canvas = canvasElement.getContext("2d");
		if (canvas)
			canvas.clearRect(0, 0, canvasElement.width, canvasElement.height);
	}
	if (videoTrack) {
		videoTrack.stop();
		videoTrack = null;
	}
	if (videoElement) {
		videoElement.remove();
		videoElement = null;
	}
	const outputContainer = document.getElementById("output");
	if (outputContainer) outputContainer.hidden = true;
	const loadingMessage = document.getElementById("loadingMessage");
	if (loadingMessage) loadingMessage.hidden = false;
	notify("QR Code Scanner", "Stopped scanning for QR codes...", "info");
}

export async function scanQRCode(): Promise<string | null> {
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
		const loadingMessage = document.getElementById("loadingMessage");
		const outputContainer = document.getElementById("output");
		const outputMessage = document.getElementById("outputMessage");
		const outputData = document.getElementById("outputData");
		const toggleButton = document.getElementById("toggleFlashlight");
		if (!toggleButton)
			return notify("QR Code Scanner", "Could not find flash button", "error");
		toggleButton.onclick = () => {
			toggleFlashlight(!flashlightOn);
		};
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
		navigator.mediaDevices
			.getUserMedia({ video: { facingMode: "environment" } })
			.then((stream) => {
				if (!videoElement)
					return notify(
						"QR Code Scanner",
						"Could not find videoElement",
						"error",
					);
				videoElement.srcObject = stream;
				videoElement.playsInline = true;
				videoElement.play();
				videoTrack = stream.getVideoTracks()[0];
				const capabilities =
					videoTrack.getCapabilities() as MediaTrackCapabilities & {
						torch: boolean;
					};
				if (capabilities.torch) {
					// const toggleButton = document.getElementById("toggleFlashlight");
					// if (!toggleButton)
					// 	return console.error("Could not find flash button");
					// toggleButton.classList.remove("hidden");
					// toggleButton.style.display = "block";
					notify(
						"QR Code Scanner",
						"Your device can use the flash light",
						"info",
					);
				} else {
					notify(
						"QR Code Scanner",
						"The flash light capability is not supported on this device",
						"error",
					);
				}
				requestAnimationFrame(qrScanner);
			});
		function qrScanner() {
			if (!videoTrack)
				return notify("QR Code Scanner", "Could not find videoTrack", "error");
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
				const imageData = canvas.getImageData(
					0,
					0,
					canvasElement.width,
					canvasElement.height,
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
					const capabilities =
						videoTrack.getCapabilities() as MediaTrackCapabilities & {
							torch: boolean;
						};
					if (capabilities.torch) toggleFlashlight(false);
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

function toggleFlashlight(on: boolean) {
	if (!videoTrack) {
		notify("QR Code Scanner", "No video track available.", "error");
		return;
	}
	flashlightOn = on;
	try {
		videoTrack.applyConstraints({
			// @ts-ignore
			advanced: [{ torch: flashlightOn }],
		});
		notify(
			"QR Code Scanner",
			`Flashlight turned ${flashlightOn ? "on" : "off"}.`,
			"info",
		);
	} catch (error) {
		notify("QR Code Scanner", `Error toggling flashlight: ${error}`, "error");
	}
}
