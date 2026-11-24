export const API_BASE_URL = (process.env.API_BASE_URL || '/api').replace(/\/+$/, '');

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
	const response = await fetch(`${API_BASE_URL}/${path.replace(/^\/+/, '')}`, init);
	const data = await response.json().catch(() => ({}));
	if (!response.ok || data.status === 'error') {
		throw new Error(data.message || data.error || `请求失败（${response.status}）`);
	}
	return data as T;
}

export function post<T>(path: string, data: unknown): Promise<T> {
	return api<T>(path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
}

export function errorMessage(error: unknown): string {
	return error instanceof Error ? error.message : '请求失败，请稍后重试';
}
