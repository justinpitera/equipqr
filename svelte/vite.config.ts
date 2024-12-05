import { sveltekit } from "@sveltejs/kit/vite";
import type { ResolvedConfig, Plugin } from "vite";
import fs from "node:fs";
import path from "node:path";
import colors from "colors";
import toml from "toml";
import forge from "node-forge";
import type { IncomingMessage } from "node:http";
import type { ClientRequest } from "node:http";
import { VitePWA } from "vite-plugin-pwa";

// Load configuration file
const configPath: string = path.resolve(
	__dirname,
	"../private/configurations/vite.config.toml",
);
const config = toml.parse(fs.readFileSync(configPath, "utf-8"));

// Check required fields
if (
	!config.server?.cert_folder ||
	!config.server?.host ||
	!config.server?.port
) {
	throw new Error("Missing essential server configuration fields in vite.toml");
}

// Resolve paths
const resolvePath = (file: string): string =>
	path.resolve(config.server.cert_folder, file);

// Utility to determine whether a file is a certificate or a private key
const detectCertOrKey = (filePath: string): "cert" | "key" | "unknown" => {
	const fileContent = fs.readFileSync(filePath, "utf-8");

	if (fileContent.includes("-----BEGIN CERTIFICATE-----")) {
		return "cert";
	}

	if (fileContent.includes("-----BEGIN PRIVATE KEY-----")) {
		return "key";
	}

	return "unknown";
};

// Utility to validate certificate and key
const validateCertAndKey = (certPath: string, keyPath: string): void => {
	const certData = fs.readFileSync(certPath, "utf-8");
	const keyData = fs.readFileSync(keyPath, "utf-8");

	try {
		const cert = forge.pki.certificateFromPem(certData);
		const now = new Date();
		if (cert.validity.notBefore > now || cert.validity.notAfter < now) {
			throw new Error("Certificate has expired or is not yet valid.");
		}
	} catch (err: unknown) {
		if (err instanceof Error) {
			throw new Error(`Invalid certificate: ${err.message}`);
		}
	}

	try {
		const privateKey = forge.pki.privateKeyFromPem(keyData);
		if (!privateKey) {
			throw new Error("Invalid private key.");
		}
	} catch (err: unknown) {
		if (err instanceof Error) {
			throw new Error(`Invalid private key: ${err.message}`);
		}
	}
};

// Automatically detect cert and key
const files = fs
	.readdirSync(config.server.cert_folder)
	.filter((file) => file !== ".gitkeep");
if (files.length !== 2) {
	throw new Error(
		`There should be exactly two files in the certificate folder, but found ${files.length}.`,
	);
}

let certFile: string | undefined;
let keyFile: string | undefined;

for (const file of files) {
	const filePath = resolvePath(file);
	const fileType = detectCertOrKey(filePath);

	if (fileType === "cert") {
		certFile = file;
	} else if (fileType === "key") {
		keyFile = file;
	}
}

if (!certFile || !keyFile) {
	throw new Error(
		"Could not find both certificate and private key in the folder.",
	);
}

// Validate the certificate and key
const certPath = resolvePath(certFile);
const keyPath = resolvePath(keyFile);
validateCertAndKey(certPath, keyPath);

// Custom logging
const logEvent = (level: "info" | "warn" | "error", message: string): void => {
	const timestamp = new Date().toISOString();
	let coloredMessage: string = message;

	switch (level) {
		case "info":
			coloredMessage = colors.green(message);
			break;
		case "warn":
			coloredMessage = colors.yellow(message);
			break;
		case "error":
			coloredMessage = colors.red(message);
			break;
	}

	if (level === config.logging.level || level === "error") {
		console.log(`[${timestamp}] [${level.toUpperCase()}] ${coloredMessage}`);
	}
};

// Plugin for detailed startup output
const startupDetailPlugin = (): Plugin => {
	let resolvedConfig: ResolvedConfig;

	return {
		name: "vite-startup-detail",
		configResolved(config) {
			resolvedConfig = config;
			logEvent("info", "Detailed Vite server configuration:");
			logEvent("info", `Vite Version: ${config.root}`);
			logEvent("info", `Root directory: ${config.root}`);
			logEvent("info", `Base URL: ${config.base}`);
		},
		buildStart() {
			logEvent("info", "Starting Vite server with detailed configuration...");
			logEvent("info", `Network: ${config.server.host}:${config.server.port}`);
			logEvent("info", `Environment: ${config.mode}`);
			logEvent("info", "Loaded plugins:");
			for (const plugin of resolvedConfig.plugins as Plugin[]) {
				logEvent("info", ` - ${plugin.name}`);
			}
		},
	};
};

// Vite configuration
const useHttps = config.server.use_https;
const wsProtocol = useHttps ? "wss" : "ws";

const viteConfig = {
	plugins: [
		sveltekit(),
		startupDetailPlugin(),
		VitePWA({
			registerType: "autoUpdate",
			manifest: {
				name: "My SvelteKit App",
				short_name: "SvelteApp",
				description: "A SvelteKit PWA Application",
				theme_color: "#ffffff",
				background_color: "#ffffff",
				display: "standalone",
				icons: [
					{
						src: "/icon-192x192.png",
						sizes: "192x192",
						type: "image/png",
					},
					{
						src: "/icon-512x512.png",
						sizes: "512x512",
						type: "image/png",
					},
				],
			},
			workbox: {
				globPatterns: ["**/*.{js,css,html,svg,png}"],
			},
		}),
	],
	css: {
		postcss: "./postcss.config.js",
	},
	// ssr: {
	//  noExternal: ['']
	// },
	server: {
		host: config.server.host,
		port: config.server.port,
		https: useHttps
			? { cert: fs.readFileSync(certPath), key: fs.readFileSync(keyPath) }
			: undefined,
		hmr: {
			protocol: wsProtocol,
			onConnection: () => logEvent("info", "HMR connection established"),
		},
		proxy: {
			"/api": {
				secure: false,
				target: config.proxy.target,
				rewrite: (path: string) => {
					logEvent("info", `Proxying API request: ${path}`);
					return path.replace(/^\/api/, "");
				},
				onProxyReq: (proxyReq: ClientRequest, req: IncomingMessage) => {
					logEvent(
						"info",
						`Proxy request method: ${proxyReq.method}, path: ${proxyReq.path}`,
					);
					logEvent("info", `Incoming request: ${req.method} ${req.url}`);
				},
				onError: (err: Error, req: IncomingMessage) => {
					logEvent("error", `Proxy error on ${req.url}: ${err.message}`);
				},
			},
		},
	},
	build: {
		onEnd() {
			logEvent("info", "Vite build completed");
		},
	},
};

export default viteConfig;
