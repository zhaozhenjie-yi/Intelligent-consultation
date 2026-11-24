/* eslint-disable */

declare namespace NodeJS {
	interface ProcessEnv {
		NODE_ENV: string;
		API_BASE_URL: string;
		PATIENT_MANAGEMENT_PASSWORD: string;
		VUE_ROUTER_MODE: 'hash' | 'history' | 'abstract' | undefined;
		VUE_ROUTER_BASE: string | undefined;
	}
}
