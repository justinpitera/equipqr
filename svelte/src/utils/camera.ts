import jsQR from "jsqr";
import type { Point } from "jsqr/dist/locator";
let videoTrack: MediaStreamTrack | null = null;
let videoElement: HTMLVideoElement | null = null;
let currentStream: MediaStream | null = null;
let flashlightOn = false;

export function toggleScanner(enabled: boolean) {
	if (!videoTrack) return console.error("Could not find videoTrack");
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
	console.log("Scanner destroyed and cleaned up.");
}

export async function scanQRCode(): Promise<string | null> {
	return new Promise((resolve) => {
		if (!navigator.mediaDevices || (navigator.mediaDevices && !navigator.mediaDevices.getUserMedia)) {
			alert('Could not find an available camera to use for scanning QR codes...');
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
		if (!toggleButton) return console.error("Could not find flash button");
		toggleButton.onclick = () => {
			toggleFlashlight(!flashlightOn);
		};
		function drawLine(
			begin: Point,
			end: Point,
			color: string | CanvasGradient | CanvasPattern,
		) {
			if (!canvas) return console.error("Could not find canvas");
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
				if (!videoElement) return console.error("Could not find videoElement");
				videoElement.srcObject = stream;
				currentStream = stream;
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
					console.log("You have a torch!")
				} else {
					console.warn("Torch capability is not supported on this device.");
				}
				requestAnimationFrame(qrScanner);
			});
		function qrScanner() {
			if (!videoTrack) return console.error("Could not find videoTrack");
			if (!videoTrack.enabled) return;
			if (!videoElement) return console.error("Could not find videoElement");
			if (!loadingMessage)
				return console.error("Could not find loadingMessage");
			if (!outputContainer)
				return console.error("Could not find outputContainer");
			if (!canvas) return console.error("Could not find canvas");
			if (!outputMessage) return console.error("Could not find outputMessage");
			if (!outputData) return console.error("Could not find outputData");
			if (!outputData.parentElement)
				return console.error("Could not find outputData parent");
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
		console.error("No video track available.");
		return;
	}
	flashlightOn = on;
	try {
		videoTrack.applyConstraints({
			// @ts-ignore
			advanced: [{ torch: flashlightOn }],
		});
		console.log(`Flashlight turned ${flashlightOn ? "on" : "off"}.`);
	} catch (error) {
		console.error("Error toggling flashlight:", error);
	}
}
