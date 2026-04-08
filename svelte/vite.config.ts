import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig, loadEnv } from "vite";
import fs from "node:fs";

export default defineConfig(({ mode }) => {
	const env = loadEnv(mode, process.cwd(), "");

	const host = env.HOST ?? "0.0.0.0";
	const port = parseInt(env.PORT ?? "5173", 10);
	const proxyTarget = env.PROXY_TARGET ?? "https://127.0.0.1:7879";

	// HTTPS is optional — only used for dev server when cert files are explicitly provided
	const https =
		env.SSL_CERT_FILE && env.SSL_KEY_FILE
			? {
					cert: fs.readFileSync(env.SSL_CERT_FILE),
					key: fs.readFileSync(env.SSL_KEY_FILE),
				}
			: undefined;

	return {
		plugins: [sveltekit()],
		css: {
			postcss: "./postcss.config.js",
		},
		server: {
			host,
			port,
			https,
			hmr: { protocol: https ? "wss" : "ws" },
			proxy: {
				"/api": {
					target: proxyTarget,
					secure: false,
					rewrite: (path) => path.replace(/^\/api/, ""),
				},
			},
		},
	};
});
